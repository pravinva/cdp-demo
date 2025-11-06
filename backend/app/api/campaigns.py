"""
Campaign API endpoints
Campaign management and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.campaign import Campaign, CampaignCreate
from ..dependencies import get_tenant_context, get_workspace_client
from ..config import get_settings
import uuid
from datetime import datetime
import json

router = APIRouter()


@router.post("/", response_model=Campaign, status_code=201)
async def create_campaign(
    campaign: CampaignCreate,
    tenant_id: str = Depends(get_tenant_context),
    created_by: str = "system",  # TODO: Get from auth context
    w = Depends(get_workspace_client)
):
    """Create a new campaign"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
    
    # Escape single quotes in strings
    name = campaign.name.replace("'", "''")
    description = campaign.description.replace("'", "''") if campaign.description else None
    agent_instructions = campaign.agent_instructions.replace("'", "''") if campaign.agent_instructions else None
    
    # Format channels as JSON array string
    channels_json = json.dumps(campaign.channels)
    
    insert_query = f"""
        INSERT INTO cdp_platform.core.campaigns
        (campaign_id, tenant_id, name, description, goal, status,
         target_segment, agent_mode, agent_instructions, channels,
         start_date, end_date, created_by, created_at, updated_at)
        VALUES (
            '{campaign_id}',
            '{tenant_id}',
            '{name}',
            {'NULL' if not description else "'" + description + "'"},
            '{campaign.goal}',
            'draft',
            {'NULL' if not campaign.target_segment else "'" + campaign.target_segment + "'"},
            {str(campaign.agent_mode).lower()},
            {'NULL' if not agent_instructions else "'" + agent_instructions + "'"},
            '{channels_json}',
            {'NULL' if not campaign.start_date else f"timestamp('{campaign.start_date.isoformat()}')"},
            {'NULL' if not campaign.end_date else f"timestamp('{campaign.end_date.isoformat()}')"},
            '{created_by}',
            current_timestamp(),
            current_timestamp()
        )
    """
    
    try:
        w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=insert_query,
            wait_timeout="30s"
        )
    except Exception as e:
        print(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")
    
    # Return created campaign - call get_campaign logic directly
    query = f"""
        SELECT *
        FROM cdp_platform.core.campaigns
        WHERE tenant_id = '{tenant_id}' AND campaign_id = '{campaign_id}'
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if not response.result or not response.result.data_array:
            raise HTTPException(status_code=500, detail="Failed to retrieve created campaign")
        
        columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
        row = response.result.data_array[0]
        row_dict = {columns[i]: row[i] for i in range(len(columns))}
        
        # Handle datetime conversion
        for date_col in ['start_date', 'end_date', 'created_at', 'updated_at']:
            if date_col in row_dict and row_dict[date_col]:
                if isinstance(row_dict[date_col], str):
                    try:
                        row_dict[date_col] = datetime.fromisoformat(row_dict[date_col].replace('Z', '+00:00'))
                    except:
                        pass
        
        # Handle array conversion for channels
        if 'channels' in row_dict and isinstance(row_dict['channels'], str):
            try:
                row_dict['channels'] = json.loads(row_dict['channels'])
            except:
                row_dict['channels'] = []
        
        return Campaign(**row_dict)
    except Exception as e:
        print(f"Error retrieving created campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve created campaign: {str(e)}")


@router.get("/", response_model=List[Campaign])
async def list_campaigns(
    tenant_id: str = Depends(get_tenant_context),
    status: Optional[str] = Query(None),
    w = Depends(get_workspace_client)
):
    """List all campaigns"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    where_clause = f"tenant_id = '{tenant_id}'"
    if status:
        where_clause += f" AND status = '{status}'"
    
    query = f"""
        SELECT *
        FROM cdp_platform.core.campaigns
        WHERE {where_clause}
        ORDER BY created_at DESC
    """
    
    campaigns = []
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if response.result and response.result.data_array:
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            for row in response.result.data_array:
                try:
                    row_dict = {columns[i]: row[i] for i in range(len(columns))}
                    
                    # Handle datetime conversion
                    for date_col in ['start_date', 'end_date', 'created_at', 'updated_at']:
                        if date_col in row_dict and row_dict[date_col]:
                            if isinstance(row_dict[date_col], str):
                                try:
                                    row_dict[date_col] = datetime.fromisoformat(row_dict[date_col].replace('Z', '+00:00'))
                                except:
                                    pass
                    
                    # Handle array conversion for channels
                    if 'channels' in row_dict and isinstance(row_dict['channels'], str):
                        try:
                            row_dict['channels'] = json.loads(row_dict['channels'])
                        except:
                            row_dict['channels'] = []
                    
                    campaigns.append(Campaign(**row_dict))
                except Exception as e:
                    print(f"Error parsing campaign: {e}")
                    continue
    except Exception as e:
        print(f"Error listing campaigns: {e}")
    
    return campaigns


@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
):
    """Get a specific campaign"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    query = f"""
        SELECT *
        FROM cdp_platform.core.campaigns
        WHERE tenant_id = '{tenant_id}' AND campaign_id = '{campaign_id}'
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if not response.result or not response.result.data_array:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
        row = response.result.data_array[0]
        row_dict = {columns[i]: row[i] for i in range(len(columns))}
        
        # Handle datetime conversion
        for date_col in ['start_date', 'end_date', 'created_at', 'updated_at']:
            if date_col in row_dict and row_dict[date_col]:
                if isinstance(row_dict[date_col], str):
                    try:
                        row_dict[date_col] = datetime.fromisoformat(row_dict[date_col].replace('Z', '+00:00'))
                    except:
                        pass
        
        # Handle array conversion for channels
        if 'channels' in row_dict and isinstance(row_dict['channels'], str):
            try:
                row_dict['channels'] = json.loads(row_dict['channels'])
            except:
                row_dict['channels'] = []
        
        return Campaign(**row_dict)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
):
    """Activate a campaign"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    update_query = f"""
        UPDATE cdp_platform.core.campaigns
        SET status = 'active',
            updated_at = current_timestamp()
        WHERE tenant_id = '{tenant_id}' AND campaign_id = '{campaign_id}'
    """
    
    try:
        w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=update_query,
            wait_timeout="30s"
        )
    except Exception as e:
        print(f"Error activating campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to activate campaign: {str(e)}")
    
    return {"status": "activated", "campaign_id": campaign_id}


@router.post("/{campaign_id}/execute")
async def execute_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
):
    """
    Execute a campaign - triggers agent decisions for target audience
    This would typically be called by a background job
    """
    from ..services.agent_service import AgentService
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    # Get campaign
    campaign = await get_campaign(campaign_id, tenant_id, w)
    
    if campaign.status != 'active':
        raise HTTPException(status_code=400, detail="Campaign is not active")
    
    # Get target customers
    where_clause = f"tenant_id = '{tenant_id}'"
    if campaign.target_segment:
        where_clause += f" AND segment = '{campaign.target_segment}'"
    
    customers_query = f"""
        SELECT customer_id
        FROM cdp_platform.core.customers
        WHERE {where_clause}
    """
    
    customer_ids = []
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=customers_query,
            wait_timeout="30s"
        )
        if response.result and response.result.data_array:
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            for row in response.result.data_array:
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                customer_ids.append(row_dict.get('customer_id'))
    except Exception as e:
        print(f"Error getting customers: {e}")
    
    # Execute agent decisions
    agent_service = AgentService(tenant_id)
    decisions = []
    
    for customer_id in customer_ids[:100]:  # Limit to 100 for demo
        decision = agent_service.analyze_and_decide(
            customer_id=customer_id,
            campaign_id=campaign_id,
            agent_instructions=campaign.agent_instructions,
            channels=campaign.channels
        )
        decisions.append(decision.decision_id)
    
    return {
        "status": "success",
        "campaign_id": campaign_id,
        "customers_processed": len(decisions),
        "decisions": decisions
    }


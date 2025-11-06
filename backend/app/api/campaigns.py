"""
Campaign API endpoints
Campaign management and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.campaign import Campaign, CampaignCreate
from ..dependencies import get_tenant_context, get_spark_session
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=Campaign, status_code=201)
async def create_campaign(
    campaign: CampaignCreate,
    tenant_id: str = Depends(get_tenant_context),
    created_by: str = "system",  # TODO: Get from auth context
    spark = Depends(get_spark_session)
):
    """Create a new campaign"""
    
    campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
    
    channels_str = "[" + ",".join([f"'{ch}'" for ch in campaign.channels]) + "]"
    
    insert_query = f"""
        INSERT INTO cdp_platform.core.campaigns
        (campaign_id, tenant_id, name, description, goal, status,
         target_segment, agent_mode, agent_instructions, channels,
         start_date, end_date, created_by, created_at, updated_at)
        VALUES (
            '{campaign_id}',
            '{tenant_id}',
            '{campaign.name}',
            {'NULL' if not campaign.description else "'" + campaign.description.replace("'", "\\'") + "'"},
            '{campaign.goal}',
            'draft',
            {'NULL' if not campaign.target_segment else "'" + campaign.target_segment + "'"},
            {campaign.agent_mode},
            {'NULL' if not campaign.agent_instructions else "'" + campaign.agent_instructions.replace("'", "\\'") + "'"},
            {channels_str},
            {'NULL' if not campaign.start_date else f"timestamp('{campaign.start_date.isoformat()}')"},
            {'NULL' if not campaign.end_date else f"timestamp('{campaign.end_date.isoformat()}')"},
            '{created_by}',
            current_timestamp(),
            current_timestamp()
        )
    """
    
    spark.sql(insert_query)
    
    # Return created campaign
    return await get_campaign(campaign_id, tenant_id, spark)


@router.get("/", response_model=List[Campaign])
async def list_campaigns(
    tenant_id: str = Depends(get_tenant_context),
    status: Optional[str] = Query(None),
    spark = Depends(get_spark_session)
):
    """List all campaigns"""
    
    where_clause = f"tenant_id = '{tenant_id}'"
    if status:
        where_clause += f" AND status = '{status}'"
    
    query = f"""
        SELECT *
        FROM cdp_platform.core.campaigns
        WHERE {where_clause}
        ORDER BY created_at DESC
    """
    
    results = spark.sql(query).toPandas().to_dict('records')
    
    campaigns = []
    for row in results:
        try:
            row_dict = {k: float(v) if hasattr(v, '__float__') else v for k, v in row.items()}
            campaigns.append(Campaign(**row_dict))
        except Exception as e:
            print(f"Error parsing campaign: {e}")
            continue
    
    return campaigns


@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Get a specific campaign"""
    
    query = f"""
        SELECT *
        FROM cdp_platform.core.campaigns
        WHERE tenant_id = '{tenant_id}' AND campaign_id = '{campaign_id}'
    """
    
    result = spark.sql(query).toPandas().to_dict('records')
    
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    row_dict = {k: float(v) if hasattr(v, '__float__') else v for k, v in result[0].items()}
    return Campaign(**row_dict)


@router.post("/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Activate a campaign"""
    
    update_query = f"""
        UPDATE cdp_platform.core.campaigns
        SET status = 'active',
            updated_at = current_timestamp()
        WHERE tenant_id = '{tenant_id}' AND campaign_id = '{campaign_id}'
    """
    
    spark.sql(update_query)
    
    return {"status": "activated", "campaign_id": campaign_id}


@router.post("/{campaign_id}/execute")
async def execute_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """
    Execute a campaign - triggers agent decisions for target audience
    This would typically be called by a background job
    """
    from ..services.agent_service import AgentService
    
    # Get campaign
    campaign = await get_campaign(campaign_id, tenant_id, spark)
    
    if campaign.status != 'active':
        raise HTTPException(status_code=400, detail="Campaign is not active")
    
    # Get target customers
    spark = get_spark_session()
    where_clause = f"tenant_id = '{tenant_id}'"
    if campaign.target_segment:
        where_clause += f" AND segment = '{campaign.target_segment}'"
    
    customers_query = f"""
        SELECT customer_id
        FROM cdp_platform.core.customers
        WHERE {where_clause}
    """
    customers_df = spark.sql(customers_query)
    customer_ids = [row['customer_id'] for row in customers_df.collect()]
    
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


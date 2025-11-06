"""
Agent API endpoints
Agent decision execution and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from ..models.decision import AgentDecision, AgentDecisionCreate, ToolCall
from ..dependencies import get_tenant_context, get_workspace_client
from ..services.agent_service import AgentService
from ..config import get_settings
from datetime import datetime

router = APIRouter()


@router.post("/decide", response_model=AgentDecision)
async def make_agent_decision(
    request: AgentDecisionCreate,
    tenant_id: str = Depends(get_tenant_context)
):
    """Execute agent decision for a customer"""
    
    agent_service = AgentService(tenant_id)
    
    decision = agent_service.analyze_and_decide(
        customer_id=request.customer_id,
        campaign_id=request.campaign_id,
        journey_id=request.journey_id,
        journey_step_id=request.journey_step_id
    )
    
    return decision


@router.get("/decisions", response_model=List[AgentDecision])
async def list_agent_decisions(
    tenant_id: str = Depends(get_tenant_context),
    customer_id: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    journey_id: Optional[str] = Query(None),
    w = Depends(get_workspace_client)
):
    """List agent decisions with filtering"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    where_clauses = [f"tenant_id = '{tenant_id}'"]
    
    if customer_id:
        where_clauses.append(f"customer_id = '{customer_id}'")
    if campaign_id:
        where_clauses.append(f"campaign_id = '{campaign_id}'")
    if journey_id:
        where_clauses.append(f"journey_id = '{journey_id}'")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
        SELECT *
        FROM cdp_platform.core.agent_decisions
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT 100
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        decisions = []
        if response.result and response.result.data_array:
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            
            for row in response.result.data_array:
                try:
                    row_dict = {}
                    for i, col_name in enumerate(columns):
                        value = row[i] if i < len(row) else None
                        # Handle datetime conversion
                        if col_name in ['timestamp', 'scheduled_send_time']:
                            if value:
                                if isinstance(value, str):
                                    try:
                                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    except:
                                        value = None
                                elif not isinstance(value, datetime):
                                    value = None
                        row_dict[col_name] = value
                    
                    # Handle tool_calls if present
                    if 'tool_calls' in row_dict and row_dict['tool_calls']:
                        tool_calls_list = row_dict['tool_calls']
                        if isinstance(tool_calls_list, list):
                            row_dict['tool_calls'] = [
                                ToolCall(**tc) if isinstance(tc, dict) else tc
                                for tc in tool_calls_list
                            ]
                        else:
                            row_dict['tool_calls'] = []
                    else:
                        row_dict['tool_calls'] = []
                    
                    decisions.append(AgentDecision(**row_dict))
                except Exception as e:
                    print(f"Error parsing decision: {e}")
                    continue
    except Exception as e:
        print(f"Error fetching decisions: {e}")
        decisions = []
    
    return decisions


@router.get("/decisions/{decision_id}", response_model=AgentDecision)
async def get_agent_decision(
    decision_id: str,
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
):
    """Get a specific agent decision"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    query = f"""
        SELECT *
        FROM cdp_platform.core.agent_decisions
        WHERE tenant_id = '{tenant_id}' AND decision_id = '{decision_id}'
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if not response.result or not response.result.data_array:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
        row = response.result.data_array[0]
        
        row_dict = {}
        for i, col_name in enumerate(columns):
            value = row[i] if i < len(row) else None
            # Handle datetime conversion
            if col_name in ['timestamp', 'scheduled_send_time']:
                if value:
                    if isinstance(value, str):
                        try:
                            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            value = None
                    elif not isinstance(value, datetime):
                        value = None
            row_dict[col_name] = value
        
        # Handle tool_calls
        if 'tool_calls' in row_dict and row_dict['tool_calls']:
            tool_calls_list = row_dict['tool_calls']
            if isinstance(tool_calls_list, list):
                row_dict['tool_calls'] = [
                    ToolCall(**tc) if isinstance(tc, dict) else tc
                    for tc in tool_calls_list
                ]
            else:
                row_dict['tool_calls'] = []
        else:
            row_dict['tool_calls'] = []
        
        return AgentDecision(**row_dict)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching decision: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch decision: {str(e)}")


@router.get("/metrics")
async def get_agent_metrics(
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
) -> Dict[str, Any]:
    """Get agent performance metrics"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    query = f"""
        SELECT 
            COUNT(*) as total_decisions,
            SUM(CASE WHEN action = 'contact' THEN 1 ELSE 0 END) as contact_decisions,
            SUM(CASE WHEN action = 'skip' THEN 1 ELSE 0 END) as skip_decisions,
            AVG(confidence_score) as avg_confidence_score,
            AVG(execution_time_ms) as avg_execution_time_ms,
            SUM(CASE WHEN converted = true THEN 1 ELSE 0 END) as conversions,
            SUM(CASE WHEN opened = true THEN 1 ELSE 0 END) as opened,
            SUM(CASE WHEN clicked = true THEN 1 ELSE 0 END) as clicked
        FROM cdp_platform.core.agent_decisions
        WHERE tenant_id = '{tenant_id}'
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if not response.result or not response.result.data_array:
            return {
                "total_decisions": 0,
                "contact_decisions": 0,
                "skip_decisions": 0,
                "avg_confidence_score": 0,
                "avg_execution_time_ms": 0,
                "conversion_rate": 0,
                "open_rate": 0,
                "click_rate": 0,
                "decisions_by_channel": {},
                "decisions_by_segment": {},
                "top_reasons": [],
            }
        
        columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
        row = response.result.data_array[0]
        metrics_dict = {columns[i]: row[i] for i in range(len(columns))}
        
        total = int(metrics_dict.get('total_decisions', 0) or 0)
        contact = int(metrics_dict.get('contact_decisions', 0) or 0)
        conversions = int(metrics_dict.get('conversions', 0) or 0)
        opened = int(metrics_dict.get('opened', 0) or 0)
        clicked = int(metrics_dict.get('clicked', 0) or 0)
        
        # Get channel distribution
        channel_query = f"""
            SELECT channel, COUNT(*) as count
            FROM cdp_platform.core.agent_decisions
            WHERE tenant_id = '{tenant_id}' AND channel IS NOT NULL
            GROUP BY channel
        """
        
        channel_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=channel_query,
            wait_timeout="30s"
        )
        
        decisions_by_channel = {}
        if channel_response.result and channel_response.result.data_array:
            channel_columns = [col.name for col in channel_response.manifest.schema.columns] if channel_response.manifest and channel_response.manifest.schema else []
            for row in channel_response.result.data_array:
                row_dict = {channel_columns[i]: row[i] for i in range(len(channel_columns))}
                decisions_by_channel[row_dict.get('channel', 'unknown')] = int(row_dict.get('count', 0))
        
        # Get segment distribution
        segment_query = f"""
            SELECT customer_segment, COUNT(*) as count
            FROM cdp_platform.core.agent_decisions
            WHERE tenant_id = '{tenant_id}' AND customer_segment IS NOT NULL
            GROUP BY customer_segment
        """
        
        segment_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=segment_query,
            wait_timeout="30s"
        )
        
        decisions_by_segment = {}
        if segment_response.result and segment_response.result.data_array:
            segment_columns = [col.name for col in segment_response.manifest.schema.columns] if segment_response.manifest and segment_response.manifest.schema else []
            for row in segment_response.result.data_array:
                row_dict = {segment_columns[i]: row[i] for i in range(len(segment_columns))}
                decisions_by_segment[row_dict.get('customer_segment', 'unknown')] = int(row_dict.get('count', 0))
        
        return {
            "total_decisions": total,
            "contact_decisions": contact,
            "skip_decisions": int(metrics_dict.get('skip_decisions', 0) or 0),
            "avg_confidence_score": float(metrics_dict.get('avg_confidence_score', 0) or 0),
            "avg_execution_time_ms": float(metrics_dict.get('avg_execution_time_ms', 0) or 0),
            "conversion_rate": (conversions / contact * 100) if contact > 0 else 0,
            "open_rate": (opened / contact * 100) if contact > 0 else 0,
            "click_rate": (clicked / opened * 100) if opened > 0 else 0,
            "decisions_by_channel": decisions_by_channel,
            "decisions_by_segment": decisions_by_segment,
            "top_reasons": [],  # Could be enhanced with reasoning_summary analysis
        }
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


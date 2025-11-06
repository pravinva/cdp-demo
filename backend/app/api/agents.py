"""
Agent API endpoints
Agent decision execution and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.decision import AgentDecision, AgentDecisionCreate
from ..dependencies import get_tenant_context, get_spark_session
from ..services.agent_service import AgentService

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
    spark = Depends(get_spark_session)
):
    """List agent decisions with filtering"""
    
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
    
    results = spark.sql(query).toPandas().to_dict('records')
    
    decisions = []
    for row in results:
        try:
            row_dict = {k: float(v) if hasattr(v, '__float__') else v for k, v in row.items()}
            # Convert tool_calls array if present
            if 'tool_calls' in row_dict and row_dict['tool_calls']:
                from ..models.decision import ToolCall
                tool_calls = [
                    ToolCall(**tc) if isinstance(tc, dict) else tc
                    for tc in row_dict['tool_calls']
                ]
                row_dict['tool_calls'] = tool_calls
            decisions.append(AgentDecision(**row_dict))
        except Exception as e:
            print(f"Error parsing decision: {e}")
            continue
    
    return decisions


@router.get("/decisions/{decision_id}", response_model=AgentDecision)
async def get_agent_decision(
    decision_id: str,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Get a specific agent decision"""
    
    query = f"""
        SELECT *
        FROM cdp_platform.core.agent_decisions
        WHERE tenant_id = '{tenant_id}' AND decision_id = '{decision_id}'
    """
    
    result = spark.sql(query).toPandas().to_dict('records')
    
    if not result:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    row_dict = {k: float(v) if hasattr(v, '__float__') else v for k, v in result[0].items()}
    return AgentDecision(**row_dict)


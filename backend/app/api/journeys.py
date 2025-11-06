"""
Journey API endpoints
CRUD operations for journey definitions and execution
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.journey import (
    JourneyDefinition,
    JourneyDefinitionCreate,
    JourneyDefinitionUpdate,
    JourneyExecutionRequest,
    JourneyProgressResponse,
    CustomerJourneyState
)
from ..dependencies import get_tenant_context, get_spark_session
from ..services.journey_orchestrator_service import JourneyOrchestratorService
import uuid

router = APIRouter()


@router.post("/", response_model=JourneyDefinition, status_code=201)
async def create_journey(
    journey_def: JourneyDefinitionCreate,
    tenant_id: str = Depends(get_tenant_context),
    created_by: str = "system"  # TODO: Get from auth context
):
    """Create a new journey definition"""
    orchestrator = JourneyOrchestratorService(tenant_id)
    journey = orchestrator.create_journey(journey_def, created_by)
    return journey


@router.get("/", response_model=List[JourneyDefinition])
async def list_journeys(
    tenant_id: str = Depends(get_tenant_context),
    status: Optional[str] = Query(None),
    spark = Depends(get_spark_session)
):
    """List all journeys for tenant"""
    where_clause = f"tenant_id = '{tenant_id}'"
    if status:
        where_clause += f" AND status = '{status}'"
    
    result = spark.sql(f"""
        SELECT definition_json
        FROM cdp_platform.core.journey_definitions
        WHERE {where_clause}
        ORDER BY created_at DESC
    """).collect()
    
    journeys = []
    for row in result:
        try:
            journey = JourneyDefinition.model_validate_json(row['definition_json'])
            journeys.append(journey)
        except Exception as e:
            print(f"Error parsing journey: {e}")
            continue
    
    return journeys


@router.get("/{journey_id}", response_model=JourneyDefinition)
async def get_journey(
    journey_id: str,
    tenant_id: str = Depends(get_tenant_context)
):
    """Get a specific journey definition"""
    orchestrator = JourneyOrchestratorService(tenant_id)
    journey = orchestrator.get_journey(journey_id)
    
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    return journey


@router.patch("/{journey_id}", response_model=JourneyDefinition)
async def update_journey(
    journey_id: str,
    updates: JourneyDefinitionUpdate,
    tenant_id: str = Depends(get_tenant_context)
):
    """Update a journey definition"""
    orchestrator = JourneyOrchestratorService(tenant_id)
    
    update_dict = updates.model_dump(exclude_unset=True)
    journey = orchestrator.update_journey(journey_id, update_dict)
    
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    return journey


@router.post("/{journey_id}/activate")
async def activate_journey(
    journey_id: str,
    tenant_id: str = Depends(get_tenant_context)
):
    """Activate a journey (change status to active)"""
    orchestrator = JourneyOrchestratorService(tenant_id)
    success = orchestrator.activate_journey(journey_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    return {"status": "activated", "journey_id": journey_id}


@router.post("/{journey_id}/execute")
async def execute_journey(
    journey_id: str,
    request: JourneyExecutionRequest,
    tenant_id: str = Depends(get_tenant_context)
):
    """
    Enter customers into a journey
    """
    orchestrator = JourneyOrchestratorService(tenant_id)
    
    count = orchestrator.enter_customers_to_journey(
        journey_id=journey_id,
        customer_ids=request.customer_ids,
        segment=request.segment
    )
    
    return {
        "status": "success",
        "journey_id": journey_id,
        "customers_entered": count
    }


@router.get("/{journey_id}/progress", response_model=JourneyProgressResponse)
async def get_journey_progress(
    journey_id: str,
    tenant_id: str = Depends(get_tenant_context)
):
    """Get journey progress analytics"""
    orchestrator = JourneyOrchestratorService(tenant_id)
    progress = orchestrator.get_journey_progress(journey_id)
    
    return JourneyProgressResponse(
        journey_id=journey_id,
        journey_name="",  # TODO: Fetch from journey definition
        total_entered=progress.get('active', 0) + progress.get('waiting', 0) + progress.get('completed', 0),
        active_states=progress.get('active', 0),
        waiting_states=progress.get('waiting', 0),
        completed_states=progress.get('completed', 0),
        exited_states=progress.get('exited', 0),
        step_breakdown={}  # TODO: Implement step breakdown
    )


@router.get("/{journey_id}/states", response_model=List[CustomerJourneyState])
async def get_journey_states(
    journey_id: str,
    tenant_id: str = Depends(get_tenant_context),
    status: Optional[str] = Query(None),
    spark = Depends(get_spark_session)
):
    """Get all customer journey states for a journey"""
    where_clause = f"tenant_id = '{tenant_id}' AND journey_id = '{journey_id}'"
    if status:
        where_clause += f" AND status = '{status}'"
    
    result = spark.sql(f"""
        SELECT *
        FROM cdp_platform.core.customer_journey_states
        WHERE {where_clause}
        ORDER BY entered_at DESC
    """).collect()
    
    states = []
    for row in result:
        states.append(CustomerJourneyState(**row.asDict()))
    
    return states


@router.post("/orchestrator/process")
async def process_journey_states(
    tenant_id: str = Depends(get_tenant_context)
):
    """
    Manually trigger journey state processing
    Usually called by scheduled workflow
    """
    orchestrator = JourneyOrchestratorService(tenant_id)
    stats = orchestrator.process_journey_states()
    
    return {
        "status": "success",
        "stats": stats
    }


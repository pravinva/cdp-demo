"""
Identity Resolution API endpoints
Identity graph queries and match group management
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from ..dependencies import get_tenant_context, get_workspace_client
from ..services.graph_query_service import GraphQueryService
from ..services.identity_resolution_service import IdentityResolutionService
from ..config import get_settings
from datetime import datetime

router = APIRouter()


@router.post("/resolve")
async def run_identity_resolution(
    tenant_id: str = Depends(get_tenant_context),
    batch_size: int = Query(10000, ge=1, le=100000)
):
    """Run identity resolution on recent events"""
    service = IdentityResolutionService(tenant_id)
    result = service.run_identity_resolution(batch_size=batch_size)
    return {
        "status": "success",
        "processed": result["processed"],
        "match_groups_created": result["match_groups_created"]
    }


@router.post("/households/detect")
async def detect_households(
    tenant_id: str = Depends(get_tenant_context)
):
    """Detect households from customer data"""
    service = IdentityResolutionService(tenant_id)
    household_count = service.detect_households()
    return {
        "status": "success",
        "households_detected": household_count
    }


@router.get("/graph/household/{customer_id}")
async def get_household_graph(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_context)
):
    """Get household members for a customer"""
    
    graph_service = GraphQueryService(tenant_id)
    members = graph_service.get_household_members(customer_id)
    
    return {
        "customer_id": customer_id,
        "household_members": members
    }


@router.get("/match-groups")
async def list_match_groups(
    tenant_id: str = Depends(get_tenant_context),
    is_household: Optional[bool] = Query(None),
    w = Depends(get_workspace_client)
):
    """List identity match groups"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    where_clause = f"tenant_id = '{tenant_id}'"
    if is_household is not None:
        where_clause += f" AND is_household = {is_household}"
    
    query = f"""
        SELECT 
            match_id,
            total_events,
            anonymous_events,
            known_events,
            is_household,
            household_size,
            first_seen,
            last_seen
        FROM cdp_platform.core.match_groups
        WHERE {where_clause}
        ORDER BY last_seen DESC
        LIMIT 100
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        match_groups = []
        if response.result and response.result.data_array:
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            for row in response.result.data_array:
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                # Handle datetime conversion
                for date_col in ['first_seen', 'last_seen']:
                    if date_col in row_dict and row_dict[date_col]:
                        if isinstance(row_dict[date_col], str):
                            try:
                                row_dict[date_col] = datetime.fromisoformat(row_dict[date_col].replace('Z', '+00:00'))
                            except:
                                pass
                match_groups.append({
                    "match_id": row_dict.get('match_id'),
                    "total_events": int(row_dict.get('total_events', 0) or 0),
                    "anonymous_events": int(row_dict.get('anonymous_events', 0) or 0),
                    "known_events": int(row_dict.get('known_events', 0) or 0),
                    "is_household": bool(row_dict.get('is_household', False)),
                    "household_size": int(row_dict.get('household_size', 0) or 0) if row_dict.get('household_size') else None,
                    "first_seen": str(row_dict.get('first_seen', '')),
                    "last_seen": str(row_dict.get('last_seen', '')),
                })
    except Exception as e:
        print(f"Error fetching match groups: {e}")
        match_groups = []
    
    return {
        "match_groups": match_groups
    }


@router.get("/identity-graph/edges")
async def get_identity_graph_edges(
    tenant_id: str = Depends(get_tenant_context),
    relationship_type: Optional[str] = Query(None),
    w = Depends(get_workspace_client)
):
    """Get identity graph edges/relationships"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    where_clause = f"tenant_id = '{tenant_id}'"
    if relationship_type:
        where_clause += f" AND relationship_type = '{relationship_type}'"
    
    query = f"""
        SELECT 
            edge_id,
            from_entity_type,
            from_entity_id,
            to_entity_type,
            to_entity_id,
            relationship_type,
            strength,
            evidence_count
        FROM cdp_platform.core.identity_graph_edges
        WHERE {where_clause}
        ORDER BY strength DESC
        LIMIT 1000
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        edges = []
        if response.result and response.result.data_array:
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            for row in response.result.data_array:
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                edges.append({
                    "edge_id": row_dict.get('edge_id'),
                    "from": {
                        "type": row_dict.get('from_entity_type'),
                        "id": row_dict.get('from_entity_id')
                    },
                    "to": {
                        "type": row_dict.get('to_entity_type'),
                        "id": row_dict.get('to_entity_id')
                    },
                    "relationship_type": row_dict.get('relationship_type'),
                    "strength": float(row_dict.get('strength', 0) or 0),
                    "evidence_count": int(row_dict.get('evidence_count', 0) or 0)
                })
    except Exception as e:
        print(f"Error fetching graph edges: {e}")
        edges = []
    
    return {
        "edges": edges
    }


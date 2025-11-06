"""
Identity Resolution API endpoints
Identity graph queries and match group management
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from ..dependencies import get_tenant_context, get_spark_session
from ..services.graph_query_service import GraphQueryService

router = APIRouter()


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
    spark = Depends(get_spark_session)
):
    """List identity match groups"""
    
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
    
    results = spark.sql(query).collect()
    
    return {
        "match_groups": [
            {
                "match_id": row['match_id'],
                "total_events": row['total_events'],
                "anonymous_events": row['anonymous_events'],
                "known_events": row['known_events'],
                "is_household": row['is_household'],
                "household_size": row['household_size'],
                "first_seen": str(row['first_seen']),
                "last_seen": str(row['last_seen'])
            }
            for row in results
        ]
    }


@router.get("/identity-graph/edges")
async def get_identity_graph_edges(
    tenant_id: str = Depends(get_tenant_context),
    relationship_type: Optional[str] = Query(None),
    spark = Depends(get_spark_session)
):
    """Get identity graph edges/relationships"""
    
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
    
    results = spark.sql(query).collect()
    
    return {
        "edges": [
            {
                "edge_id": row['edge_id'],
                "from": {
                    "type": row['from_entity_type'],
                    "id": row['from_entity_id']
                },
                "to": {
                    "type": row['to_entity_type'],
                    "id": row['to_entity_id']
                },
                "relationship_type": row['relationship_type'],
                "strength": float(row['strength']) if row['strength'] else 0.0,
                "evidence_count": row['evidence_count']
            }
            for row in results
        ]
    }


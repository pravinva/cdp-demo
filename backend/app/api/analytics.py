"""
Analytics API endpoints
Dashboard data and analytics
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..dependencies import get_tenant_context, get_workspace_client
from ..config import get_settings

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_data(
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
):
    """Get dashboard summary data"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    # Total customers
    customers_count = 0
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=f"""
                SELECT COUNT(*) as total
                FROM cdp_platform.core.customers
                WHERE tenant_id = '{tenant_id}'
            """,
            wait_timeout="30s"
        )
        if response.result and response.result.data_array:
            customers_count = int(response.result.data_array[0][0] or 0)
    except Exception as e:
        print(f"Error getting customers count: {e}")
    
    # Active campaigns
    active_campaigns = 0
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=f"""
                SELECT COUNT(*) as total
                FROM cdp_platform.core.campaigns
                WHERE tenant_id = '{tenant_id}' AND status = 'active'
            """,
            wait_timeout="30s"
        )
        if response.result and response.result.data_array:
            active_campaigns = int(response.result.data_array[0][0] or 0)
    except Exception as e:
        print(f"Error getting active campaigns: {e}")
    
    # Total messages sent (last 30 days)
    messages_sent = 0
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=f"""
                SELECT COUNT(*) as total
                FROM cdp_platform.core.deliveries
                WHERE tenant_id = '{tenant_id}'
                AND sent_at >= current_timestamp() - INTERVAL 30 DAY
            """,
            wait_timeout="30s"
        )
        if response.result and response.result.data_array:
            messages_sent = int(response.result.data_array[0][0] or 0)
    except Exception as e:
        print(f"Error getting messages sent: {e}")
    
    # Conversion rate (last 30 days)
    conversion_rate = 0.0
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=f"""
                SELECT 
                    COUNT(*) as total_sent,
                    SUM(CASE WHEN converted = true THEN 1 ELSE 0 END) as total_converted
                FROM cdp_platform.core.deliveries
                WHERE tenant_id = '{tenant_id}'
                AND sent_at >= current_timestamp() - INTERVAL 30 DAY
            """,
            wait_timeout="30s"
        )
        if response.result and response.result.data_array:
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            row = response.result.data_array[0]
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            total_sent = int(row_dict.get('total_sent', 0) or 0)
            total_converted = int(row_dict.get('total_converted', 0) or 0)
            conversion_rate = total_converted / total_sent if total_sent > 0 else 0.0
    except Exception as e:
        print(f"Error getting conversion rate: {e}")
    
    # Active journeys
    active_journeys = 0
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=f"""
                SELECT COUNT(DISTINCT journey_id) as total
                FROM cdp_platform.core.customer_journey_states
                WHERE tenant_id = '{tenant_id}' AND status = 'active'
            """,
            wait_timeout="30s"
        )
        if response.result and response.result.data_array:
            active_journeys = int(response.result.data_array[0][0] or 0)
    except Exception as e:
        print(f"Error getting active journeys: {e}")
    
    return {
        "customers": {
            "total": customers_count
        },
        "campaigns": {
            "active": active_campaigns
        },
        "messages": {
            "sent_last_30d": messages_sent,
            "conversion_rate": conversion_rate
        },
        "journeys": {
            "active": active_journeys
        }
    }


@router.get("/customers/segments")
async def get_segment_distribution(
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
):
    """Get customer segment distribution"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    query = f"""
        SELECT 
            COALESCE(segment, 'Unknown') as segment,
            COUNT(*) as count
        FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}'
        GROUP BY segment
        ORDER BY count DESC
    """
    
    segments = []
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        if response.result and response.result.data_array:
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            for row in response.result.data_array:
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                segments.append({
                    "segment": row_dict.get('segment', 'Unknown'),
                    "count": int(row_dict.get('count', 0) or 0)
                })
    except Exception as e:
        print(f"Error getting segment distribution: {e}")
    
    return {"segments": segments}


@router.get("/campaigns/performance")
async def get_campaign_performance(
    tenant_id: str = Depends(get_tenant_context),
    days: int = Query(30, ge=1, le=365),
    w = Depends(get_workspace_client)
):
    """Get campaign performance metrics"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    query = f"""
        SELECT 
            c.campaign_id,
            c.name,
            c.goal,
            COUNT(DISTINCT d.delivery_id) as messages_sent,
            SUM(CASE WHEN d.opened = true THEN 1 ELSE 0 END) as messages_opened,
            SUM(CASE WHEN d.converted = true THEN 1 ELSE 0 END) as conversions
        FROM cdp_platform.core.campaigns c
        LEFT JOIN cdp_platform.core.deliveries d
            ON c.campaign_id = d.campaign_id
            AND c.tenant_id = d.tenant_id
            AND d.sent_at >= current_timestamp() - INTERVAL {days} DAY
        WHERE c.tenant_id = '{tenant_id}'
        GROUP BY c.campaign_id, c.name, c.goal
        ORDER BY messages_sent DESC
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
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                messages_sent = int(row_dict.get('messages_sent', 0) or 0)
                messages_opened = int(row_dict.get('messages_opened', 0) or 0)
                conversions = int(row_dict.get('conversions', 0) or 0)
                
                campaigns.append({
                    "campaign_id": row_dict.get('campaign_id'),
                    "name": row_dict.get('name'),
                    "goal": row_dict.get('goal'),
                    "messages_sent": messages_sent,
                    "messages_opened": messages_opened,
                    "conversions": conversions,
                    "open_rate": messages_opened / messages_sent if messages_sent > 0 else 0.0,
                    "conversion_rate": conversions / messages_sent if messages_sent > 0 else 0.0
                })
    except Exception as e:
        print(f"Error getting campaign performance: {e}")
    
    return {"campaigns": campaigns}


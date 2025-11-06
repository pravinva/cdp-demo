"""
Analytics API endpoints
Dashboard data and analytics
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..dependencies import get_tenant_context, get_spark_session

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_data(
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Get dashboard summary data"""
    
    # Total customers
    customers_count = spark.sql(f"""
        SELECT COUNT(*) as total
        FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}'
    """).collect()[0]['total']
    
    # Active campaigns
    active_campaigns = spark.sql(f"""
        SELECT COUNT(*) as total
        FROM cdp_platform.core.campaigns
        WHERE tenant_id = '{tenant_id}' AND status = 'active'
    """).collect()[0]['total']
    
    # Total messages sent (last 30 days)
    messages_sent = spark.sql(f"""
        SELECT COUNT(*) as total
        FROM cdp_platform.core.deliveries
        WHERE tenant_id = '{tenant_id}'
        AND sent_at >= current_timestamp() - INTERVAL 30 DAY
    """).collect()[0]['total']
    
    # Conversion rate (last 30 days)
    conversions_data = spark.sql(f"""
        SELECT 
            COUNT(*) as total_sent,
            SUM(CASE WHEN converted = true THEN 1 ELSE 0 END) as total_converted
        FROM cdp_platform.core.deliveries
        WHERE tenant_id = '{tenant_id}'
        AND sent_at >= current_timestamp() - INTERVAL 30 DAY
    """).collect()[0]
    
    conversion_rate = (
        conversions_data['total_converted'] / conversions_data['total_sent']
        if conversions_data['total_sent'] > 0 else 0.0
    )
    
    # Active journeys
    active_journeys = spark.sql(f"""
        SELECT COUNT(DISTINCT journey_id) as total
        FROM cdp_platform.core.customer_journey_states
        WHERE tenant_id = '{tenant_id}' AND status = 'active'
    """).collect()[0]['total']
    
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
    spark = Depends(get_spark_session)
):
    """Get customer segment distribution"""
    
    query = f"""
        SELECT 
            COALESCE(segment, 'Unknown') as segment,
            COUNT(*) as count
        FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}'
        GROUP BY segment
        ORDER BY count DESC
    """
    
    results = spark.sql(query).collect()
    
    return {
        "segments": [
            {"segment": row['segment'], "count": row['count']}
            for row in results
        ]
    }


@router.get("/campaigns/performance")
async def get_campaign_performance(
    tenant_id: str = Depends(get_tenant_context),
    days: int = Query(30, ge=1, le=365),
    spark = Depends(get_spark_session)
):
    """Get campaign performance metrics"""
    
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
    
    results = spark.sql(query).collect()
    
    campaigns = []
    for row in results:
        messages_sent = row['messages_sent'] or 0
        messages_opened = row['messages_opened'] or 0
        conversions = row['conversions'] or 0
        
        campaigns.append({
            "campaign_id": row['campaign_id'],
            "name": row['name'],
            "goal": row['goal'],
            "messages_sent": messages_sent,
            "messages_opened": messages_opened,
            "conversions": conversions,
            "open_rate": messages_opened / messages_sent if messages_sent > 0 else 0.0,
            "conversion_rate": conversions / messages_sent if messages_sent > 0 else 0.0
        })
    
    return {"campaigns": campaigns}


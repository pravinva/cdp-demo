"""
Customer API endpoints
CRUD operations and customer 360 views
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.customer import Customer, CustomerCreate, CustomerUpdate, Customer360, CustomerListResponse
from ..dependencies import get_tenant_context, get_spark_session
from ..services.graph_query_service import GraphQueryService
import uuid

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    tenant_id: str = Depends(get_tenant_context),
    segment: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    spark = Depends(get_spark_session)
):
    """List customers with filtering and pagination"""
    
    offset = (page - 1) * page_size
    
    # Build query
    where_clauses = [f"tenant_id = '{tenant_id}'"]
    
    if segment:
        where_clauses.append(f"segment = '{segment}'")
    
    if search:
        where_clauses.append(
            f"(first_name LIKE '%{search}%' OR last_name LIKE '%{search}%' OR email LIKE '%{search}%')"
        )
    
    where_clause = " AND ".join(where_clauses)
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*) as total
        FROM cdp_platform.core.customers
        WHERE {where_clause}
    """
    total_result = spark.sql(count_query).collect()
    total = total_result[0]['total'] if total_result else 0
    
    # Get customers
    query = f"""
        SELECT *
        FROM cdp_platform.core.customers
        WHERE {where_clause}
        ORDER BY lifetime_value DESC NULLS LAST, created_at DESC
        LIMIT {page_size} OFFSET {offset}
    """
    
    results = spark.sql(query).toPandas().to_dict('records')
    
    # Convert to Customer models
    customers = []
    for row in results:
        try:
            # Handle decimal types
            row_dict = {k: float(v) if hasattr(v, '__float__') else v for k, v in row.items()}
            customers.append(Customer(**row_dict))
        except Exception as e:
            print(f"Error parsing customer: {e}")
            continue
    
    return CustomerListResponse(
        customers=customers,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{customer_id}", response_model=Customer360)
async def get_customer_360(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Get complete customer 360 view"""
    
    # 1. Profile
    profile_query = f"""
        SELECT * FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """
    profile_result = spark.sql(profile_query).toPandas().to_dict('records')
    
    if not profile_result:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    profile_dict = profile_result[0]
    # Convert decimals to float
    profile_dict = {k: float(v) if hasattr(v, '__float__') else v for k, v in profile_dict.items()}
    profile = Customer(**profile_dict)
    
    # 2. Recent events
    events_query = f"""
        SELECT event_type, event_timestamp, page_url, properties
        FROM cdp_platform.core.clickstream_events
        WHERE tenant_id = '{tenant_id}' 
        AND match_id = '{profile.match_id if profile.match_id else ""}'
        ORDER BY event_timestamp DESC
        LIMIT 50
    """
    recent_events_df = spark.sql(events_query)
    recent_events = [
        {
            'event_type': row['event_type'],
            'event_timestamp': str(row['event_timestamp']),
            'page_url': row['page_url'],
            'properties': dict(row['properties']) if row['properties'] else {}
        }
        for row in recent_events_df.collect()
    ]
    
    # 3. Campaign history
    campaign_query = f"""
        SELECT 
            c.name as campaign_name,
            d.sent_at,
            d.channel,
            d.opened,
            d.clicked,
            d.converted
        FROM cdp_platform.core.deliveries d
        LEFT JOIN cdp_platform.core.campaigns c 
            ON d.campaign_id = c.campaign_id 
            AND d.tenant_id = c.tenant_id
        WHERE d.tenant_id = '{tenant_id}' AND d.customer_id = '{customer_id}'
        ORDER BY d.sent_at DESC
        LIMIT 20
    """
    campaign_history_df = spark.sql(campaign_query)
    campaign_history = [
        {
            'campaign_name': row['campaign_name'],
            'sent_at': str(row['sent_at']),
            'channel': row['channel'],
            'opened': bool(row['opened']) if row['opened'] is not None else False,
            'clicked': bool(row['clicked']) if row['clicked'] is not None else False,
            'converted': bool(row['converted']) if row['converted'] is not None else False
        }
        for row in campaign_history_df.collect()
    ]
    
    # 4. Agent decisions
    decisions_query = f"""
        SELECT 
            decision_id,
            campaign_id,
            action,
            channel,
            reasoning_summary,
            confidence_score,
            timestamp
        FROM cdp_platform.core.agent_decisions
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
        ORDER BY timestamp DESC
        LIMIT 10
    """
    decisions_df = spark.sql(decisions_query)
    agent_decisions = [
        {
            'decision_id': row['decision_id'],
            'campaign_id': row['campaign_id'],
            'action': row['action'],
            'channel': row['channel'],
            'reasoning_summary': row['reasoning_summary'],
            'confidence_score': float(row['confidence_score']) if row['confidence_score'] else 0.0,
            'timestamp': str(row['timestamp'])
        }
        for row in decisions_df.collect()
    ]
    
    # 5. Household members (if applicable)
    household_members = None
    if profile.household_id:
        graph_service = GraphQueryService(tenant_id, use_neptune=False)
        household_members = graph_service.get_household_members(customer_id)
    
    return Customer360(
        profile=profile,
        recent_events=recent_events,
        campaign_history=campaign_history,
        agent_decisions=agent_decisions,
        household_members=household_members
    )


@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Create new customer"""
    
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    
    # Insert into customers table
    insert_query = f"""
        INSERT INTO cdp_platform.core.customers
        (customer_id, tenant_id, email, phone, first_name, last_name, 
         segment, created_at, updated_at)
        VALUES (
            '{customer_id}',
            '{tenant_id}',
            '{customer.email}',
            {'NULL' if not customer.phone else "'" + customer.phone + "'"},
            '{customer.first_name}',
            '{customer.last_name}',
            {'NULL' if not customer.segment else "'" + customer.segment + "'"},
            current_timestamp(),
            current_timestamp()
        )
    """
    
    spark.sql(insert_query)
    
    # Return created customer
    return await get_customer_360(customer_id, tenant_id, spark)


@router.patch("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    updates: CustomerUpdate,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Update customer"""
    
    # Build SET clause
    set_clauses = []
    if updates.email:
        set_clauses.append(f"email = '{updates.email}'")
    if updates.phone:
        set_clauses.append(f"phone = '{updates.phone}'")
    if updates.first_name:
        set_clauses.append(f"first_name = '{updates.first_name}'")
    if updates.last_name:
        set_clauses.append(f"last_name = '{updates.last_name}'")
    if updates.segment:
        set_clauses.append(f"segment = '{updates.segment}'")
    if updates.preferred_channel:
        set_clauses.append(f"preferred_channel = '{updates.preferred_channel}'")
    if updates.email_consent is not None:
        set_clauses.append(f"email_consent = {updates.email_consent}")
    if updates.sms_consent is not None:
        set_clauses.append(f"sms_consent = {updates.sms_consent}")
    if updates.push_consent is not None:
        set_clauses.append(f"push_consent = {updates.push_consent}")
    
    set_clauses.append("updated_at = current_timestamp()")
    
    if len(set_clauses) == 1:  # Only updated_at
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_query = f"""
        UPDATE cdp_platform.core.customers
        SET {', '.join(set_clauses)}
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """
    
    spark.sql(update_query)
    
    # Return updated customer
    profile_result = spark.sql(f"""
        SELECT * FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """).toPandas().to_dict('records')
    
    if not profile_result:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    profile_dict = profile_result[0]
    profile_dict = {k: float(v) if hasattr(v, '__float__') else v for k, v in profile_dict.items()}
    return Customer(**profile_dict)


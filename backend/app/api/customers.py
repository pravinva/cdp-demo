"""
Customer API endpoints
CRUD operations and customer 360 views
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.customer import Customer, CustomerCreate, CustomerUpdate, Customer360, CustomerListResponse
from ..dependencies import get_tenant_context, get_workspace_client
from ..services.graph_query_service import GraphQueryService
from ..config import get_settings
from databricks.sdk.service.sql import StatementState
from datetime import datetime
import uuid

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    tenant_id: str = Depends(get_tenant_context),
    segment: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    w = Depends(get_workspace_client)
):
    """List customers with filtering and pagination"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"  # Fallback warehouse ID
    
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
    
    try:
        count_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=count_query,
            wait_timeout="30s"
        )
        total = 0
        if count_response.result and count_response.result.data_array:
            total = int(count_response.result.data_array[0][0]) if count_response.result.data_array[0] else 0
    except Exception as e:
        print(f"Error getting count: {e}")
        total = 0
    
    # Get customers
    query = f"""
        SELECT *
        FROM cdp_platform.core.customers
        WHERE {where_clause}
        ORDER BY lifetime_value DESC NULLS LAST, created_at DESC
        LIMIT {page_size} OFFSET {offset}
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        # Parse results
        customers = []
        if response.result and response.result.data_array:
            # Get column names from manifest
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            
            for row in response.result.data_array:
                try:
                    row_dict = {}
                    for i, col_name in enumerate(columns):
                        value = row[i] if i < len(row) else None
                        # Handle datetime conversion
                        if col_name in ['created_at', 'updated_at', 'date_of_birth', 'first_purchase_date', 'last_purchase_date']:
                            if value:
                                if isinstance(value, str):
                                    try:
                                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    except:
                                        value = None
                                elif not isinstance(value, datetime):
                                    value = None
                            # Provide defaults for required datetime fields
                            if value is None:
                                if col_name in ['created_at', 'updated_at']:
                                    value = datetime.now()
                        # Handle None values for required fields with defaults
                        if col_name == 'preferred_language' and value is None:
                            value = 'en'
                        if col_name in ['email_consent', 'sms_consent', 'push_consent'] and value is None:
                            value = False
                        if col_name == 'total_purchases' and value is None:
                            value = 0
                        if col_name == 'registered_devices' and value is None:
                            value = []
                        row_dict[col_name] = value
                    customers.append(Customer(**row_dict))
                except Exception as e:
                    print(f"Error parsing customer: {e}, row: {row[:5] if row else 'empty'}")
                    continue
    except Exception as e:
        print(f"Error fetching customers: {e}")
        customers = []
    
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
    w = Depends(get_workspace_client)
):
    """Get complete customer 360 view"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    # 1. Profile
    profile_query = f"""
        SELECT * FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """
    
    try:
        profile_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=profile_query,
            wait_timeout="30s"
        )
        
        if not profile_response.result or not profile_response.result.data_array:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Parse profile
        columns = [col.name for col in profile_response.manifest.schema.columns] if profile_response.manifest and profile_response.manifest.schema else []
        profile_row = profile_response.result.data_array[0]
        profile_dict = {columns[i]: profile_row[i] for i in range(len(columns))}
        profile = Customer(**profile_dict)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 2. Recent events
    events_query = f"""
        SELECT event_type, event_timestamp, page_url, properties
        FROM cdp_platform.core.clickstream_events
        WHERE tenant_id = '{tenant_id}' 
        AND match_id = '{profile.match_id if profile.match_id else ""}'
        ORDER BY event_timestamp DESC
        LIMIT 50
    """
    
    recent_events = []
    try:
        events_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=events_query,
            wait_timeout="30s"
        )
        
        if events_response.result and events_response.result.data_array:
            event_columns = [col.name for col in events_response.manifest.schema.columns] if events_response.manifest and events_response.manifest.schema else []
            for row in events_response.result.data_array:
                row_dict = {event_columns[i]: row[i] for i in range(len(event_columns))}
                recent_events.append({
                    'event_type': row_dict.get('event_type'),
                    'event_timestamp': str(row_dict.get('event_timestamp', '')),
                    'page_url': row_dict.get('page_url'),
                    'properties': row_dict.get('properties') or {}
                })
    except Exception as e:
        print(f"Error fetching events: {e}")
    
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
    
    campaign_history = []
    try:
        campaign_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=campaign_query,
            wait_timeout="30s"
        )
        
        if campaign_response.result and campaign_response.result.data_array:
            campaign_columns = [col.name for col in campaign_response.manifest.schema.columns] if campaign_response.manifest and campaign_response.manifest.schema else []
            for row in campaign_response.result.data_array:
                row_dict = {campaign_columns[i]: row[i] for i in range(len(campaign_columns))}
                campaign_history.append({
                    'campaign_name': row_dict.get('campaign_name'),
                    'sent_at': str(row_dict.get('sent_at', '')),
                    'channel': row_dict.get('channel'),
                    'opened': bool(row_dict.get('opened')) if row_dict.get('opened') is not None else False,
                    'clicked': bool(row_dict.get('clicked')) if row_dict.get('clicked') is not None else False,
                    'converted': bool(row_dict.get('converted')) if row_dict.get('converted') is not None else False
                })
    except Exception as e:
        print(f"Error fetching campaign history: {e}")
    
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
    
    agent_decisions = []
    try:
        decisions_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=decisions_query,
            wait_timeout="30s"
        )
        
        if decisions_response.result and decisions_response.result.data_array:
            decision_columns = [col.name for col in decisions_response.manifest.schema.columns] if decisions_response.manifest and decisions_response.manifest.schema else []
            for row in decisions_response.result.data_array:
                row_dict = {decision_columns[i]: row[i] for i in range(len(decision_columns))}
                agent_decisions.append({
                    'decision_id': row_dict.get('decision_id'),
                    'campaign_id': row_dict.get('campaign_id'),
                    'action': row_dict.get('action'),
                    'channel': row_dict.get('channel'),
                    'reasoning_summary': row_dict.get('reasoning_summary'),
                    'confidence_score': float(row_dict.get('confidence_score', 0)) if row_dict.get('confidence_score') else 0.0,
                    'timestamp': str(row_dict.get('timestamp', ''))
                })
    except Exception as e:
        print(f"Error fetching agent decisions: {e}")
    
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
    w = Depends(get_workspace_client)
):
    """Create new customer"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    customer_id = f"cust_{uuid.uuid4().hex[:8]}"
    
    # Insert into customers table
    phone_val = "NULL" if not customer.phone else f"'{customer.phone}'"
    segment_val = "NULL" if not customer.segment else f"'{customer.segment}'"
    
    insert_query = f"""
        INSERT INTO cdp_platform.core.customers
        (customer_id, tenant_id, email, phone, first_name, last_name, 
         segment, created_at, updated_at)
        VALUES (
            '{customer_id}',
            '{tenant_id}',
            '{customer.email}',
            {phone_val},
            '{customer.first_name}',
            '{customer.last_name}',
            {segment_val},
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
        print(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")
    
    # Return created customer
    return await get_customer_360(customer_id, tenant_id, w)


@router.patch("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    updates: CustomerUpdate,
    tenant_id: str = Depends(get_tenant_context),
    w = Depends(get_workspace_client)
):
    """Update customer"""
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
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
    
    try:
        w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=update_query,
            wait_timeout="30s"
        )
    except Exception as e:
        print(f"Error updating customer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update customer: {str(e)}")
    
    # Return updated customer
    select_query = f"""
        SELECT * FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=select_query,
            wait_timeout="30s"
        )
        
        if not response.result or not response.result.data_array:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
        profile_row = response.result.data_array[0]
        profile_dict = {columns[i]: profile_row[i] for i in range(len(columns))}
        return Customer(**profile_dict)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching updated customer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch updated customer: {str(e)}")


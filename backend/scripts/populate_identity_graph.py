"""
Populate Identity Graph Data
Creates match groups and identity graph edges for demo purposes
"""

from databricks.sdk import WorkspaceClient
from datetime import datetime, timedelta
import random
import uuid

def populate_identity_graph(w: WorkspaceClient, warehouse_id: str, tenant_id: str = "demo_tenant"):
    """Populate identity graph tables with demo data"""
    
    print(f"Populating identity graph data for tenant: {tenant_id}")
    
    # 1. Get existing customers and assign zip codes for households
    customers_query = f"""
        SELECT customer_id, email, zip_code
        FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}'
        LIMIT 100
    """
    
    try:
        customers_response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=customers_query,
            wait_timeout="30s"
        )
        
        if not customers_response.result or not customers_response.result.data_array:
            print("No customers found. Please seed customers first.")
            return
        
        columns = [col.name for col in customers_response.manifest.schema.columns] if customers_response.manifest and customers_response.manifest.schema else []
        customers = []
        for row in customers_response.result.data_array:
            customer_dict = {columns[i]: row[i] for i in range(len(columns))}
            # Assign zip code if missing
            if not customer_dict.get('zip_code'):
                customer_dict['zip_code'] = f"{random.randint(10000, 99999)}"
                # Update customer with zip code
                update_zip = f"""
                    UPDATE cdp_platform.core.customers
                    SET zip_code = '{customer_dict['zip_code']}'
                    WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_dict['customer_id']}'
                """
                try:
                    w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=update_zip,
                        wait_timeout="30s"
                    )
                except Exception as e:
                    print(f"Error updating zip code: {e}")
            customers.append(customer_dict)
        
        print(f"Found {len(customers)} customers")
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return
    
    # 2. Create match groups for customers (one per customer)
    print("Creating match groups...")
    match_groups = []
    
    for customer in customers:
        match_id = f"match_{uuid.uuid4().hex[:8]}"
        match_groups.append({
            'match_id': match_id,
            'customer_id': customer['customer_id'],
            'email': customer['email']
        })
        
        # Update customer with match_id
        update_query = f"""
            UPDATE cdp_platform.core.customers
            SET match_id = '{match_id}'
            WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer['customer_id']}'
        """
        
        try:
            w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=update_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error updating customer {customer['customer_id']}: {e}")
    
    # Insert match groups
    for mg in match_groups:
        insert_match_group = f"""
            INSERT INTO cdp_platform.core.match_groups
            (match_id, tenant_id, known_emails, known_phones, known_login_ids,
             shared_devices, shared_ips, shared_addresses,
             total_events, anonymous_events, known_events, unique_devices, unique_ips,
             is_household, household_size, first_seen, last_seen, created_at, updated_at)
            VALUES (
                '{mg['match_id']}',
                '{tenant_id}',
                ARRAY('{mg['email']}'),
                ARRAY(),
                ARRAY('{mg['customer_id']}'),
                ARRAY(),
                ARRAY(),
                ARRAY(),
                {random.randint(10, 100)},
                {random.randint(0, 20)},
                {random.randint(10, 80)},
                {random.randint(1, 3)},
                {random.randint(1, 5)},
                false,
                1,
                current_timestamp() - INTERVAL {random.randint(1, 90)} DAY,
                current_timestamp() - INTERVAL {random.randint(0, 7)} DAY,
                current_timestamp(),
                current_timestamp()
            )
        """
        
        try:
            w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=insert_match_group,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error inserting match group {mg['match_id']}: {e}")
    
    print(f"✓ Created {len(match_groups)} match groups")
    
    # 3. Create households (group customers by zip_code)
    print("Creating households...")
    
    # Group customers by zip code (assign some customers to same zip codes)
    zip_codes = [f"{random.randint(10000, 99999)}" for _ in range(10)]  # 10 unique zip codes
    zip_groups = {zip_code: [] for zip_code in zip_codes}
    
    # Distribute customers across zip codes (some zip codes will have multiple customers)
    for i, customer in enumerate(customers):
        zip_code = zip_codes[i % len(zip_codes)]  # Distribute evenly
        zip_groups[zip_code].append(customer)
    
    # Create households for zip codes with 2+ customers
    household_count = 0
    for zip_code, zip_customers in zip_groups.items():
        if len(zip_customers) >= 2:
            household_id = f"household_{uuid.uuid4().hex[:8]}"
            household_count += 1
            
            # Update customers with household_id
            for i, customer in enumerate(zip_customers[:5]):  # Limit to 5 per household
                role = 'head' if i == 0 else 'member'
                update_household = f"""
                    UPDATE cdp_platform.core.customers
                    SET household_id = '{household_id}',
                        household_role = '{role}',
                        zip_code = '{zip_code}',
                        updated_at = current_timestamp()
                    WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer['customer_id']}'
                """
                
                try:
                    w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=update_household,
                        wait_timeout="30s"
                    )
                except Exception as e:
                    print(f"Error updating household for {customer['customer_id']}: {e}")
            
            # Update match group for household
            if len(zip_customers) > 1:
                match_id_for_household = next((mg['match_id'] for mg in match_groups if mg['customer_id'] == zip_customers[0]['customer_id']), None)
                if match_id_for_household:
                    update_match_group = f"""
                        UPDATE cdp_platform.core.match_groups
                        SET is_household = true,
                            household_size = {len(zip_customers[:5])},
                            updated_at = current_timestamp()
                        WHERE tenant_id = '{tenant_id}' AND match_id = '{match_id_for_household}'
                    """
                    
                    try:
                        w.statement_execution.execute_statement(
                            warehouse_id=warehouse_id,
                            statement=update_match_group,
                            wait_timeout="30s"
                        )
                    except Exception as e:
                        print(f"Error updating match group for household: {e}")
    
    print(f"✓ Created {household_count} households")
    
    # 4. Create identity graph edges
    print("Creating identity graph edges...")
    edges_created = 0
    
    # Create household edges
    for zip_code, zip_customers in zip_groups.items():
        if len(zip_customers) >= 2:
            for i in range(len(zip_customers) - 1):
                from_customer = zip_customers[i]
                to_customer = zip_customers[i + 1]
                
                edge_id = f"edge_{uuid.uuid4().hex}"
                
                insert_edge = f"""
                    INSERT INTO cdp_platform.core.identity_graph_edges
                    (edge_id, tenant_id, from_entity_type, from_entity_id,
                     to_entity_type, to_entity_id, relationship_type,
                     strength, evidence_count, first_seen, last_seen)
                    VALUES (
                        '{edge_id}',
                        '{tenant_id}',
                        'customer',
                        '{from_customer['customer_id']}',
                        'customer',
                        '{to_customer['customer_id']}',
                        'household',
                        {random.uniform(0.7, 0.95)},
                        {random.randint(5, 50)},
                        current_timestamp() - INTERVAL {random.randint(1, 90)} DAY,
                        current_timestamp() - INTERVAL {random.randint(0, 7)} DAY
                    )
                """
                
                try:
                    w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=insert_edge,
                        wait_timeout="30s"
                    )
                    edges_created += 1
                except Exception as e:
                    print(f"Error inserting edge: {e}")
    
    # Create some match group to customer edges
    for mg in match_groups[:20]:  # Limit to first 20
        edge_id = f"edge_{uuid.uuid4().hex}"
        
        insert_edge = f"""
            INSERT INTO cdp_platform.core.identity_graph_edges
            (edge_id, tenant_id, from_entity_type, from_entity_id,
             to_entity_type, to_entity_id, relationship_type,
             strength, evidence_count, first_seen, last_seen)
            VALUES (
                '{edge_id}',
                '{tenant_id}',
                'match_group',
                '{mg['match_id']}',
                'customer',
                '{mg['customer_id']}',
                'identity_match',
                {random.uniform(0.8, 0.99)},
                {random.randint(10, 100)},
                current_timestamp() - INTERVAL {random.randint(1, 90)} DAY,
                current_timestamp() - INTERVAL {random.randint(0, 7)} DAY
            )
        """
        
        try:
            w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=insert_edge,
                wait_timeout="30s"
            )
            edges_created += 1
        except Exception as e:
            print(f"Error inserting match group edge: {e}")
    
    print(f"✓ Created {edges_created} identity graph edges")
    print("\n✅ Identity graph data populated successfully!")


if __name__ == "__main__":
    from ..config import get_settings
    
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    w = WorkspaceClient()
    populate_identity_graph(w, warehouse_id)


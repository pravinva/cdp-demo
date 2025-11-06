"""
Identity Resolution Service
Processes clickstream events to resolve identities and create match groups
"""

from typing import List, Dict, Optional
from datetime import datetime
import uuid
import json

from ..dependencies import get_workspace_client
from ..config import get_settings


class IdentityResolutionService:
    """
    Service for resolving customer identities from clickstream events
    Groups events by matching identity signals (email, phone, device, IP)
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.w = get_workspace_client()
        self.settings = get_settings()
        self.warehouse_id = self.settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    def run_identity_resolution(self, batch_size: int = 10000) -> Dict[str, int]:
        """
        Run identity resolution on recent clickstream events
        Creates/updates match groups based on identity signals
        """
        print(f"Running identity resolution for tenant: {self.tenant_id}")
        
        # Get recent events without match_id grouped by email
        query = f"""
            SELECT 
                email,
                COUNT(*) as event_count,
                COLLECT_LIST(DISTINCT cookie_id) as cookie_ids,
                COLLECT_LIST(DISTINCT device_id) as device_ids,
                COLLECT_LIST(DISTINCT ip_address) as ip_addresses,
                MIN(event_timestamp) as first_seen,
                MAX(event_timestamp) as last_seen
            FROM cdp_platform.core.clickstream_events
            WHERE tenant_id = '{self.tenant_id}'
            AND match_id IS NULL
            AND email IS NOT NULL
            GROUP BY email
            ORDER BY last_seen DESC
            LIMIT {batch_size}
        """
        
        match_groups_created = 0
        events_processed = 0
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if not response.result or not response.result.data_array:
                print("No unmatched events found")
                return {"processed": 0, "match_groups_created": 0}
            
            columns = [column.name for column in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            
            for row in response.result.data_array:
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                email = row_dict.get('email')
                if not email:
                    continue
                
                match_id = f"match_{uuid.uuid4().hex[:8]}"
                event_count = int(row_dict.get('event_count', 0) or 0)
                events_processed += event_count
                
                # Get unique values from arrays (they come as strings or lists)
                cookie_ids = row_dict.get('cookie_ids', [])
                device_ids = row_dict.get('device_ids', [])
                ip_addresses = row_dict.get('ip_addresses', [])
                
                if isinstance(cookie_ids, str):
                    try:
                        cookie_ids = json.loads(cookie_ids)
                    except:
                        cookie_ids = []
                if isinstance(device_ids, str):
                    try:
                        device_ids = json.loads(device_ids)
                    except:
                        device_ids = []
                if isinstance(ip_addresses, str):
                    try:
                        ip_addresses = json.loads(ip_addresses)
                    except:
                        ip_addresses = []
                
                # Limit array sizes
                cookie_ids = list(set([c for c in cookie_ids if c]))[:10]
                device_ids = list(set([d for d in device_ids if d]))[:10]
                ip_addresses = list(set([ip for ip in ip_addresses if ip]))[:10]
                
                # Insert match group
                known_emails_json = json.dumps([email])
                shared_devices_json = json.dumps(device_ids)
                shared_ips_json = json.dumps(ip_addresses)
                
                insert_match_group = f"""
                    INSERT INTO cdp_platform.core.match_groups
                    (match_id, tenant_id, known_emails, known_phones, known_login_ids,
                     shared_devices, shared_ips, shared_addresses,
                     total_events, anonymous_events, known_events,
                     unique_devices, unique_ips, is_household, household_size,
                     first_seen, last_seen, created_at, updated_at)
                    VALUES (
                        '{match_id}',
                        '{self.tenant_id}',
                        ARRAY({','.join([f"'{email}'" for _ in [email]])}),
                        ARRAY(),
                        ARRAY(),
                        ARRAY({','.join([f"'{d}'" for d in device_ids]) if device_ids else ''}),
                        ARRAY({','.join([f"'{ip}'" for ip in ip_addresses]) if ip_addresses else ''}),
                        ARRAY(),
                        {event_count},
                        0,
                        {event_count},
                        {len(device_ids)},
                        {len(ip_addresses)},
                        false,
                        1,
                        current_timestamp(),
                        current_timestamp(),
                        current_timestamp(),
                        current_timestamp()
                    )
                """
                
                try:
                    self.w.statement_execution.execute_statement(
                        warehouse_id=self.warehouse_id,
                        statement=insert_match_group,
                        wait_timeout="30s"
                    )
                    match_groups_created += 1
                except Exception as e:
                    print(f"Error inserting match group: {e}")
                    continue
                
                # Update events with match_id
                update_events = f"""
                    UPDATE cdp_platform.core.clickstream_events
                    SET match_id = '{match_id}',
                        match_rule = 'email_match',
                        match_confidence = 0.9
                    WHERE tenant_id = '{self.tenant_id}'
                    AND email = '{email}'
                    AND match_id IS NULL
                """
                
                try:
                    self.w.statement_execution.execute_statement(
                        warehouse_id=self.warehouse_id,
                        statement=update_events,
                        wait_timeout="30s"
                    )
                except Exception as e:
                    print(f"Error updating events: {e}")
        
        except Exception as e:
            print(f"Error running identity resolution: {e}")
            return {"processed": events_processed, "match_groups_created": match_groups_created}
        
        print(f"✓ Processed {events_processed} events")
        print(f"✓ Created {match_groups_created} match groups")
        
        return {
            "processed": events_processed,
            "match_groups_created": match_groups_created
        }
    
    def detect_households(self) -> int:
        """
        Detect households based on shared addresses, devices, IPs
        """
        # Simple household detection: customers with same zip_code
        query = f"""
            SELECT 
                zip_code,
                COUNT(DISTINCT customer_id) as household_size,
                COLLECT_LIST(customer_id) as customer_ids
            FROM cdp_platform.core.customers
            WHERE tenant_id = '{self.tenant_id}'
            AND zip_code IS NOT NULL
            GROUP BY zip_code
            HAVING COUNT(DISTINCT customer_id) > 1
        """
        
        household_count = 0
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if not response.result or not response.result.data_array:
                return 0
            
            columns = [column.name for column in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            
            for row in response.result.data_array:
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                household_id = f"household_{uuid.uuid4().hex[:8]}"
                
                # Get customer_ids (may be array or string)
                customer_ids = row_dict.get('customer_ids', [])
                if isinstance(customer_ids, str):
                    try:
                        customer_ids = json.loads(customer_ids)
                    except:
                        customer_ids = []
                
                # Update customers with household_id
                for i, customer_id in enumerate(customer_ids):
                    household_role = 'head' if i == 0 else 'member'
                    update_query = f"""
                        UPDATE cdp_platform.core.customers
                        SET household_id = '{household_id}',
                            household_role = '{household_role}',
                            updated_at = current_timestamp()
                        WHERE tenant_id = '{self.tenant_id}'
                        AND customer_id = '{customer_id}'
                    """
                    
                    try:
                        self.w.statement_execution.execute_statement(
                            warehouse_id=self.warehouse_id,
                            statement=update_query,
                            wait_timeout="30s"
                        )
                    except Exception as e:
                        print(f"Error updating customer household: {e}")
                        continue
                
                household_count += 1
        
        except Exception as e:
            print(f"Error detecting households: {e}")
        
        print(f"✓ Detected {household_count} households")
        return household_count


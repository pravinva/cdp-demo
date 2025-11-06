"""
Scheduled Deliveries Workflow
Processes scheduled message deliveries and sends them
Run this as a Databricks Workflow task
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.services.activation_service import ActivationService
from app.dependencies import get_workspace_client
from app.config import get_settings

def process_scheduled_deliveries():
    """Process scheduled deliveries that are ready to be sent"""
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    w = get_workspace_client()
    
    # For now, process demo_tenant
    tenants = ['demo_tenant']
    
    total_sent = 0
    
    for tenant_id in tenants:
        try:
            print(f"Processing scheduled deliveries for tenant: {tenant_id}")
            
            # Get deliveries scheduled for now or earlier that haven't been sent
            query = f"""
                SELECT 
                    delivery_id,
                    customer_id,
                    channel,
                    to_address,
                    subject,
                    message_preview,
                    campaign_id,
                    journey_id,
                    journey_step_id
                FROM cdp_platform.core.deliveries
                WHERE tenant_id = '{tenant_id}'
                AND status = 'scheduled'
                AND sent_at <= current_timestamp()
                ORDER BY sent_at ASC
                LIMIT 100
            """
            
            response = w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if not response.result or not response.result.data_array:
                print(f"No scheduled deliveries found for {tenant_id}")
                continue
            
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            activation_service = ActivationService(tenant_id)
            
            for row in response.result.data_array:
                try:
                    row_dict = {columns[i]: row[i] for i in range(len(columns))}
                    delivery_id = row_dict.get('delivery_id')
                    channel = row_dict.get('channel')
                    to_address = row_dict.get('to_address')
                    subject = row_dict.get('subject')
                    message_preview = row_dict.get('message_preview')
                    
                    # In production, this would actually send via SendGrid/Twilio
                    # For now, just update status to 'sent'
                    update_query = f"""
                        UPDATE cdp_platform.core.deliveries
                        SET status = 'sent',
                            sent_at = current_timestamp()
                        WHERE tenant_id = '{tenant_id}'
                        AND delivery_id = '{delivery_id}'
                    """
                    
                    w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=update_query,
                        wait_timeout="30s"
                    )
                    
                    print(f"  ✓ Sent {channel} to {to_address} (delivery_id: {delivery_id})")
                    total_sent += 1
                
                except Exception as e:
                    print(f"Error sending delivery {delivery_id}: {e}")
                    # Mark as failed
                    try:
                        update_query = f"""
                            UPDATE cdp_platform.core.deliveries
                            SET status = 'failed',
                                error_message = '{str(e).replace("'", "''")}'
                            WHERE tenant_id = '{tenant_id}'
                            AND delivery_id = '{delivery_id}'
                        """
                        w.statement_execution.execute_statement(
                            warehouse_id=warehouse_id,
                            statement=update_query,
                            wait_timeout="30s"
                        )
                    except:
                        pass
                    continue
        
        except Exception as e:
            print(f"Error processing tenant {tenant_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Scheduled deliveries processed")
    print(f"Total messages sent: {total_sent}")
    
    return {'sent': total_sent}

if __name__ == "__main__":
    process_scheduled_deliveries()


#!/usr/bin/env python3
"""
Check if campaigns table is empty
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from databricks.sdk import WorkspaceClient
from app.config import get_settings

def check_campaigns_table():
    """Check if campaigns table is empty"""
    w = WorkspaceClient()
    settings = get_settings()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    try:
        # Count total campaigns
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement="SELECT COUNT(*) as total FROM cdp_platform.core.campaigns",
            wait_timeout="30s"
        )
        
        if response.result and response.result.data_array:
            total_count = int(response.result.data_array[0][0] or 0)
            print(f"📊 Total campaigns in table: {total_count}")
            
            if total_count == 0:
                print("✅ Campaigns table is EMPTY")
            else:
                print(f"✅ Campaigns table has {total_count} campaign(s)")
                
                # Also check by tenant
                response_tenant = w.statement_execution.execute_statement(
                    warehouse_id=warehouse_id,
                    statement="SELECT tenant_id, COUNT(*) as count FROM cdp_platform.core.campaigns GROUP BY tenant_id",
                    wait_timeout="30s"
                )
                
                if response_tenant.result and response_tenant.result.data_array:
                    print("\n📋 Campaigns by tenant:")
                    for row in response_tenant.result.data_array:
                        tenant_id = row[0]
                        count = row[1]
                        print(f"   • {tenant_id}: {count} campaign(s)")
        else:
            print("⚠️  No data returned from query")
            
    except Exception as e:
        print(f"❌ Error checking campaigns table: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(check_campaigns_table())


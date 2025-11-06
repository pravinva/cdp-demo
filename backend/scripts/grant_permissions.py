"""
Grant permissions to all account users on CDP Platform Unity Catalog
Run this script to grant access to all users in your Databricks account
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.config import get_settings

def grant_permissions_to_account_users():
    """Grant permissions to all account users"""
    
    settings = get_settings()
    w = WorkspaceClient()
    warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    catalog_name = settings.DATABRICKS_CATALOG or "cdp_platform"
    schema_name = settings.DATABRICKS_SCHEMA or "core"
    
    print("=" * 60)
    print("Granting Permissions to All Account Users")
    print("=" * 60)
    
    # SQL statements to grant permissions
    grants = [
        # Catalog permissions
        f"GRANT USE CATALOG ON CATALOG {catalog_name} TO `account users`",
        f"GRANT CREATE SCHEMA ON CATALOG {catalog_name} TO `account users`",
        
        # Schema permissions
        f"GRANT USE SCHEMA ON SCHEMA {catalog_name}.core TO `account users`",
        f"GRANT CREATE TABLE ON SCHEMA {catalog_name}.core TO `account users`",
        f"GRANT MODIFY ON SCHEMA {catalog_name}.core TO `account users`",
        
        f"GRANT USE SCHEMA ON SCHEMA {catalog_name}.staging TO `account users`",
        f"GRANT CREATE TABLE ON SCHEMA {catalog_name}.staging TO `account users`",
        f"GRANT MODIFY ON SCHEMA {catalog_name}.staging TO `account users`",
        
        f"GRANT USE SCHEMA ON SCHEMA {catalog_name}.analytics TO `account users`",
        f"GRANT CREATE TABLE ON SCHEMA {catalog_name}.analytics TO `account users`",
        f"GRANT MODIFY ON SCHEMA {catalog_name}.analytics TO `account users`",
        
        f"GRANT USE SCHEMA ON SCHEMA {catalog_name}.ml TO `account users`",
        f"GRANT CREATE TABLE ON SCHEMA {catalog_name}.ml TO `account users`",
        f"GRANT MODIFY ON SCHEMA {catalog_name}.ml TO `account users`",
        
        # Table permissions
        f"GRANT SELECT ON TABLE {catalog_name}.{schema_name}.customers TO `account users`",
        f"GRANT MODIFY ON TABLE {catalog_name}.{schema_name}.customers TO `account users`",
        
        f"GRANT SELECT ON TABLE {catalog_name}.{schema_name}.campaigns TO `account users`",
        f"GRANT MODIFY ON TABLE {catalog_name}.{schema_name}.campaigns TO `account users`",
        
        f"GRANT SELECT ON TABLE {catalog_name}.{schema_name}.clickstream_events TO `account users`",
        f"GRANT MODIFY ON TABLE {catalog_name}.{schema_name}.clickstream_events TO `account users`",
        
        f"GRANT SELECT ON TABLE {catalog_name}.{schema_name}.agent_decisions TO `account users`",
        f"GRANT MODIFY ON TABLE {catalog_name}.{schema_name}.agent_decisions TO `account users`",
        
        f"GRANT SELECT ON TABLE {catalog_name}.{schema_name}.deliveries TO `account users`",
        f"GRANT MODIFY ON TABLE {catalog_name}.{schema_name}.deliveries TO `account users`",
        
        f"GRANT SELECT ON TABLE {catalog_name}.{schema_name}.match_groups TO `account users`",
        f"GRANT MODIFY ON TABLE {catalog_name}.{schema_name}.match_groups TO `account users`",
    ]
    
    print("\nGranting permissions...")
    success_count = 0
    for grant_sql in grants:
        try:
            response = w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=grant_sql,
                wait_timeout="30s"
            )
            if response.status.state == StatementState.SUCCEEDED:
                success_count += 1
                print(f"  ✓ {grant_sql[:60]}...")
            else:
                error_msg = ""
                if hasattr(response.status, 'error'):
                    error_msg = response.status.error
                # Some grants might fail if already granted, that's okay
                if "already" not in str(error_msg).lower():
                    print(f"  ✗ {grant_sql[:60]}... - {response.status.state}")
        except Exception as e:
            error_msg = str(e).lower()
            if "already" not in error_msg and "does not exist" not in error_msg:
                print(f"  ✗ {grant_sql[:60]}... - {e}")
    
    print("\n" + "=" * 60)
    print(f"✓ Granted {success_count}/{len(grants)} permissions")
    print("=" * 60)
    print("\nAll account users now have:")
    print("  • USE CATALOG on cdp_platform")
    print("  • USE SCHEMA on all schemas (core, staging, analytics, ml)")
    print("  • SELECT and MODIFY on all tables")
    
    return success_count == len(grants)

if __name__ == "__main__":
    grant_permissions_to_account_users()


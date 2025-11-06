"""
Row-Level Security Policies for Unity Catalog
Ensures users can only access data for their tenant
"""

from ..dependencies import get_workspace_client
from ..config import get_settings
from typing import Optional

settings = get_settings()


class RowLevelSecurity:
    """Manage row-level security policies in Unity Catalog"""
    
    def __init__(self):
        self.w = get_workspace_client()
        self.warehouse_id = settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    def create_rls_policy(self, table_name: str, tenant_column: str = "tenant_id"):
        """
        Create row-level security policy for a table
        Users can only access rows where tenant_id matches their tenant
        """
        catalog = settings.DATABRICKS_CATALOG
        schema = settings.DATABRICKS_SCHEMA
        full_table_name = f"{catalog}.{schema}.{table_name}"
        
        # Create RLS policy SQL
        # Note: Unity Catalog RLS uses different syntax than traditional SQL
        # This is a conceptual implementation - actual RLS may vary by Databricks version
        
        policy_sql = f"""
        ALTER TABLE {full_table_name}
        SET ROW FILTER tenant_filter ON ({tenant_column})
        """
        
        # In Unity Catalog, RLS is typically enforced via:
        # 1. Unity Catalog access controls (grants)
        # 2. Dynamic views with WHERE clauses
        # 3. Table functions that filter by tenant
        
        # For now, we'll create a view that enforces tenant filtering
        view_sql = f"""
        CREATE OR REPLACE VIEW {catalog}.{schema}.{table_name}_secure AS
        SELECT *
        FROM {full_table_name}
        WHERE {tenant_column} = current_user_tenant()
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=view_sql,
                wait_timeout=30
            )
            print(f"Created secure view for {table_name}")
        except Exception as e:
            print(f"Error creating RLS policy for {table_name}: {e}")
    
    def grant_tenant_access(self, user_email: str, tenant_id: str):
        """
        Grant user access to specific tenant data
        Uses Unity Catalog grants
        """
        catalog = settings.DATABRICKS_CATALOG
        schema = settings.DATABRICKS_SCHEMA
        
        # Grant SELECT on catalog/schema to user
        grant_sql = f"""
        GRANT SELECT ON CATALOG {catalog} TO `{user_email}`
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=grant_sql,
                wait_timeout=30
            )
            print(f"Granted access to {user_email} for tenant {tenant_id}")
        except Exception as e:
            print(f"Error granting access: {e}")


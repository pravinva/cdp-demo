"""
Graph Query Service - Relationship intelligence queries
"""

from typing import List, Dict, Optional
from ..dependencies import get_workspace_client
from ..config import get_settings


class GraphQueryService:
    """Service for querying identity graph and relationships"""
    
    def __init__(self, tenant_id: str, use_neptune: bool = False):
        self.tenant_id = tenant_id
        self.w = get_workspace_client()
        self.settings = get_settings()
        self.warehouse_id = self.settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
        self.use_neptune = use_neptune
    
    def get_household_members(self, customer_id: str) -> List[Dict]:
        """Get all customers in same household"""
        query = f"""
            SELECT 
                c2.customer_id,
                c2.first_name,
                c2.last_name,
                c2.email,
                c2.household_role
            FROM cdp_platform.core.customers c1
            INNER JOIN cdp_platform.core.customers c2
                ON c1.household_id = c2.household_id
                AND c1.tenant_id = c2.tenant_id
            WHERE c1.tenant_id = '{self.tenant_id}'
            AND c1.customer_id = '{customer_id}'
            AND c2.customer_id != c1.customer_id
            AND c1.household_id IS NOT NULL
        """
        
        members = []
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                for row in response.result.data_array:
                    row_dict = {columns[i]: row[i] for i in range(len(columns))}
                    members.append(row_dict)
        except Exception as e:
            print(f"Error getting household members: {e}")
        
        return members


"""
Agent tools - interfaces to Unity Catalog functions
"""

from ..dependencies import get_workspace_client
from ..config import get_settings
from typing import Dict, List, Any
import json

class AgentTools:
    """Wrapper for UC functions as agent tools"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.w = get_workspace_client()
        self.settings = get_settings()
        self.warehouse_id = self.settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
    
    def get_customer_context(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve complete customer profile and computed metrics
        Tool for agent to understand customer deeply
        """
        query = f"""
            SELECT * FROM TABLE(
                cdp_platform.core.get_customer_context(
                    '{self.tenant_id}',
                    '{customer_id}'
                )
            )
        """
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if not response.result or not response.result.data_array:
                return {"error": "Customer not found"}
            
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            row = response.result.data_array[0]
            return {columns[i]: row[i] for i in range(len(columns))}
        except Exception as e:
            print(f"Error getting customer context: {e}")
            return {"error": str(e)}
    
    def get_recent_behavior(self, customer_id: str, days: int = 30) -> List[Dict]:
        """Get customer events from last N days"""
        query = f"""
            SELECT * FROM TABLE(
                cdp_platform.core.get_recent_behavior(
                    '{self.tenant_id}',
                    '{customer_id}',
                    {days}
                )
            )
        """
        
        results = []
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
                    results.append(row_dict)
        except Exception as e:
            print(f"Error getting recent behavior: {e}")
        
        return results
    
    def get_communication_fatigue(self, customer_id: str) -> Dict[str, Any]:
        """Check contact frequency and recent engagement"""
        query = f"""
            SELECT * FROM TABLE(
                cdp_platform.core.get_communication_fatigue(
                    '{self.tenant_id}',
                    '{customer_id}'
                )
            )
        """
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                row = response.result.data_array[0]
                return {columns[i]: row[i] for i in range(len(columns))}
        except Exception as e:
            print(f"Error getting communication fatigue: {e}")
        
        return {}
    
    def get_household_members(self, customer_id: str) -> List[Dict]:
        """Get all customers in same household"""
        query = f"""
            SELECT * FROM TABLE(
                cdp_platform.core.get_household_members(
                    '{self.tenant_id}',
                    '{customer_id}'
                )
            )
        """
        
        results = []
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
                    results.append(row_dict)
        except Exception as e:
            print(f"Error getting household members: {e}")
        
        return results
    
    def get_product_recommendations(self, customer_id: str, limit: int = 5) -> List[Dict]:
        """Get personalized product recommendations"""
        query = f"""
            SELECT * FROM TABLE(
                cdp_platform.core.get_product_recommendations(
                    '{self.tenant_id}',
                    '{customer_id}',
                    {limit}
                )
            )
        """
        
        results = []
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
                    results.append(row_dict)
        except Exception as e:
            print(f"Error getting product recommendations: {e}")
        
        return results


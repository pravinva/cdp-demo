"""
Agent tools - interfaces to Unity Catalog functions
"""

from ..dependencies import get_spark_session
from typing import Dict, List, Any
import json

class AgentTools:
    """Wrapper for UC functions as agent tools"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.spark = get_spark_session()
    
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
        
        result = self.spark.sql(query).toPandas().to_dict('records')
        
        if not result:
            return {"error": "Customer not found"}
        
        return result[0]
    
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
        
        return self.spark.sql(query).toPandas().to_dict('records')
    
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
        
        result = self.spark.sql(query).toPandas().to_dict('records')
        return result[0] if result else {}
    
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
        
        return self.spark.sql(query).toPandas().to_dict('records')
    
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
        
        return self.spark.sql(query).toPandas().to_dict('records')


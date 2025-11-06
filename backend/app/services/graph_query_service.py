"""
Graph Query Service - Relationship intelligence queries
"""

from typing import List, Dict, Optional
from pyspark.sql import SparkSession

from ..dependencies import get_spark_session


class GraphQueryService:
    """Service for querying identity graph and relationships"""
    
    def __init__(self, tenant_id: str, use_neptune: bool = False):
        self.tenant_id = tenant_id
        self.spark = get_spark_session()
        self.use_neptune = use_neptune
    
    def get_household_members(self, customer_id: str) -> List[Dict]:
        """Get all customers in same household"""
        result = self.spark.sql(f"""
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
        """).collect()
        
        return [row.asDict() for row in result]


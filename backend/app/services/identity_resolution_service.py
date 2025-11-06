"""
Identity Resolution Service
Processes clickstream events to resolve identities and create match groups
"""

from typing import List, Dict, Optional
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, collect_list, count, max as spark_max, min as spark_min
from datetime import datetime
import uuid

from ..dependencies import get_spark_session


class IdentityResolutionService:
    """
    Service for resolving customer identities from clickstream events
    Groups events by matching identity signals (email, phone, device, IP)
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.spark = get_spark_session()
    
    def run_identity_resolution(self, batch_size: int = 10000) -> Dict[str, int]:
        """
        Run identity resolution on recent clickstream events
        Creates/updates match groups based on identity signals
        """
        print(f"Running identity resolution for tenant: {self.tenant_id}")
        
        # Get recent events without match_id
        events_df = self.spark.sql(f"""
            SELECT *
            FROM cdp_platform.core.clickstream_events
            WHERE tenant_id = '{self.tenant_id}'
            AND match_id IS NULL
            ORDER BY event_timestamp DESC
            LIMIT {batch_size}
        """)
        
        if events_df.count() == 0:
            print("No unmatched events found")
            return {"processed": 0, "match_groups_created": 0}
        
        # Group events by identity signals
        # Strategy: Group by email, phone, or device fingerprint
        
        # 1. Group by email
        email_groups = events_df \
            .filter(col("email").isNotNull()) \
            .groupBy("email", "tenant_id") \
            .agg(
                collect_list("event_id").alias("event_ids"),
                collect_list("cookie_id").alias("cookie_ids"),
                collect_list("device_id").alias("device_ids"),
                collect_list("ip_address").alias("ip_addresses"),
                count("*").alias("event_count"),
                spark_min("event_timestamp").alias("first_seen"),
                spark_max("event_timestamp").alias("last_seen")
            )
        
        # Create match groups
        match_groups_data = []
        for row in email_groups.collect():
            match_id = f"match_{uuid.uuid4().hex[:8]}"
            
            # Get unique values
            cookie_ids = list(set([c for c in row['cookie_ids'] if c]))
            device_ids = list(set([d for d in row['device_ids'] if d]))
            ip_addresses = list(set([ip for ip in row['ip_addresses'] if ip]))
            
            match_groups_data.append({
                "match_id": match_id,
                "tenant_id": self.tenant_id,
                "known_emails": [row['email']],
                "known_phones": [],
                "known_login_ids": [],
                "shared_devices": device_ids[:10],  # Limit array size
                "shared_ips": ip_addresses[:10],
                "shared_addresses": [],
                "total_events": row['event_count'],
                "anonymous_events": 0,
                "known_events": row['event_count'],
                "unique_devices": len(device_ids),
                "unique_ips": len(ip_addresses),
                "is_household": False,
                "household_size": 1,
                "first_seen": row['first_seen'],
                "last_seen": row['last_seen'],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            # Update events with match_id
            self.spark.sql(f"""
                UPDATE cdp_platform.core.clickstream_events
                SET match_id = '{match_id}',
                    match_rule = 'email_match',
                    match_confidence = 0.9
                WHERE tenant_id = '{self.tenant_id}'
                AND email = '{row['email']}'
                AND match_id IS NULL
            """)
        
        # Insert match groups
        if match_groups_data:
            match_groups_df = self.spark.createDataFrame(match_groups_data)
            match_groups_df.write.format("delta").mode("append").saveAsTable("cdp_platform.core.match_groups")
        
        print(f"✓ Processed {events_df.count()} events")
        print(f"✓ Created {len(match_groups_data)} match groups")
        
        return {
            "processed": events_df.count(),
            "match_groups_created": len(match_groups_data)
        }
    
    def detect_households(self) -> int:
        """
        Detect households based on shared addresses, devices, IPs
        """
        # Simple household detection: customers with same address
        households = self.spark.sql(f"""
            SELECT 
                zip_code,
                COUNT(DISTINCT customer_id) as household_size,
                COLLECT_LIST(customer_id) as customer_ids
            FROM cdp_platform.core.customers
            WHERE tenant_id = '{self.tenant_id}'
            AND zip_code IS NOT NULL
            GROUP BY zip_code
            HAVING COUNT(DISTINCT customer_id) > 1
        """).collect()
        
        household_count = 0
        for household in households:
            household_id = f"household_{uuid.uuid4().hex[:8]}"
            customer_ids = household['customer_ids']
            
            # Update customers with household_id
            for customer_id in customer_ids:
                self.spark.sql(f"""
                    UPDATE cdp_platform.core.customers
                    SET household_id = '{household_id}',
                        household_role = 'member',
                        updated_at = current_timestamp()
                    WHERE tenant_id = '{self.tenant_id}'
                    AND customer_id = '{customer_id}'
                """)
            
            household_count += 1
        
        print(f"✓ Detected {household_count} households")
        return household_count


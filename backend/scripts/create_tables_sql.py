"""
Create tables using SQL Execution API
Fixes partition expressions and DEFAULT values for Delta Lake compatibility
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import sys
import os

# Add parent directory to path to import app config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.config import get_settings

settings = get_settings()

def get_sql_warehouse_id():
    """Get SQL warehouse ID from config or auto-detect"""
    if settings.SQL_WAREHOUSE_ID:
        return settings.SQL_WAREHOUSE_ID
    
    # Auto-detect: get first available warehouse
    w = WorkspaceClient()
    warehouses = list(w.warehouses.list())
    if warehouses:
        return warehouses[0].id
    return None

def create_tables_via_sql():
    """Create tables using SQL Execution API with Delta Lake compatible syntax"""
    
    w = WorkspaceClient()
    warehouse_id = get_sql_warehouse_id()
    
    if not warehouse_id:
        print("Error: No SQL warehouse found. Please set SQL_WAREHOUSE_ID in config.")
        return False
    
    print(f"Using SQL warehouse ID: {warehouse_id}")
    
    # Fixed SQL statements - compatible with Delta Lake
    tables_sql = {
        "clickstream_events": """
        CREATE TABLE IF NOT EXISTS cdp_platform.core.clickstream_events (
            event_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            login_id STRING,
            email STRING,
            phone STRING,
            user_agent STRING,
            device_family STRING,
            os_family STRING,
            browser_family STRING,
            ip_address STRING,
            session_id STRING,
            cookie_id STRING,
            device_id STRING,
            zip_code STRING,
            country STRING,
            city STRING,
            event_type STRING,
            page_url STRING,
            referrer_url STRING,
            event_timestamp TIMESTAMP,
            properties MAP<STRING, STRING>,
            match_id STRING,
            match_rule STRING,
            match_confidence DOUBLE,
            ingested_at TIMESTAMP
        )
        USING DELTA
        PARTITIONED BY (tenant_id, to_date(event_timestamp))
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        COMMENT 'Raw clickstream events with identity signals'
        """,
        "customers": """
        CREATE TABLE IF NOT EXISTS cdp_platform.core.customers (
            customer_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            match_id STRING,
            email STRING,
            phone STRING,
            first_name STRING,
            last_name STRING,
            date_of_birth DATE,
            gender STRING,
            street_address STRING,
            city STRING,
            state STRING,
            zip_code STRING,
            country STRING,
            household_id STRING,
            household_role STRING,
            segment STRING,
            lifecycle_stage STRING,
            lifetime_value DECIMAL(10,2),
            total_purchases INT,
            total_spend DECIMAL(10,2),
            avg_order_value DECIMAL(10,2),
            first_purchase_date TIMESTAMP,
            last_purchase_date TIMESTAMP,
            days_since_purchase INT,
            purchase_frequency DOUBLE,
            email_engagement_score DOUBLE,
            sms_engagement_score DOUBLE,
            push_engagement_score DOUBLE,
            last_engagement_date TIMESTAMP,
            churn_risk_score DOUBLE,
            purchase_propensity_score DOUBLE,
            upsell_propensity_score DOUBLE,
            preferred_channel STRING,
            preferred_language STRING,
            timezone STRING,
            email_consent BOOLEAN,
            sms_consent BOOLEAN,
            push_consent BOOLEAN,
            registered_devices ARRAY<STRUCT<device_id: STRING, device_family: STRING, last_seen: TIMESTAMP, push_token: STRING>>,
            product_categories_viewed ARRAY<STRING>,
            product_categories_purchased ARRAY<STRING>,
            favorite_products ARRAY<STRING>,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        USING DELTA
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.autoOptimize.optimizeWrite' = 'true'
        )
        COMMENT 'Customer golden records - unified profiles'
        """,
        "campaigns": """
        CREATE TABLE IF NOT EXISTS cdp_platform.core.campaigns (
            campaign_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            name STRING,
            description STRING,
            goal STRING,
            status STRING,
            target_segment STRING,
            audience_filter STRING,
            estimated_audience_size INT,
            agent_mode BOOLEAN,
            agent_instructions STRING,
            agent_model STRING,
            channels ARRAY<STRING>,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            customers_targeted INT,
            messages_sent INT,
            messages_delivered INT,
            messages_opened INT,
            messages_clicked INT,
            conversions INT,
            revenue_attributed DECIMAL(10,2),
            open_rate DOUBLE,
            click_rate DOUBLE,
            conversion_rate DOUBLE,
            total_cost DECIMAL(10,2),
            cost_per_send DECIMAL(6,4),
            cost_per_conversion DECIMAL(10,2),
            roas DOUBLE,
            created_by STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        USING DELTA
        TBLPROPERTIES (
            'delta.feature.allowColumnDefaults' = 'supported'
        )
        COMMENT 'Campaign definitions and performance metrics'
        """,
        "agent_decisions": """
        CREATE TABLE IF NOT EXISTS cdp_platform.core.agent_decisions (
            decision_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            campaign_id STRING,
            customer_id STRING,
            timestamp TIMESTAMP,
            action STRING,
            channel STRING,
            message_subject STRING,
            message_body STRING,
            reasoning_summary STRING,
            confidence_score DOUBLE,
            customer_segment STRING,
            churn_risk DOUBLE,
            model_version STRING,
            execution_time_ms INT,
            journey_id STRING,
            journey_step_id STRING,
            delivery_id STRING,
            created_at TIMESTAMP
        )
        USING DELTA
        PARTITIONED BY (tenant_id, to_date(timestamp))
        COMMENT 'AI agent decisions and reasoning'
        """,
        "deliveries": """
        CREATE TABLE IF NOT EXISTS cdp_platform.core.deliveries (
            delivery_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            decision_id STRING,
            customer_id STRING,
            campaign_id STRING,
            channel STRING,
            sent_at TIMESTAMP,
            to_address STRING,
            subject STRING,
            message_preview STRING,
            status STRING,
            delivered BOOLEAN,
            opened BOOLEAN,
            clicked BOOLEAN,
            converted BOOLEAN,
            cost_usd DECIMAL(6,4),
            created_at TIMESTAMP
        )
        USING DELTA
        PARTITIONED BY (tenant_id, to_date(sent_at))
        COMMENT 'Message delivery tracking and engagement metrics'
        """
    }
    
    print("\nCreating tables...")
    success_count = 0
    for table_name, sql in tables_sql.items():
        try:
            response = w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=sql.strip(),
                wait_timeout="30s"
            )
            if response.status.state == StatementState.SUCCEEDED:
                print(f"✓ Created table: {table_name}")
                success_count += 1
            else:
                print(f"✗ Table {table_name}: {response.status.state}")
                if hasattr(response.status, 'error'):
                    print(f"  Error: {response.status.error}")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg:
                print(f"✓ Table {table_name} already exists")
                success_count += 1
            else:
                print(f"✗ Error creating {table_name}: {e}")
    
    print(f"\n✓ Created {success_count}/{len(tables_sql)} tables")
    return success_count == len(tables_sql)

if __name__ == "__main__":
    create_tables_via_sql()


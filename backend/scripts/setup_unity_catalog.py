"""
Unity Catalog setup script
Creates catalog, schemas, and all tables for CDP platform
Run once during initial setup
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import *
import os

def setup_unity_catalog():
    """Create complete Unity Catalog structure"""
    
    w = WorkspaceClient()
    
    # Create catalog
    try:
        w.catalogs.create(name="cdp_platform", comment="Customer Data Platform")
        print("✓ Created catalog: cdp_platform")
    except Exception as e:
        print(f"Catalog exists or error: {e}")
    
    # Create schemas
    schemas = [
        ("core", "Core CDP tables"),
        ("staging", "Staging and temporary tables"),
        ("analytics", "Aggregated analytics tables"),
        ("ml", "ML models and feature tables")
    ]
    
    for schema_name, comment in schemas:
        try:
            w.schemas.create(
                catalog_name="cdp_platform",
                name=schema_name,
                comment=comment
            )
            print(f"✓ Created schema: {schema_name}")
        except Exception as e:
            print(f"Schema {schema_name} exists or error: {e}")

def create_tables(spark):
    """Create all core tables with proper schemas"""
    
    # 1. Clickstream Events Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.clickstream_events (
            event_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            
            -- Identity signals (nullable for anonymous)
            login_id STRING,
            email STRING,
            phone STRING,
            
            -- Device fingerprinting
            user_agent STRING,
            device_family STRING,
            os_family STRING,
            browser_family STRING,
            
            -- Network
            ip_address STRING,
            
            -- Session
            session_id STRING,
            cookie_id STRING,
            device_id STRING,
            
            -- Location
            zip_code STRING,
            country STRING,
            city STRING,
            
            -- Event details
            event_type STRING,
            page_url STRING,
            referrer_url STRING,
            event_timestamp TIMESTAMP,
            
            -- Properties (flexible)
            properties MAP<STRING, STRING>,
            
            -- Match group (populated by identity resolution)
            match_id STRING,
            match_rule STRING,
            match_confidence DOUBLE,
            
            -- System
            ingested_at TIMESTAMP,
            
            CONSTRAINT pk_events PRIMARY KEY (tenant_id, event_id)
        )
        USING DELTA
        PARTITIONED BY (tenant_id, DATE(event_timestamp))
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        COMMENT 'Raw clickstream events with identity signals'
    """)
    print("✓ Created table: clickstream_events")
    
    # 2. Match Groups Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.match_groups (
            match_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            
            -- Consolidated identity signals
            known_emails ARRAY<STRING>,
            known_phones ARRAY<STRING>,
            known_login_ids ARRAY<STRING>,
            
            -- Shared attributes (for household detection)
            shared_devices ARRAY<STRING>,
            shared_ips ARRAY<STRING>,
            shared_addresses ARRAY<STRING>,
            
            -- Counts
            total_events INT,
            anonymous_events INT,
            known_events INT,
            unique_devices INT,
            unique_ips INT,
            
            -- Classification
            is_household BOOLEAN,
            household_size INT,
            
            -- Metadata
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            
            CONSTRAINT pk_match_groups PRIMARY KEY (tenant_id, match_id)
        )
        USING DELTA
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true'
        )
        COMMENT 'Identity resolution output - consolidated match groups'
    """)
    print("✓ Created table: match_groups")
    
    # 3. Customers Table (Golden Records)
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.customers (
            customer_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            match_id STRING,
            
            -- Profile
            email STRING,
            phone STRING,
            first_name STRING,
            last_name STRING,
            date_of_birth DATE,
            gender STRING,
            
            -- Address
            street_address STRING,
            city STRING,
            state STRING,
            zip_code STRING,
            country STRING,
            
            -- Household context
            household_id STRING,
            household_role STRING,
            
            -- Segmentation
            segment STRING,
            lifecycle_stage STRING,
            
            -- Metrics (computed)
            lifetime_value DECIMAL(10,2),
            total_purchases INT,
            total_spend DECIMAL(10,2),
            avg_order_value DECIMAL(10,2),
            first_purchase_date TIMESTAMP,
            last_purchase_date TIMESTAMP,
            days_since_purchase INT,
            purchase_frequency DOUBLE,
            
            -- Engagement
            email_engagement_score DOUBLE,
            sms_engagement_score DOUBLE,
            push_engagement_score DOUBLE,
            last_engagement_date TIMESTAMP,
            
            -- ML Scores
            churn_risk_score DOUBLE,
            purchase_propensity_score DOUBLE,
            upsell_propensity_score DOUBLE,
            
            -- Preferences
            preferred_channel STRING,
            preferred_language STRING,
            timezone STRING,
            
            -- Consent
            email_consent BOOLEAN,
            sms_consent BOOLEAN,
            push_consent BOOLEAN,
            
            -- Device inventory
            registered_devices ARRAY<STRUCT<
                device_id: STRING,
                device_family: STRING,
                last_seen: TIMESTAMP,
                push_token: STRING
            >>,
            
            -- Behavioral
            product_categories_viewed ARRAY<STRING>,
            product_categories_purchased ARRAY<STRING>,
            favorite_products ARRAY<STRING>,
            
            -- System
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            
            CONSTRAINT pk_customers PRIMARY KEY (tenant_id, customer_id)
        )
        USING DELTA
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.autoOptimize.optimizeWrite' = 'true'
        )
        COMMENT 'Customer golden records - unified profiles'
    """)
    print("✓ Created table: customers")
    
    # 4. Identity Graph Edges Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.identity_graph_edges (
            edge_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            
            from_entity_type STRING,
            from_entity_id STRING,
            
            to_entity_type STRING,
            to_entity_id STRING,
            
            relationship_type STRING,
            
            -- Metadata
            strength DOUBLE,
            evidence_count INT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            
            CONSTRAINT pk_edges PRIMARY KEY (tenant_id, edge_id)
        )
        USING DELTA
        PARTITIONED BY (tenant_id, relationship_type)
        COMMENT 'Identity graph relationships for household/network analysis'
    """)
    print("✓ Created table: identity_graph_edges")
    
    # 5. Campaigns Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.campaigns (
            campaign_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            
            name STRING,
            description STRING,
            goal STRING,
            status STRING,
            
            -- Targeting
            target_segment STRING,
            audience_filter STRING,
            estimated_audience_size INT,
            
            -- Agent configuration
            agent_mode BOOLEAN DEFAULT TRUE,
            agent_instructions STRING,
            agent_model STRING,
            
            -- Activation
            channels ARRAY<STRING>,
            
            -- Schedule
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            
            -- Metrics
            customers_targeted INT,
            messages_sent INT,
            messages_delivered INT,
            messages_opened INT,
            messages_clicked INT,
            conversions INT,
            revenue_attributed DECIMAL(10,2),
            
            -- Rates (computed)
            open_rate DOUBLE,
            click_rate DOUBLE,
            conversion_rate DOUBLE,
            
            -- Costs
            total_cost DECIMAL(10,2),
            cost_per_send DECIMAL(6,4),
            cost_per_conversion DECIMAL(10,2),
            roas DOUBLE,
            
            -- System
            created_by STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            
            CONSTRAINT pk_campaigns PRIMARY KEY (tenant_id, campaign_id)
        )
        USING DELTA
        COMMENT 'Campaign definitions and performance metrics'
    """)
    print("✓ Created table: campaigns")
    
    # 6. Agent Decisions Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.agent_decisions (
            decision_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            campaign_id STRING,
            customer_id STRING,
            
            timestamp TIMESTAMP,
            
            -- Decision
            action STRING,
            channel STRING,
            scheduled_send_time TIMESTAMP,
            
            -- Generated content
            message_subject STRING,
            message_body STRING,
            call_to_action STRING,
            
            -- Reasoning
            reasoning_summary STRING,
            reasoning_details STRING,
            tool_calls ARRAY<STRUCT<
                tool_name: STRING,
                parameters: STRING,
                result: STRING
            >>,
            confidence_score DOUBLE,
            
            -- Context used
            customer_segment STRING,
            churn_risk DOUBLE,
            ltv DOUBLE,
            days_since_last_contact INT,
            household_context STRING,
            
            -- Outcome (populated after delivery)
            delivery_id STRING,
            delivered BOOLEAN,
            opened BOOLEAN,
            clicked BOOLEAN,
            converted BOOLEAN,
            conversion_value DECIMAL(10,2),
            
            -- System
            model_version STRING,
            execution_time_ms INT,
            
            CONSTRAINT pk_decisions PRIMARY KEY (tenant_id, decision_id)
        )
        USING DELTA
        PARTITIONED BY (tenant_id, DATE(timestamp))
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true'
        )
        COMMENT 'Agent decision audit trail with full reasoning'
    """)
    print("✓ Created table: agent_decisions")
    
    # 7. Deliveries Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.deliveries (
            delivery_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            decision_id STRING,
            customer_id STRING,
            campaign_id STRING,
            
            channel STRING,
            sent_at TIMESTAMP,
            
            -- Recipient
            to_address STRING,
            
            -- Content
            subject STRING,
            message_preview STRING,
            
            -- Status
            status STRING,
            provider_message_id STRING,
            error_message STRING,
            
            -- Engagement
            delivered_at TIMESTAMP,
            opened_at TIMESTAMP,
            clicked_at TIMESTAMP,
            converted_at TIMESTAMP,
            conversion_value DECIMAL(10,2),
            
            -- Cost
            cost_usd DECIMAL(6,4),
            
            CONSTRAINT pk_deliveries PRIMARY KEY (tenant_id, delivery_id)
        )
        USING DELTA
        PARTITIONED BY (tenant_id, DATE(sent_at))
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true'
        )
        COMMENT 'Message deliveries and engagement tracking'
    """)
    print("✓ Created table: deliveries")
    
    # 8. Scheduled Deliveries Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.scheduled_deliveries (
            delivery_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            
            channel STRING,
            scheduled_time TIMESTAMP,
            
            payload STRING,
            
            status STRING,
            processed_at TIMESTAMP,
            error_message STRING,
            
            CONSTRAINT pk_scheduled PRIMARY KEY (tenant_id, delivery_id)
        )
        USING DELTA
        COMMENT 'Queue for scheduled message deliveries'
    """)
    print("✓ Created table: scheduled_deliveries")
    
    # 9. Journey Definitions Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.journey_definitions (
            journey_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            name STRING,
            description STRING,
            definition_json STRING,
            status STRING,
            created_by STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            
            CONSTRAINT pk_journeys PRIMARY KEY (tenant_id, journey_id)
        )
        USING DELTA
        COMMENT 'Journey definitions with JSON state machine configuration'
    """)
    print("✓ Created table: journey_definitions")
    
    # 10. Customer Journey States Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.customer_journey_states (
            state_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            customer_id STRING,
            journey_id STRING,
            current_step_id STRING,
            status STRING,
            waiting_for STRING,
            wait_until TIMESTAMP,
            steps_completed ARRAY<STRING>,
            actions_taken STRING,
            entered_at TIMESTAMP,
            last_action_at TIMESTAMP,
            completed_at TIMESTAMP,
            exit_reason STRING,
            
            CONSTRAINT pk_journey_states PRIMARY KEY (tenant_id, state_id)
        )
        USING DELTA
        PARTITIONED BY (tenant_id, journey_id)
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true'
        )
        COMMENT 'Individual customer journey state tracking'
    """)
    print("✓ Created table: customer_journey_states")
    
    # 11. Journey Analytics Table
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.core.journey_analytics (
            journey_id STRING,
            tenant_id STRING,
            step_id STRING,
            customers_entered INT,
            customers_completed INT,
            customers_dropped INT,
            avg_time_in_step_hours DOUBLE,
            conversion_rate DOUBLE,
            date DATE
        )
        USING DELTA
        PARTITIONED BY (tenant_id, date)
        COMMENT 'Journey performance analytics'
    """)
    print("✓ Created table: journey_analytics")
    
    # 12. Customer Features Table (for ML)
    spark.sql("""
        CREATE TABLE IF NOT EXISTS cdp_platform.ml.customer_features (
            customer_id STRING NOT NULL,
            tenant_id STRING NOT NULL,
            
            -- Feature vector (for embedding lookups)
            feature_vector MAP<STRING, DOUBLE>,
            
            -- Recommendations
            product_recommendations ARRAY<STRING>,
            content_recommendations ARRAY<STRING>,
            
            -- Scores
            churn_risk_score DOUBLE,
            ltv_prediction DOUBLE,
            purchase_propensity_score DOUBLE,
            
            -- Preferences
            preferred_category STRING,
            preferred_price_range STRING,
            
            -- Computed at
            last_updated TIMESTAMP,
            
            CONSTRAINT pk_features PRIMARY KEY (tenant_id, customer_id)
        )
        USING DELTA
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true'
        )
        COMMENT 'Precomputed customer features for real-time serving'
    """)
    print("✓ Created table: customer_features")
    
    print("\n✓ All tables created successfully!")

if __name__ == "__main__":
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder \
        .appName("CDP Setup") \
        .getOrCreate()
    
    setup_unity_catalog()
    create_tables(spark)


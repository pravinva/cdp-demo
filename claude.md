# Databricks Customer Intelligence Platform - Implementation Guide

**Version:** 1.0  
**Target:** Claude Code AI Agent  
**Quality Level:** Enterprise Production-Ready  
**Estimated Timeline:** 8-10 hours for MVP

---

## PROJECT OVERVIEW

**What We're Building:**
A native Databricks Customer Intelligence Platform (CDP) with identity resolution, relationship intelligence, agentic AI activation, and multi-channel orchestration. This is a complete, production-ready application that runs on customer's Databricks lakehouse.

**Core Value Propositions:**
1. **Native to Lakehouse** - All data in Unity Catalog, zero data movement
2. **Agentic AI** - Autonomous agents that analyze each customer and execute personalized campaigns
3. **Relationship Intelligence** - Graph-based household/network understanding
4. **Multi-Channel Activation** - Email, SMS, Push, Ads, Real-time web
5. **Complete Governance** - Full audit trail, explainable AI, compliance-ready

**Technology Stack:**
- **Backend:** FastAPI, Python 3.10+, PySpark, Databricks SDK
- **Frontend:** React 18+, TypeScript, Material-UI, Recharts
- **Data:** Delta Lake, Unity Catalog, Delta Live Tables
- **AI/ML:** Databricks Agent Framework, MLflow, Foundation Model APIs
- **Infrastructure:** Databricks Apps, Serverless Compute

---

## ARCHITECTURE OVERVIEW

```
┌────────────────────────────────────────────────────────┐
│  FRONTEND (React + TypeScript)                         │
│  /cdp-platform-ui/                                     │
│  ├─ Customer 360 Explorer                              │
│  ├─ Campaign Management                                │
│  ├─ Identity Graph Viewer                              │
│  ├─ Agent Insights Dashboard                           │
│  └─ Activation Center                                  │
└────────────────────┬───────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────┐
│  BACKEND API (FastAPI)                                 │
│  /cdp-platform-backend/                                │
│  ├─ REST APIs (customers, campaigns, analytics)        │
│  ├─ Agent Orchestration Service                        │
│  ├─ Identity Resolution Service                        │
│  ├─ Activation Service (multi-channel)                 │
│  └─ Graph Query Service                                │
└────────────────────┬───────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────┐
│  INTELLIGENCE LAYER                                     │
│  ├─ Databricks Agent Framework                         │
│  ├─ MLflow (Tracking, Registry, Serving)              │
│  └─ Foundation Model APIs                              │
└────────────────────┬───────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────┐
│  DATA LAYER (Unity Catalog)                            │
│  cdp_platform catalog                                  │
│  ├─ customers (unified profiles)                       │
│  ├─ clickstream_events (anonymous + known)            │
│  ├─ match_groups (identity resolution output)         │
│  ├─ identity_graph_edges (relationships)              │
│  ├─ campaigns (configuration)                          │
│  ├─ agent_decisions (audit trail)                     │
│  └─ deliveries (engagement tracking)                  │
└────────────────────────────────────────────────────────┘
```

---

## PROJECT STRUCTURE

Create this exact directory structure:

```
databricks-cdp-platform/
├── README.md
├── .gitignore
├── requirements.txt
├── setup.py
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app entry point
│   │   ├── config.py                    # Configuration management
│   │   ├── dependencies.py              # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── customers.py             # Customer CRUD APIs
│   │   │   ├── campaigns.py             # Campaign management APIs
│   │   │   ├── agents.py                # Agent execution APIs
│   │   │   ├── analytics.py             # Dashboard data APIs
│   │   │   └── identity.py              # Identity resolution APIs
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── identity_resolution_service.py
│   │   │   ├── agent_service.py         # Core agent orchestration
│   │   │   ├── activation_service.py    # Multi-channel activation
│   │   │   ├── graph_query_service.py   # Relationship queries
│   │   │   └── feature_service.py       # Feature computation
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── marketing_agent.py       # Main agent implementation
│   │   │   ├── tools.py                 # Agent tools (UC functions)
│   │   │   └── prompts.py               # System prompts
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── customer.py              # Pydantic models
│   │   │   ├── campaign.py
│   │   │   ├── decision.py
│   │   │   └── delivery.py
│   │   │
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── email_providers.py       # SendGrid, SES
│   │   │   ├── sms_providers.py         # Twilio, SNS
│   │   │   ├── push_providers.py        # Firebase, OneSignal
│   │   │   └── ad_platforms.py          # Meta, Google, LinkedIn
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── databricks_utils.py      # DB SDK helpers
│   │       ├── security.py              # Auth, encryption
│   │       └── monitoring.py            # Logging, metrics
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   ├── test_agents/
│   │   └── fixtures/
│   │
│   ├── scripts/
│   │   ├── setup_unity_catalog.py       # Create schemas, tables
│   │   ├── create_uc_functions.sql      # Agent tool functions
│   │   ├── seed_demo_data.py            # Generate sample data
│   │   └── run_identity_resolution.py   # Batch processing
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── pages/
│   │   │   ├── CustomersPage.tsx        # Customer list/search
│   │   │   ├── CustomerDetailPage.tsx   # Customer 360 view
│   │   │   ├── CampaignsPage.tsx        # Campaign list
│   │   │   ├── CampaignBuilderPage.tsx  # Create campaign
│   │   │   ├── IdentityGraphPage.tsx    # Graph visualization
│   │   │   ├── AgentInsightsPage.tsx    # Agent dashboard
│   │   │   ├── ActivationCenterPage.tsx # Activation UI
│   │   │   └── AnalyticsPage.tsx        # Overall analytics
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   │
│   │   │   ├── customers/
│   │   │   │   ├── CustomerCard.tsx
│   │   │   │   ├── CustomerTimeline.tsx
│   │   │   │   ├── CustomerSegmentBadge.tsx
│   │   │   │   └── ChurnRiskIndicator.tsx
│   │   │   │
│   │   │   ├── campaigns/
│   │   │   │   ├── CampaignCard.tsx
│   │   │   │   ├── CampaignStatus.tsx
│   │   │   │   ├── AudienceBuilder.tsx
│   │   │   │   └── AgentConfigPanel.tsx
│   │   │   │
│   │   │   ├── agent/
│   │   │   │   ├── AgentDecisionCard.tsx
│   │   │   │   ├── AgentReasoningPanel.tsx
│   │   │   │   ├── AgentTraceViewer.tsx
│   │   │   │   └── AgentPerformanceMetrics.tsx
│   │   │   │
│   │   │   ├── identity/
│   │   │   │   ├── IdentityGraphViewer.tsx
│   │   │   │   ├── MatchGroupCard.tsx
│   │   │   │   └── HouseholdPanel.tsx
│   │   │   │
│   │   │   └── shared/
│   │   │       ├── MetricCard.tsx
│   │   │       ├── DataTable.tsx
│   │   │       ├── LoadingSpinner.tsx
│   │   │       └── ErrorBoundary.tsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                   # API client
│   │   │   ├── customers.ts
│   │   │   ├── campaigns.ts
│   │   │   ├── agents.ts
│   │   │   └── analytics.ts
│   │   │
│   │   ├── hooks/
│   │   │   ├── useCustomers.ts
│   │   │   ├── useCampaigns.ts
│   │   │   ├── useAgentDecisions.ts
│   │   │   └── useAnalytics.ts
│   │   │
│   │   ├── theme/
│   │   │   └── databricksTheme.ts       # Material-UI theme
│   │   │
│   │   ├── types/
│   │   │   ├── customer.ts
│   │   │   ├── campaign.ts
│   │   │   └── agent.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── routes.tsx
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
│
├── infrastructure/
│   ├── databricks/
│   │   ├── workflows/
│   │   │   ├── identity_resolution.yml
│   │   │   ├── scheduled_deliveries.yml
│   │   │   └── feature_sync.yml
│   │   │
│   │   └── apps/
│   │       └── cdp-platform-app.yml
│   │
│   └── terraform/                       # Optional IaC
│       ├── main.tf
│       └── variables.tf
│
├── docs/
│   ├── api/
│   │   └── openapi.yaml
│   ├── architecture/
│   │   ├── data-model.md
│   │   ├── agent-architecture.md
│   │   └── security.md
│   └── user-guides/
│       ├── getting-started.md
│       ├── campaign-creation.md
│       └── identity-resolution.md
│
└── .github/
    └── workflows/
        ├── backend-tests.yml
        └── frontend-tests.yml
```

---

## PHASE 1: DATA FOUNDATION

### 1.1 Unity Catalog Setup

**File:** `backend/scripts/setup_unity_catalog.py`

```python
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
    
    # 9. Customer Features Table (for ML)
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
```

### 1.2 Unity Catalog Functions (Agent Tools)

**File:** `backend/scripts/create_uc_functions.sql`

```sql
-- Unity Catalog Functions for Agent Tools
-- These functions provide clean interfaces for agents to query customer data

USE CATALOG cdp_platform;
USE SCHEMA core;

-- Function: Get complete customer context
CREATE OR REPLACE FUNCTION get_customer_context(
  p_tenant_id STRING,
  p_customer_id STRING
)
RETURNS TABLE(
  customer_id STRING,
  email STRING,
  first_name STRING,
  last_name STRING,
  segment STRING,
  lifetime_value DECIMAL(10,2),
  total_purchases INT,
  days_since_purchase INT,
  churn_risk_score DOUBLE,
  purchase_propensity_score DOUBLE,
  email_engagement_score DOUBLE,
  preferred_channel STRING,
  household_id STRING,
  is_in_household BOOLEAN,
  events_last_7d INT,
  messages_last_7d INT,
  last_message_date TIMESTAMP
)
COMMENT 'Agent tool: Get complete customer context for decision making'
RETURN 
  SELECT 
    c.customer_id,
    c.email,
    c.first_name,
    c.last_name,
    c.segment,
    c.lifetime_value,
    c.total_purchases,
    c.days_since_purchase,
    c.churn_risk_score,
    c.purchase_propensity_score,
    c.email_engagement_score,
    c.preferred_channel,
    c.household_id,
    c.household_id IS NOT NULL as is_in_household,
    
    -- Recent activity
    (SELECT COUNT(*) FROM cdp_platform.core.clickstream_events e 
     WHERE e.tenant_id = c.tenant_id
     AND e.match_id = c.match_id
     AND e.event_timestamp >= current_timestamp() - INTERVAL 7 DAY) as events_last_7d,
    
    -- Communication frequency
    (SELECT COUNT(*) FROM cdp_platform.core.deliveries d
     WHERE d.tenant_id = c.tenant_id
     AND d.customer_id = c.customer_id
     AND d.sent_at >= current_timestamp() - INTERVAL 7 DAY) as messages_last_7d,
    
    (SELECT MAX(sent_at) FROM cdp_platform.core.deliveries d
     WHERE d.tenant_id = c.tenant_id
     AND d.customer_id = c.customer_id) as last_message_date
    
  FROM cdp_platform.core.customers c
  WHERE c.tenant_id = p_tenant_id
  AND c.customer_id = p_customer_id;

-- Function: Get recent behavior events
CREATE OR REPLACE FUNCTION get_recent_behavior(
  p_tenant_id STRING,
  p_customer_id STRING,
  p_days INT
)
RETURNS TABLE(
  event_type STRING,
  event_timestamp TIMESTAMP,
  page_url STRING,
  product_id STRING,
  channel STRING
)
COMMENT 'Agent tool: Get customer events from last N days'
RETURN
  SELECT 
    e.event_type,
    e.event_timestamp,
    e.page_url,
    e.properties['product_id'] as product_id,
    e.properties['channel'] as channel
  FROM cdp_platform.core.clickstream_events e
  INNER JOIN cdp_platform.core.customers c 
    ON e.tenant_id = c.tenant_id AND e.match_id = c.match_id
  WHERE e.tenant_id = p_tenant_id
  AND c.customer_id = p_customer_id
  AND e.event_timestamp >= current_timestamp() - INTERVAL p_days DAY
  ORDER BY e.event_timestamp DESC
  LIMIT 100;

-- Function: Check communication fatigue
CREATE OR REPLACE FUNCTION get_communication_fatigue(
  p_tenant_id STRING,
  p_customer_id STRING
)
RETURNS TABLE(
  messages_last_7d INT,
  messages_last_30d INT,
  open_rate_7d DOUBLE,
  open_rate_30d DOUBLE,
  last_contact_days INT,
  is_fatigued BOOLEAN
)
COMMENT 'Agent tool: Check contact frequency and engagement'
RETURN
  SELECT 
    COUNT(CASE WHEN sent_at >= current_timestamp() - INTERVAL 7 DAY THEN 1 END) as messages_last_7d,
    COUNT(CASE WHEN sent_at >= current_timestamp() - INTERVAL 30 DAY THEN 1 END) as messages_last_30d,
    
    AVG(CASE 
      WHEN sent_at >= current_timestamp() - INTERVAL 7 DAY 
      THEN CAST(opened AS INT) 
    END) as open_rate_7d,
    
    AVG(CASE 
      WHEN sent_at >= current_timestamp() - INTERVAL 30 DAY 
      THEN CAST(opened AS INT) 
    END) as open_rate_30d,
    
    DATEDIFF(current_date(), MAX(sent_at)) as last_contact_days,
    
    -- Fatigue heuristic: >3 messages in 7 days OR >10 in 30 days
    (COUNT(CASE WHEN sent_at >= current_timestamp() - INTERVAL 7 DAY THEN 1 END) > 3
     OR COUNT(CASE WHEN sent_at >= current_timestamp() - INTERVAL 30 DAY THEN 1 END) > 10) as is_fatigued
     
  FROM cdp_platform.core.deliveries
  WHERE tenant_id = p_tenant_id
  AND customer_id = p_customer_id;

-- Function: Get household members
CREATE OR REPLACE FUNCTION get_household_members(
  p_tenant_id STRING,
  p_customer_id STRING
)
RETURNS TABLE(
  member_customer_id STRING,
  member_name STRING,
  member_email STRING,
  relationship_type STRING,
  last_contact_date TIMESTAMP
)
COMMENT 'Agent tool: Get all customers in same household'
RETURN
  SELECT 
    c2.customer_id as member_customer_id,
    CONCAT(c2.first_name, ' ', c2.last_name) as member_name,
    c2.email as member_email,
    'household_member' as relationship_type,
    
    (SELECT MAX(sent_at) FROM cdp_platform.core.deliveries d
     WHERE d.customer_id = c2.customer_id
     AND d.tenant_id = p_tenant_id) as last_contact_date
     
  FROM cdp_platform.core.customers c1
  INNER JOIN cdp_platform.core.customers c2
    ON c1.household_id = c2.household_id
    AND c1.tenant_id = c2.tenant_id
  WHERE c1.tenant_id = p_tenant_id
  AND c1.customer_id = p_customer_id
  AND c2.customer_id != p_customer_id
  AND c1.household_id IS NOT NULL;

-- Function: Get product recommendations
CREATE OR REPLACE FUNCTION get_product_recommendations(
  p_tenant_id STRING,
  p_customer_id STRING,
  p_limit INT
)
RETURNS TABLE(
  product_id STRING,
  score DOUBLE,
  reason STRING
)
COMMENT 'Agent tool: Get personalized product recommendations'
RETURN
  SELECT 
    product_id,
    score,
    reason
  FROM cdp_platform.ml.customer_features cf
  LATERAL VIEW EXPLODE(cf.product_recommendations) t AS product_id
  -- Note: This is simplified. Real implementation would join with product catalog
  -- and compute collaborative filtering scores
  WHERE cf.tenant_id = p_tenant_id
  AND cf.customer_id = p_customer_id
  LIMIT p_limit;

-- Function: Get anonymous journey
CREATE OR REPLACE FUNCTION get_anonymous_journey(
  p_tenant_id STRING,
  p_customer_id STRING
)
RETURNS TABLE(
  event_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP,
  page_url STRING,
  session_type STRING
)
COMMENT 'Agent tool: Show anonymous events before customer logged in'
RETURN
  SELECT 
    e.event_id,
    e.event_type,
    e.event_timestamp,
    e.page_url,
    CASE 
      WHEN e.login_id IS NULL THEN 'Anonymous'
      ELSE 'Known'
    END as session_type
  FROM cdp_platform.core.clickstream_events e
  INNER JOIN cdp_platform.core.customers c
    ON e.tenant_id = c.tenant_id AND e.match_id = c.match_id
  WHERE e.tenant_id = p_tenant_id
  AND c.customer_id = p_customer_id
  ORDER BY e.event_timestamp ASC;

-- Function: Get similar customers (for collaborative filtering)
CREATE OR REPLACE FUNCTION get_similar_customers(
  p_tenant_id STRING,
  p_customer_id STRING,
  p_limit INT
)
RETURNS TABLE(
  similar_customer_id STRING,
  similarity_score DOUBLE,
  common_behaviors INT
)
COMMENT 'Agent tool: Find similar customers for recommendations'
RETURN
  -- Simplified: In production, use embedding similarity or collaborative filtering
  SELECT 
    c2.customer_id as similar_customer_id,
    0.8 as similarity_score,  -- Placeholder
    10 as common_behaviors    -- Placeholder
  FROM cdp_platform.core.customers c1
  INNER JOIN cdp_platform.core.customers c2
    ON c1.tenant_id = c2.tenant_id
    AND c1.segment = c2.segment
    AND c2.customer_id != c1.customer_id
  WHERE c1.tenant_id = p_tenant_id
  AND c1.customer_id = p_customer_id
  LIMIT p_limit;

-- Grant permissions (adjust as needed)
-- GRANT EXECUTE ON FUNCTION get_customer_context TO `cdp_app_role`;
-- GRANT EXECUTE ON FUNCTION get_recent_behavior TO `cdp_app_role`;
-- ... etc
```

### 1.3 Sample Data Generator

**File:** `backend/scripts/seed_demo_data.py`

```python
"""
Generate realistic demo data for CDP platform
Creates customers, events, campaigns, decisions for testing
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime, timedelta
import random
import uuid

def generate_demo_data(spark, tenant_id="demo_tenant", num_customers=100):
    """Generate realistic demo data"""
    
    print(f"Generating demo data for tenant: {tenant_id}")
    
    # 1. Generate Customers
    print("Generating customers...")
    
    segments = ["VIP", "Active", "AtRisk", "Dormant"]
    channels = ["email", "sms", "push"]
    
    customers_data = []
    for i in range(num_customers):
        customer_id = f"cust_{uuid.uuid4().hex[:8]}"
        segment = random.choices(segments, weights=[10, 40, 30, 20])[0]
        
        # Segment-based attributes
        if segment == "VIP":
            ltv = random.randint(5000, 20000)
            purchases = random.randint(20, 100)
            churn_risk = random.uniform(0.1, 0.3)
        elif segment == "Active":
            ltv = random.randint(500, 5000)
            purchases = random.randint(5, 20)
            churn_risk = random.uniform(0.2, 0.4)
        elif segment == "AtRisk":
            ltv = random.randint(300, 2000)
            purchases = random.randint(2, 10)
            churn_risk = random.uniform(0.6, 0.8)
        else:  # Dormant
            ltv = random.randint(100, 500)
            purchases = random.randint(1, 3)
            churn_risk = random.uniform(0.8, 0.95)
        
        customers_data.append({
            "customer_id": customer_id,
            "tenant_id": tenant_id,
            "email": f"customer{i}@example.com",
            "phone": f"+1555{i:07d}",
            "first_name": f"Customer{i}",
            "last_name": f"Demo{i}",
            "segment": segment,
            "lifetime_value": ltv,
            "total_purchases": purchases,
            "avg_order_value": ltv / purchases if purchases > 0 else 0,
            "days_since_purchase": random.randint(1, 180) if segment != "Dormant" else random.randint(60, 365),
            "churn_risk_score": churn_risk,
            "purchase_propensity_score": random.uniform(0.3, 0.9),
            "email_engagement_score": random.uniform(0.4, 0.9),
            "preferred_channel": random.choice(channels),
            "email_consent": True,
            "sms_consent": random.choice([True, False]),
            "push_consent": random.choice([True, False]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
    
    customers_df = spark.createDataFrame(customers_data)
    customers_df.write.format("delta").mode("overwrite").saveAsTable("cdp_platform.core.customers")
    print(f"✓ Created {num_customers} customers")
    
    # 2. Generate Clickstream Events
    print("Generating clickstream events...")
    
    event_types = ["page_view", "product_view", "cart_add", "cart_remove", "purchase", "search"]
    events_data = []
    
    for customer in customers_data:
        # Generate 5-50 events per customer
        num_events = random.randint(5, 50)
        
        for j in range(num_events):
            event_id = f"evt_{uuid.uuid4().hex}"
            event_timestamp = datetime.now() - timedelta(days=random.randint(0, 90))
            
            # Some events are anonymous (no login_id)
            is_anonymous = j < num_events * 0.3  # 30% anonymous
            
            events_data.append({
                "event_id": event_id,
                "tenant_id": tenant_id,
                "login_id": None if is_anonymous else customer["customer_id"],
                "email": None if is_anonymous else customer["email"],
                "cookie_id": f"cookie_{customer['customer_id']}",
                "session_id": f"session_{uuid.uuid4().hex[:8]}",
                "event_type": random.choice(event_types),
                "event_timestamp": event_timestamp,
                "page_url": f"/products/{random.randint(1, 100)}",
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "device_family": random.choice(["Desktop", "Mobile", "Tablet"]),
                "ingested_at": datetime.now()
            })
    
    events_df = spark.createDataFrame(events_data)
    events_df.write.format("delta").mode("overwrite").saveAsTable("cdp_platform.core.clickstream_events")
    print(f"✓ Created {len(events_data)} events")
    
    # 3. Generate Sample Campaign
    print("Generating sample campaign...")
    
    campaign_data = [{
        "campaign_id": f"camp_{uuid.uuid4().hex[:8]}",
        "tenant_id": tenant_id,
        "name": "Q4 Retention Campaign",
        "description": "Re-engage at-risk customers",
        "goal": "retention",
        "status": "active",
        "agent_mode": True,
        "agent_instructions": "Focus on personalized offers based on past purchases",
        "channels": ["email", "sms"],
        "start_date": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }]
    
    campaign_df = spark.createDataFrame(campaign_data)
    campaign_df.write.format("delta").mode("append").saveAsTable("cdp_platform.core.campaigns")
    print("✓ Created sample campaign")
    
    # 4. Generate Sample Agent Decisions
    print("Generating agent decisions...")
    
    decisions_data = []
    for customer in customers_data[:20]:  # First 20 customers
        decision_id = f"dec_{uuid.uuid4().hex}"
        
        # Agent decides based on segment
        if customer["segment"] == "AtRisk":
            action = "contact"
            channel = "email"
            subject = f"We miss you, {customer['first_name']}! Here's 20% off"
            body = f"Hi {customer['first_name']}, we noticed you haven't shopped recently..."
            reasoning = "Customer shows high churn risk but good historical engagement"
        else:
            action = "skip"
            channel = None
            subject = None
            body = None
            reasoning = "Customer recently contacted, avoiding fatigue"
        
        decisions_data.append({
            "decision_id": decision_id,
            "tenant_id": tenant_id,
            "campaign_id": campaign_data[0]["campaign_id"],
            "customer_id": customer["customer_id"],
            "timestamp": datetime.now(),
            "action": action,
            "channel": channel,
            "message_subject": subject,
            "message_body": body,
            "reasoning_summary": reasoning,
            "confidence_score": random.uniform(0.7, 0.95),
            "customer_segment": customer["segment"],
            "churn_risk": customer["churn_risk_score"],
            "model_version": "v1.0",
            "execution_time_ms": random.randint(800, 2000)
        })
    
    decisions_df = spark.createDataFrame(decisions_data)
    decisions_df.write.format("delta").mode("append").saveAsTable("cdp_platform.core.agent_decisions")
    print(f"✓ Created {len(decisions_data)} agent decisions")
    
    print("\n✓ Demo data generation complete!")
    print(f"  - {num_customers} customers")
    print(f"  - {len(events_data)} events")
    print(f"  - 1 campaign")
    print(f"  - {len(decisions_data)} agent decisions")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("CDP Demo Data") \
        .getOrCreate()
    
    generate_demo_data(spark, tenant_id="demo_tenant", num_customers=100)
```

---

## PHASE 2: BACKEND IMPLEMENTATION

### 2.1 Configuration & Dependencies

**File:** `backend/requirements.txt`

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Databricks
databricks-sdk==0.18.0
databricks-agents==0.1.0
mlflow==2.9.0

# Data Processing
pyspark==3.5.0
pandas==2.1.3
numpy==1.26.2

# Database
delta-spark==3.0.0

# Integrations - Email
sendgrid==6.11.0
boto3==1.34.0  # For AWS SES

# Integrations - SMS
twilio==8.11.0

# Integrations - Push
firebase-admin==6.3.0

# Integrations - Ads
facebook-business==18.0.0
google-ads==23.0.0

# Utilities
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2
redis==5.0.1
celery==5.3.4

# Monitoring & Logging
python-json-logger==2.0.7
prometheus-client==0.19.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
```

**File:** `backend/app/config.py`

```python
"""
Configuration management for CDP Platform
Uses Pydantic settings for validation and environment variable management
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Databricks CDP Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Databricks
    DATABRICKS_HOST: str
    DATABRICKS_TOKEN: str
    DATABRICKS_CATALOG: str = "cdp_platform"
    DATABRICKS_SCHEMA: str = "core"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Agent Configuration
    AGENT_MODEL: str = "databricks-meta-llama-3-1-70b-instruct"
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_TEMPERATURE: float = 0.7
    
    # Email Provider (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@cdp-platform.com"
    
    # SMS Provider (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    
    # Push Notification (Firebase)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Redis (for feature caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # MLflow
    MLFLOW_TRACKING_URI: str
    MLFLOW_EXPERIMENT_NAME: str = "/cdp-platform/agent-decisions"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
```

**File:** `backend/app/dependencies.py`

```python
"""
Dependency injection for FastAPI
Handles authentication, database connections, etc.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession
import mlflow
from typing import Optional
from .config import get_settings

settings = get_settings()
security = HTTPBearer()

# Databricks Client (singleton)
_workspace_client = None
_spark_session = None

def get_workspace_client() -> WorkspaceClient:
    """Get Databricks workspace client"""
    global _workspace_client
    if _workspace_client is None:
        _workspace_client = WorkspaceClient(
            host=settings.DATABRICKS_HOST,
            token=settings.DATABRICKS_TOKEN
        )
    return _workspace_client

def get_spark_session() -> SparkSession:
    """Get or create Spark session"""
    global _spark_session
    if _spark_session is None:
        _spark_session = SparkSession.builder \
            .appName("CDP Platform API") \
            .config("spark.databricks.service.address", settings.DATABRICKS_HOST) \
            .config("spark.databricks.service.token", settings.DATABRICKS_TOKEN) \
            .getOrCreate()
    return _spark_session

def get_tenant_context(x_tenant_id: Optional[str] = Header(None)) -> str:
    """
    Extract tenant ID from request headers
    In production, this would validate JWT and extract tenant from claims
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required"
        )
    return x_tenant_id

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token (simplified for demo)
    In production, use proper JWT validation with databricks-sdk or custom auth
    """
    token = credentials.credentials
    
    # TODO: Implement proper JWT validation
    # For now, accept any token in development
    if settings.ENVIRONMENT == "development":
        return {"user_id": "demo_user", "tenant_id": "demo_tenant"}
    
    # Production: validate token
    try:
        # Validate token and extract claims
        payload = verify_jwt_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def verify_jwt_token(token: str) -> dict:
    """Validate JWT token"""
    # Implement JWT validation logic
    pass

def setup_mlflow():
    """Configure MLflow tracking"""
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
```

### 2.2 Main FastAPI Application

**File:** `backend/app/main.py`

```python
"""
Main FastAPI application
Entry point for CDP Platform API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from .config import get_settings
from .dependencies import setup_mlflow
from .api import customers, campaigns, agents, analytics, identity
from .utils.monitoring import setup_logging, MetricsMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    setup_logging()
    setup_mlflow()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Customer Data Platform with Agentic AI",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(MetricsMiddleware)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Include routers
app.include_router(
    customers.router,
    prefix="/api/customers",
    tags=["customers"]
)
app.include_router(
    campaigns.router,
    prefix="/api/campaigns",
    tags=["campaigns"]
)
app.include_router(
    agents.router,
    prefix="/api/agents",
    tags=["agents"]
)
app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["analytics"]
)
app.include_router(
    identity.router,
    prefix="/api/identity",
    tags=["identity"]
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

### 2.3 Pydantic Models

**File:** `backend/app/models/customer.py`

```python
"""
Pydantic models for Customer entities
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal

class DeviceInfo(BaseModel):
    """Device information"""
    device_id: str
    device_family: str
    last_seen: datetime
    push_token: Optional[str] = None

class CustomerBase(BaseModel):
    """Base customer model"""
    email: EmailStr
    phone: Optional[str] = None
    first_name: str
    last_name: str
    segment: Optional[str] = None
    
class CustomerCreate(CustomerBase):
    """Customer creation model"""
    tenant_id: str
    
class CustomerUpdate(BaseModel):
    """Customer update model (all fields optional)"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    segment: Optional[str] = None
    preferred_channel: Optional[str] = None
    email_consent: Optional[bool] = None
    sms_consent: Optional[bool] = None
    push_consent: Optional[bool] = None

class Customer(CustomerBase):
    """Full customer model"""
    customer_id: str
    tenant_id: str
    match_id: Optional[str] = None
    
    # Profile
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    
    # Address
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    
    # Household
    household_id: Optional[str] = None
    household_role: Optional[str] = None
    
    # Segmentation
    lifecycle_stage: Optional[str] = None
    
    # Metrics
    lifetime_value: Optional[Decimal] = None
    total_purchases: int = 0
    total_spend: Optional[Decimal] = None
    avg_order_value: Optional[Decimal] = None
    first_purchase_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None
    days_since_purchase: Optional[int] = None
    
    # Engagement
    email_engagement_score: Optional[float] = None
    sms_engagement_score: Optional[float] = None
    push_engagement_score: Optional[float] = None
    
    # ML Scores
    churn_risk_score: Optional[float] = None
    purchase_propensity_score: Optional[float] = None
    upsell_propensity_score: Optional[float] = None
    
    # Preferences
    preferred_channel: Optional[str] = None
    preferred_language: str = "en"
    timezone: Optional[str] = None
    
    # Consent
    email_consent: bool = False
    sms_consent: bool = False
    push_consent: bool = False
    
    # Devices
    registered_devices: List[DeviceInfo] = []
    
    # System
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Customer360(BaseModel):
    """Complete customer 360 view"""
    profile: Customer
    recent_events: List[Dict]
    campaign_history: List[Dict]
    agent_decisions: List[Dict]
    household_members: Optional[List[Dict]] = None
    
class CustomerListResponse(BaseModel):
    """Customer list response"""
    customers: List[Customer]
    total: int
    page: int
    page_size: int
```

**File:** `backend/app/models/campaign.py`

```python
"""Campaign models"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    goal: str
    agent_mode: bool = True
    agent_instructions: Optional[str] = None
    channels: List[str] = ["email"]

class CampaignCreate(CampaignBase):
    tenant_id: str
    target_segment: Optional[str] = None
    audience_filter: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Campaign(CampaignBase):
    campaign_id: str
    tenant_id: str
    status: str
    target_segment: Optional[str] = None
    estimated_audience_size: Optional[int] = None
    customers_targeted: int = 0
    messages_sent: int = 0
    messages_delivered: int = 0
    messages_opened: int = 0
    conversions: int = 0
    revenue_attributed: Optional[Decimal] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    total_cost: Optional[Decimal] = None
    roas: Optional[float] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 2.4 Customer API Implementation

**File:** `backend/app/api/customers.py`

```python
"""
Customer API endpoints
CRUD operations and customer 360 views
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.customer import Customer, CustomerCreate, CustomerUpdate, Customer360, CustomerListResponse
from ..dependencies import get_tenant_context, get_spark_session
from ..services.graph_query_service import GraphQueryService
import uuid

router = APIRouter()

@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    tenant_id: str = Depends(get_tenant_context),
    segment: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    spark = Depends(get_spark_session)
):
    """List customers with filtering and pagination"""
    
    offset = (page - 1) * page_size
    
    # Build query
    where_clauses = [f"tenant_id = '{tenant_id}'"]
    
    if segment:
        where_clauses.append(f"segment = '{segment}'")
    
    if search:
        where_clauses.append(
            f"(first_name LIKE '%{search}%' OR last_name LIKE '%{search}%' OR email LIKE '%{search}%')"
        )
    
    where_clause = " AND ".join(where_clauses)
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*) as total
        FROM cdp_platform.core.customers
        WHERE {where_clause}
    """
    total = spark.sql(count_query).collect()[0]['total']
    
    # Get customers
    query = f"""
        SELECT *
        FROM cdp_platform.core.customers
        WHERE {where_clause}
        ORDER BY lifetime_value DESC
        LIMIT {page_size} OFFSET {offset}
    """
    
    results = spark.sql(query).toPandas().to_dict('records')
    customers = [Customer(**row) for row in results]
    
    return CustomerListResponse(
        customers=customers,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{customer_id}", response_model=Customer360)
async def get_customer_360(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Get complete customer 360 view"""
    
    # 1. Profile
    profile_query = f"""
        SELECT * FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """
    profile_result = spark.sql(profile_query).toPandas().to_dict('records')
    
    if not profile_result:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    profile = Customer(**profile_result[0])
    
    # 2. Recent events
    events_query = f"""
        SELECT event_type, event_timestamp, page_url, properties
        FROM cdp_platform.core.clickstream_events
        WHERE tenant_id = '{tenant_id}' 
        AND match_id = '{profile.match_id}'
        ORDER BY event_timestamp DESC
        LIMIT 50
    """
    recent_events = spark.sql(events_query).toPandas().to_dict('records')
    
    # 3. Campaign history
    campaign_query = f"""
        SELECT 
            c.name,
            d.sent_at,
            d.channel,
            d.opened,
            d.clicked,
            d.converted
        FROM cdp_platform.core.deliveries d
        JOIN cdp_platform.core.campaigns c ON d.campaign_id = c.campaign_id
        WHERE d.tenant_id = '{tenant_id}' AND d.customer_id = '{customer_id}'
        ORDER BY d.sent_at DESC
        LIMIT 20
    """
    campaign_history = spark.sql(campaign_query).toPandas().to_dict('records')
    
    # 4. Agent decisions
    decisions_query = f"""
        SELECT 
            decision_id,
            campaign_id,
            action,
            channel,
            reasoning_summary,
            confidence_score,
            timestamp
        FROM cdp_platform.core.agent_decisions
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
        ORDER BY timestamp DESC
        LIMIT 10
    """
    agent_decisions = spark.sql(decisions_query).toPandas().to_dict('records')
    
    # 5. Household members (if applicable)
    household_members = None
    if profile.household_id:
        graph_service = GraphQueryService(tenant_id, use_neptune=False)
        household_members = graph_service.get_household_members(customer_id)
    
    return Customer360(
        profile=profile,
        recent_events=recent_events,
        campaign_history=campaign_history,
        agent_decisions=agent_decisions,
        household_members=household_members
    )

@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Create new customer"""
    
    customer_id = str(uuid.uuid4())
    
    # Insert into customers table
    insert_query = f"""
        INSERT INTO cdp_platform.core.customers
        (customer_id, tenant_id, email, phone, first_name, last_name, 
         segment, created_at, updated_at)
        VALUES (
            '{customer_id}',
            '{tenant_id}',
            '{customer.email}',
            '{customer.phone or ""}',
            '{customer.first_name}',
            '{customer.last_name}',
            '{customer.segment or ""}',
            current_timestamp(),
            current_timestamp()
        )
    """
    
    spark.sql(insert_query)
    
    # Return created customer
    return await get_customer_360(customer_id, tenant_id, spark)

@router.patch("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    updates: CustomerUpdate,
    tenant_id: str = Depends(get_tenant_context),
    spark = Depends(get_spark_session)
):
    """Update customer"""
    
    # Build SET clause
    set_clauses = []
    if updates.email:
        set_clauses.append(f"email = '{updates.email}'")
    if updates.phone:
        set_clauses.append(f"phone = '{updates.phone}'")
    if updates.first_name:
        set_clauses.append(f"first_name = '{updates.first_name}'")
    if updates.last_name:
        set_clauses.append(f"last_name = '{updates.last_name}'")
    # ... add other fields
    
    set_clauses.append("updated_at = current_timestamp()")
    
    update_query = f"""
        UPDATE cdp_platform.core.customers
        SET {', '.join(set_clauses)}
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """
    
    spark.sql(update_query)
    
    # Return updated customer
    profile_result = spark.sql(f"""
        SELECT * FROM cdp_platform.core.customers
        WHERE tenant_id = '{tenant_id}' AND customer_id = '{customer_id}'
    """).toPandas().to_dict('records')
    
    if not profile_result:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return Customer(**profile_result[0])
```

### 2.5 Agent Service Implementation

**File:** `backend/app/agents/tools.py`

```python
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
    
    def send_email(
        self,
        customer_id: str,
        subject: str,
        body: str,
        send_time: str = "now"
    ) -> Dict[str, Any]:
        """
        Send email to customer (execution tool)
        Agent can call this to actually send messages
        """
        from ..services.activation_service import ActivationService
        
        # Get customer email
        customer = self.get_customer_context(customer_id)
        
        if not customer.get('email') or not customer.get('email_consent'):
            return {
                "status": "skipped",
                "reason": "no consent or email"
            }
        
        activation_service = ActivationService(self.tenant_id)
        
        delivery_id = activation_service.send_email(
            to_email=customer['email'],
            subject=subject,
            body=body,
            scheduled_time=None if send_time == "now" else send_time
        )
        
        return {
            "status": "sent" if send_time == "now" else "scheduled",
            "delivery_id": delivery_id,
            "channel": "email"
        }
    
    def send_sms(
        self,
        customer_id: str,
        message: str,
        send_time: str = "now"
    ) -> Dict[str, Any]:
        """Send SMS to customer"""
        from ..services.activation_service import ActivationService
        
        customer = self.get_customer_context(customer_id)
        
        if not customer.get('phone') or not customer.get('sms_consent'):
            return {
                "status": "skipped",
                "reason": "no consent or phone"
            }
        
        if len(message) > 160:
            return {
                "status": "error",
                "reason": "message too long (max 160 characters)"
            }
        
        activation_service = ActivationService(self.tenant_id)
        
        delivery_id = activation_service.send_sms(
            to_phone=customer['phone'],
            message=message,
            scheduled_time=None if send_time == "now" else send_time
        )
        
        return {
            "status": "sent" if send_time == "now" else "scheduled",
            "delivery_id": delivery_id,
            "channel": "sms"
        }
    
    def get_tool_list(self) -> List[callable]:
        """Return list of tools for agent framework"""
        return [
            self.get_customer_context,
            self.get_recent_behavior,
            self.get_communication_fatigue,
            self.get_household_members,
            self.get_product_recommendations,
            self.send_email,
            self.send_sms
        ]
```

**File:** `backend/app/agents/prompts.py`

```python
"""System prompts for marketing agent"""

MARKETING_AGENT_SYSTEM_PROMPT = """You are an expert marketing AI agent with execution capabilities for a Customer Data Platform.

Your role: Analyze individual customers and execute personalized marketing campaigns autonomously.

Available Tools:
1. QUERY TOOLS:
   - get_customer_context: Full customer profile, metrics, ML scores
   - get_recent_behavior: Detailed event stream
   - get_communication_fatigue: Check contact frequency and engagement
   - get_household_members: Find customers in same household
   - get_product_recommendations: Personalized product suggestions

2. EXECUTION TOOLS:
   - send_email: Send personalized email (provide subject and body)
   - send_sms: Send SMS message (max 160 characters)

Decision Framework:
1. **Understand the customer deeply** - Use query tools to gather complete context
2. **Assess if contact is appropriate**:
   - Check consent (email_consent, sms_consent)
   - Check fatigue (is_fatigued flag, messages_last_7d)
   - Check household context (avoid over-messaging households)
   - Consider churn risk, engagement scores, and recent behavior

3. **If contacting is appropriate**:
   - Choose optimal channel based on:
     * Customer preference (preferred_channel)
     * Engagement scores (email_engagement_score, sms_engagement_score)
     * Message complexity (email for detailed, SMS for urgent/short)
   - Generate highly personalized content:
     * Use customer's name
     * Reference their specific behaviors/purchases
     * Align with their segment and lifecycle stage
     * Be genuinely helpful, not salesy
   - Determine timing based on timezone and behavior patterns

4. **Execute the decision**:
   - Call send_email or send_sms with generated content
   - If scheduling for later, specify send_time

5. **Explain your reasoning**:
   - Why you decided to contact or skip
   - Why you chose this channel
   - How you personalized the message
   - What data points influenced your decision

Important Principles:
- **Respect consent**: NEVER send to customers without consent
- **Avoid fatigue**: If is_fatigued=True or messages_last_7d>3, consider skipping
- **Household awareness**: Check household_members and coordinate messaging
- **Quality over quantity**: One great personalized message > many generic ones
- **Be strategic**: Sometimes NOT contacting is the right decision
- **Transparency**: Always explain your reasoning with specific data points

Campaign Goals & Tactics:
- **Retention**: Focus on at-risk customers (churn_risk_score > 0.6), emphasize loyalty
- **Winback**: Target dormant customers, offer compelling incentives
- **Cross-sell**: Leverage product_recommendations for active customers
- **Upsell**: Focus on high-LTV customers with higher-tier products

Example Decision Process:
```
1. get_customer_context(customer_id) 
   → segment="AtRisk", churn_risk=0.75, ltv=$2500, days_since_purchase=45

2. get_communication_fatigue(customer_id)
   → messages_last_7d=1, is_fatigued=False, open_rate_7d=0.6

3. get_recent_behavior(customer_id, 30)
   → 3 product views, 1 cart abandonment, last visit 5 days ago

4. DECISION: Contact via email
   - WHY: High churn risk but good engagement, cart abandonment signal
   - CHANNEL: Email (good open rate, can include product details)
   - MESSAGE: Personalized cart recovery with additional recommendations

5. send_email(
     customer_id="...",
     subject="Still interested in [product]? Here's 15% off",
     body="Hi [name], I noticed you were looking at [product] last week..."
   )

6. REASONING: "Customer shows high churn risk (0.75) but maintains good email engagement (0.6). Cart abandonment 5 days ago presents clear opportunity. Not fatigued (only 1 message in 7d). Personalized offer based on abandoned product plus recommendations to increase basket."
```

You have the power to execute - use it wisely to genuinely help customers."""

def get_campaign_specific_prompt(campaign_goal: str, instructions: str = None) -> str:
    """Augment system prompt with campaign-specific instructions"""
    
    goal_guidance = {
        "retention": "Focus on at-risk customers. Emphasize value, loyalty rewards, and personalized attention.",
        "winback": "Target dormant customers aggressively. Use compelling incentives and urgency.",
        "cross-sell": "Leverage product recommendations. Focus on complementary products.",
        "upsell": "Target high-LTV customers with premium offerings.",
        "acquisition": "Welcome new customers warmly. Set expectations and provide onboarding."
    }
    
    campaign_prompt = f"\n\n**Current Campaign Goal: {campaign_goal}**\n"
    campaign_prompt += goal_guidance.get(campaign_goal, "")
    
    if instructions:
        campaign_prompt += f"\n\n**Additional Campaign Instructions:**\n{instructions}"
    
    return MARKETING_AGENT_SYSTEM_PROMPT + campaign_prompt
```

---

## PHASE 3: FRONTEND IMPLEMENTATION

### 3.1 React Setup

**File:** `frontend/package.json`

```json
{
  "name": "cdp-platform-ui",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@mui/material": "^5.14.20",
    "@mui/icons-material": "^5.14.19",
    "@tanstack/react-query": "^5.12.2",
    "axios": "^1.6.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "recharts": "^2.10.3",
    "react-force-graph-2d": "^1.25.4"
  },
  "devDependencies": {
    "@types/node": "^20.10.5",
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "@vitejs/plugin-react": "^4.2.1"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx"
  }
}
```

**File:** `frontend/src/theme/databricksTheme.ts`

```typescript
import { createTheme } from '@mui/material/styles';

export const databricksTheme = createTheme({
  palette: {
    primary: {
      main: '#FF3621',
      light: '#FF6247',
      dark: '#D92E1C',
    },
    secondary: {
      main: '#1B3139',
      light: '#2D4A54',
      dark: '#0F1F25',
    },
    success: {
      main: '#00A972',
    },
    error: {
      main: '#E74C3C',
    },
    warning: {
      main: '#F39C12',
    },
    background: {
      default: '#F5F7FA',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
  },
});
```

### 3.2 API Service Layer

**File:** `frontend/src/services/api.ts`

```typescript
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      const tenantId = localStorage.getItem('tenant_id') || 'demo_tenant';
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      config.headers['X-Tenant-ID'] = tenantId;
      
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic methods
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.patch(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete(url);
    return response.data;
  }
}

export const apiClient = new APIClient();
```

---

## PHASE 4: TESTING & QUALITY ASSURANCE

### 4.1 Backend Tests

**File:** `backend/tests/test_agents/test_marketing_agent.py`

```python
"""
Tests for marketing agent
"""

import pytest
from app.agents.marketing_agent import MarketingAgent
from app.agents.tools import AgentTools

@pytest.fixture
def agent():
    return MarketingAgent(tenant_id="test_tenant")

@pytest.fixture
def agent_tools():
    return AgentTools(tenant_id="test_tenant")

def test_agent_analyzes_customer(agent, mock_customer_data):
    """Test agent can analyze customer and make decision"""
    
    result = agent.analyze_and_recommend(
        customer_id="test_customer_1",
        campaign_goal="retention"
    )
    
    assert result['decision_id'] is not None
    assert result['action'] in ['contact', 'skip']
    assert result['reasoning_summary'] is not None
    assert result['confidence_score'] >= 0 and result['confidence_score'] <= 1

def test_agent_respects_fatigue(agent, fatigued_customer):
    """Test agent skips fatigued customers"""
    
    result = agent.analyze_and_recommend(
        customer_id=fatigued_customer['customer_id'],
        campaign_goal="retention"
    )
    
    assert result['action'] == 'skip'
    assert 'fatigue' in result['reasoning_summary'].lower()

def test_agent_generates_personalized_content(agent, mock_customer_data):
    """Test agent generates unique personalized messages"""
    
    result1 = agent.analyze_and_recommend("customer_1", "retention")
    result2 = agent.analyze_and_recommend("customer_2", "retention")
    
    # Messages should be different
    assert result1['message_body'] != result2['message_body']
    
    # Messages should include customer name
    assert mock_customer_data[0]['first_name'] in result1['message_body']

def test_agent_tool_calls(agent_tools):
    """Test agent tools return correct data"""
    
    context = agent_tools.get_customer_context("test_customer")
    assert 'customer_id' in context
    assert 'churn_risk_score' in context
    
    behavior = agent_tools.get_recent_behavior("test_customer", days=30)
    assert isinstance(behavior, list)
    
    fatigue = agent_tools.get_communication_fatigue("test_customer")
    assert 'messages_last_7d' in fatigue
    assert 'is_fatigued' in fatigue
```

### 4.2 Integration Tests

**File:** `backend/tests/test_api/test_customer_api.py`

```python
"""
Integration tests for customer API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_customers():
    """Test customer list endpoint"""
    
    response = client.get(
        "/api/customers/",
        headers={"X-Tenant-ID": "test_tenant"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'customers' in data
    assert 'total' in data
    assert isinstance(data['customers'], list)

def test_get_customer_360():
    """Test customer 360 view"""
    
    response = client.get(
        "/api/customers/test_customer_1",
        headers={"X-Tenant-ID": "test_tenant"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'profile' in data
    assert 'recent_events' in data
    assert 'campaign_history' in data
    assert 'agent_decisions' in data

def test_customer_filtering():
    """Test customer search and filtering"""
    
    response = client.get(
        "/api/customers/?segment=VIP&search=John",
        headers={"X-Tenant-ID": "test_tenant"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # All returned customers should be VIP segment
    for customer in data['customers']:
        assert customer['segment'] == 'VIP'
```

---

## PHASE 5: DEPLOYMENT

### 5.1 Databricks Apps Configuration

**File:** `infrastructure/databricks/apps/cdp-platform-app.yml`

```yaml
name: cdp-platform
description: Customer Data Platform with Agentic AI

# Backend configuration
backend:
  path: ./backend
  dockerfile: ./backend/Dockerfile
  port: 8000
  
  env:
    DATABRICKS_HOST: ${secrets/cdp/databricks_host}
    DATABRICKS_TOKEN: ${secrets/cdp/databricks_token}
    MLFLOW_TRACKING_URI: ${secrets/cdp/mlflow_uri}
    SENDGRID_API_KEY: ${secrets/cdp/sendgrid_key}
    TWILIO_ACCOUNT_SID: ${secrets/cdp/twilio_sid}
    TWILIO_AUTH_TOKEN: ${secrets/cdp/twilio_token}
    SECRET_KEY: ${secrets/cdp/app_secret_key}
  
  resources:
    cpu: "4"
    memory: "8Gi"
    
  scale:
    min_replicas: 2
    max_replicas: 10
    target_cpu_utilization: 70

# Frontend configuration
frontend:
  path: ./frontend/build
  
# Resources access
resources:
  - name: cdp_catalog
    type: unity_catalog
    catalog: cdp_platform
    
  - name: agent_endpoint
    type: serving_endpoint
    endpoint_name: cdp-marketing-agent
    
  - name: mlflow_experiment
    type: mlflow_experiment
    path: /cdp-platform/agent-decisions

# Workflows (background jobs)
workflows:
  - name: identity_resolution
    path: ./infrastructure/databricks/workflows/identity_resolution.yml
    schedule: "0 */4 * * *"  # Every 4 hours
    
  - name: scheduled_deliveries
    path: ./infrastructure/databricks/workflows/scheduled_deliveries.yml
    schedule: "*/5 * * * *"  # Every 5 minutes
    
  - name: feature_sync
    path: ./infrastructure/databricks/workflows/feature_sync.yml
    schedule: "*/5 * * * *"  # Every 5 minutes
```

### 5.2 Docker Configuration

**File:** `backend/Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./scripts ./scripts

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Foundation ✓
- [ ] Create Unity Catalog structure
- [ ] Create all core tables
- [ ] Create UC functions for agent tools
- [ ] Generate demo data
- [ ] Verify data model with sample queries

### Phase 2: Backend ✓
- [ ] Setup FastAPI application
- [ ] Implement Customer API
- [ ] Implement Campaign API
- [ ] Implement Agent Service
- [ ] Implement Activation Service
- [ ] Setup provider integrations (SendGrid, Twilio)
- [ ] Write unit tests (>80% coverage)
- [ ] Write integration tests

### Phase 3: Frontend ✓
- [ ] Setup React application
- [ ] Implement Customer 360 page
- [ ] Implement Campaign Builder
- [ ] Implement Agent Insights Dashboard
- [ ] Implement Identity Graph Viewer
- [ ] Add Databricks theme styling
- [ ] Test responsive design

### Phase 4: Integration ✓
- [ ] Connect frontend to backend APIs
- [ ] Test end-to-end flows
- [ ] Implement error handling
- [ ] Add loading states
- [ ] Performance testing

### Phase 5: Deployment ✓
- [ ] Configure Databricks Apps
- [ ] Setup background workflows
- [ ] Configure monitoring
- [ ] Setup alerts
- [ ] Documentation
- [ ] User acceptance testing

---

## ENTERPRISE QUALITY STANDARDS

### Code Quality
- **Type Safety:** Use TypeScript for frontend, type hints for Python
- **Linting:** ESLint for TS, Black + Flake8 for Python
- **Testing:** >80% code coverage, integration tests for all APIs
- **Documentation:** Docstrings for all functions, API documentation

### Security
- **Authentication:** JWT tokens with proper validation
- **Authorization:** Row-level security via Unity Catalog
- **Data Encryption:** PII encrypted at rest
- **API Security:** Rate limiting, input validation, SQL injection prevention
- **Secrets Management:** Use Databricks Secrets, never hardcode

### Performance
- **API Response Time:** p95 < 500ms, p99 < 1s
- **Database Queries:** Optimized with proper indexing
- **Caching:** Redis for frequently accessed data
- **Scalability:** Horizontal scaling via load balancer

### Monitoring
- **Logging:** Structured JSON logs with correlation IDs
- **Metrics:** Track API latency, error rates, agent decisions
- **Alerts:** Alert on errors, performance degradation
- **Dashboards:** Real-time monitoring via Databricks System Tables

### Compliance
- **GDPR:** Right to be forgotten, data portability
- **CCPA:** Consumer privacy rights
- **Audit Trail:** Complete logging of all decisions
- **Data Retention:** Configurable retention policies

---

## NEXT STEPS AFTER IMPLEMENTATION

1. **Week 1-2:** Build Phase 1 (Data Foundation)
2. **Week 3-4:** Build Phase 2 (Backend APIs + Agent)
3. **Week 5-6:** Build Phase 3 (Frontend UI)
4. **Week 7:** Integration Testing
5. **Week 8:** Deployment + Documentation

**Success Criteria:**
- ✓ Demo-able to VP and stakeholders
- ✓ Agent makes intelligent decisions >80% accuracy
- ✓ Complete customer 360 view functional
- ✓ Multi-channel activation working (email minimum)
- ✓ Professional UI matching Databricks design system
- ✓ All tests passing
- ✓ Documentation complete

---
-- Journey definitions
CREATE TABLE cdp_platform.core.journey_definitions (
    journey_id STRING NOT NULL,
    tenant_id STRING NOT NULL,
    name STRING,
    description STRING,
    definition_json STRING,  -- Full JourneyDefinition as JSON
    status STRING,
    created_by STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT pk_journeys PRIMARY KEY (tenant_id, journey_id)
);

-- Customer journey states
CREATE TABLE cdp_platform.core.customer_journey_states (
    state_id STRING NOT NULL,
    tenant_id STRING NOT NULL,
    customer_id STRING,
    journey_id STRING,
    current_step_id STRING,
    status STRING,
    waiting_for STRING,
    wait_until TIMESTAMP,
    steps_completed ARRAY<STRING>,
    actions_taken STRING,  -- JSON array
    entered_at TIMESTAMP,
    last_action_at TIMESTAMP,
    completed_at TIMESTAMP,
    exit_reason STRING,
    CONSTRAINT pk_journey_states PRIMARY KEY (tenant_id, state_id)
);

-- Journey analytics
CREATE TABLE cdp_platform.core.journey_analytics (
    journey_id STRING,
    tenant_id STRING,
    step_id STRING,
    customers_entered INT,
    customers_completed INT,
    customers_dropped INT,
    avg_time_in_step_hours DOUBLE,
    conversion_rate DOUBLE,
    date DATE
);
```

---

## THE COMPLETE PICTURE: AGENTIC + JOURNEY ORCHESTRATION
```
Journey Orchestrator (State Machine)
    ↓
Step 1: Entry (segment trigger)
    ↓
Step 2: Agent analyzes customer → Sends personalized email
    ↓
Wait: 24 hours OR customer opens email
    ↓
Branch:
├─ If opened → Agent decides SMS offer
│     ↓
│  Wait: 3 days OR conversion
│     ↓
│  Agent decides: final push or exit
│
└─ If NOT opened → Agent tries different channel
      ↓
   Wait: 48 hours
      ↓
   Agent decides: escalate or exit
END OF IMPLEMENTATION GUIDE

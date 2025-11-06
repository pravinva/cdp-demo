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


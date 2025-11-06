-- Create Journey Tables in Unity Catalog
-- Run this script in Databricks SQL Editor or via SQL Execution API

USE CATALOG cdp_platform;
USE SCHEMA core;

-- 1. Journey Definitions Table
-- Stores journey state machine configurations
CREATE TABLE IF NOT EXISTS cdp_platform.core.journey_definitions (
    journey_id STRING NOT NULL,
    tenant_id STRING NOT NULL,
    name STRING,
    description STRING,
    definition_json STRING,  -- Full JourneyDefinition as JSON
    status STRING,
    created_by STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING DELTA
COMMENT 'Journey definitions - state machine configurations';

-- 2. Customer Journey States Table
-- Tracks each customer's current position in their active journeys
CREATE TABLE IF NOT EXISTS cdp_platform.core.customer_journey_states (
    state_id STRING NOT NULL,
    tenant_id STRING NOT NULL,
    customer_id STRING,
    journey_id STRING,
    current_step_id STRING,
    status STRING,  -- 'active', 'waiting', 'completed', 'abandoned'
    waiting_for STRING,  -- Event or condition being waited for
    wait_until TIMESTAMP,  -- Timeout for waiting state
    steps_completed ARRAY<STRING>,  -- Array of completed step IDs
    actions_taken STRING,  -- JSON array of actions taken
    entered_at TIMESTAMP,
    last_action_at TIMESTAMP,
    completed_at TIMESTAMP,
    exit_reason STRING
)
USING DELTA
COMMENT 'Customer journey state tracking - current position in journeys';

-- 3. Journey Analytics Table
-- Aggregated performance metrics for journey steps
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
COMMENT 'Journey performance analytics - aggregated metrics';

-- Verify tables were created
SHOW TABLES IN cdp_platform.core LIKE 'journey*';


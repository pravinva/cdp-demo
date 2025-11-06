-- Populate Identity Graph Data
-- Creates match groups and identity graph edges for demo purposes
-- Run this in Databricks SQL or via SQL Execution API

USE CATALOG cdp_platform;
USE SCHEMA core;

-- 1. Update customers with match_id if they don't have one
UPDATE customers
SET match_id = CONCAT('match_', SUBSTRING(REPLACE(UUID(), '-', ''), 1, 8)),
    updated_at = current_timestamp()
WHERE tenant_id = 'demo_tenant'
AND match_id IS NULL
LIMIT 100;

-- 2. Insert match groups for customers
INSERT INTO match_groups
(match_id, tenant_id, known_emails, known_phones, known_login_ids,
 shared_devices, shared_ips, shared_addresses,
 total_events, anonymous_events, known_events, unique_devices, unique_ips,
 is_household, household_size, first_seen, last_seen, created_at, updated_at)
SELECT 
    c.match_id,
    c.tenant_id,
    ARRAY(c.email) as known_emails,
    ARRAY() as known_phones,
    ARRAY(c.customer_id) as known_login_ids,
    ARRAY() as shared_devices,
    ARRAY() as shared_ips,
    ARRAY() as shared_addresses,
    50 as total_events,
    10 as anonymous_events,
    40 as known_events,
    2 as unique_devices,
    3 as unique_ips,
    false as is_household,
    1 as household_size,
    current_timestamp() - INTERVAL 30 DAY as first_seen,
    current_timestamp() - INTERVAL 1 DAY as last_seen,
    current_timestamp() as created_at,
    current_timestamp() as updated_at
FROM customers c
WHERE c.tenant_id = 'demo_tenant'
AND c.match_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM match_groups mg 
    WHERE mg.match_id = c.match_id AND mg.tenant_id = 'demo_tenant'
)
LIMIT 100;

-- 3. Assign zip codes to customers (group them into 10 zip codes for households)
UPDATE customers
SET zip_code = CONCAT('9', LPAD(CAST((ROW_NUMBER() OVER (ORDER BY customer_id) % 10) AS STRING), 4, '0'), '0'),
    updated_at = current_timestamp()
WHERE tenant_id = 'demo_tenant'
AND zip_code IS NULL;

-- 4. Create households - assign household_id to customers in same zip code
WITH ranked_customers AS (
    SELECT 
        customer_id,
        zip_code,
        ROW_NUMBER() OVER (PARTITION BY zip_code ORDER BY customer_id) as rn
    FROM customers
    WHERE tenant_id = 'demo_tenant'
    AND zip_code IS NOT NULL
),
household_ids AS (
    SELECT 
        zip_code,
        CONCAT('household_', SUBSTRING(REPLACE(UUID(), '-', ''), 1, 8)) as household_id
    FROM (
        SELECT DISTINCT zip_code
        FROM customers
        WHERE tenant_id = 'demo_tenant'
        AND zip_code IS NOT NULL
    )
)
UPDATE customers AS c
SET 
    household_id = h.household_id,
    household_role = CASE WHEN rc.rn = 1 THEN 'head' ELSE 'member' END,
    updated_at = current_timestamp()
FROM ranked_customers rc
INNER JOIN household_ids h ON rc.zip_code = h.zip_code
WHERE c.customer_id = rc.customer_id
AND c.tenant_id = 'demo_tenant'
AND rc.zip_code IN (
    SELECT zip_code
    FROM customers
    WHERE tenant_id = 'demo_tenant'
    AND zip_code IS NOT NULL
    GROUP BY zip_code
    HAVING COUNT(*) >= 2
);

-- 5. Update match groups to mark households
UPDATE match_groups mg
SET 
    is_household = true,
    household_size = (
        SELECT COUNT(*)
        FROM customers c
        WHERE c.household_id = (
            SELECT household_id 
            FROM customers 
            WHERE match_id = mg.match_id 
            AND tenant_id = 'demo_tenant'
            LIMIT 1
        )
        AND c.tenant_id = 'demo_tenant'
    ),
    updated_at = current_timestamp()
WHERE mg.tenant_id = 'demo_tenant'
AND EXISTS (
    SELECT 1 FROM customers c
    WHERE c.match_id = mg.match_id
    AND c.tenant_id = 'demo_tenant'
    AND c.household_id IS NOT NULL
);

-- 6. Create household edges (customer to customer)
INSERT INTO identity_graph_edges
(edge_id, tenant_id, from_entity_type, from_entity_id,
 to_entity_type, to_entity_id, relationship_type,
 strength, evidence_count, first_seen, last_seen)
SELECT 
    CONCAT('edge_', REPLACE(UUID(), '-', '')) as edge_id,
    c1.tenant_id,
    'customer' as from_entity_type,
    c1.customer_id as from_entity_id,
    'customer' as to_entity_type,
    c2.customer_id as to_entity_id,
    'household' as relationship_type,
    0.85 as strength,
    25 as evidence_count,
    current_timestamp() - INTERVAL 30 DAY as first_seen,
    current_timestamp() - INTERVAL 1 DAY as last_seen
FROM customers c1
INNER JOIN customers c2
    ON c1.household_id = c2.household_id
    AND c1.tenant_id = c2.tenant_id
    AND c1.customer_id < c2.customer_id
WHERE c1.tenant_id = 'demo_tenant'
AND c1.household_id IS NOT NULL
AND c2.household_id IS NOT NULL;

-- 7. Create match group to customer edges
INSERT INTO identity_graph_edges
(edge_id, tenant_id, from_entity_type, from_entity_id,
 to_entity_type, to_entity_id, relationship_type,
 strength, evidence_count, first_seen, last_seen)
SELECT 
    CONCAT('edge_', REPLACE(UUID(), '-', '')) as edge_id,
    c.tenant_id,
    'match_group' as from_entity_type,
    c.match_id as from_entity_id,
    'customer' as to_entity_type,
    c.customer_id as to_entity_id,
    'identity_match' as relationship_type,
    0.95 as strength,
    50 as evidence_count,
    current_timestamp() - INTERVAL 30 DAY as first_seen,
    current_timestamp() - INTERVAL 1 DAY as last_seen
FROM customers c
WHERE c.tenant_id = 'demo_tenant'
AND c.match_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM identity_graph_edges e
    WHERE e.from_entity_id = c.match_id
    AND e.to_entity_id = c.customer_id
    AND e.tenant_id = 'demo_tenant'
)
LIMIT 100;

-- Summary query
SELECT 'Match Groups' as metric, COUNT(*) as count
FROM match_groups
WHERE tenant_id = 'demo_tenant'
UNION ALL
SELECT 'Households' as metric, COUNT(DISTINCT household_id) as count
FROM customers
WHERE tenant_id = 'demo_tenant' AND household_id IS NOT NULL
UNION ALL
SELECT 'Graph Edges' as metric, COUNT(*) as count
FROM identity_graph_edges
WHERE tenant_id = 'demo_tenant';

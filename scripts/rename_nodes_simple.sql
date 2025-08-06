-- Simple SQL script to rename nodes based on volume analysis
-- This script assumes the mapping between CSV columns and node IDs
-- Please verify the node_id mappings before running!

-- Start transaction
BEGIN;

-- Show current nodes before changes
SELECT node_id, node_name, node_type 
FROM water_infrastructure.nodes 
WHERE is_active = true
ORDER BY node_id;

-- Rename based on volume analysis results:
-- M3.3 (11,077,575 m³) → TANK01 (largest volume, clearly a storage tank)
-- M3.2 (5,219,552 m³) → MONITOR01 (monitoring point with significant volume)
-- M3 (1,925,967 m³) → NODE01 (distribution node with consumption)
-- M3.1 (165,619 m³) → MONITOR02 (smaller monitoring point)

-- Update nodes - ADJUST node_id VALUES BASED ON YOUR ACTUAL DATABASE!
-- Option 1: If nodes use simple IDs like '001', '002', '003', '004'
UPDATE water_infrastructure.nodes
SET node_name = CASE node_id
    WHEN '001' THEN 'NODE01'      -- M3 column
    WHEN '002' THEN 'MONITOR02'   -- M3.1 column
    WHEN '003' THEN 'MONITOR01'   -- M3.2 column
    WHEN '004' THEN 'TANK01'      -- M3.3 column
    ELSE node_name
END,
node_type = CASE node_id
    WHEN '001' THEN 'distribution'
    WHEN '002' THEN 'monitoring'
    WHEN '003' THEN 'monitoring'
    WHEN '004' THEN 'storage'
    ELSE node_type
END,
metadata = jsonb_set(
    COALESCE(metadata, '{}'::jsonb),
    '{volume_info}',
    CASE node_id
        WHEN '001' THEN '{"max_volume_m3": 1925967, "category": "distribution"}'::jsonb
        WHEN '002' THEN '{"max_volume_m3": 165619, "category": "monitoring"}'::jsonb
        WHEN '003' THEN '{"max_volume_m3": 5219552, "category": "monitoring"}'::jsonb
        WHEN '004' THEN '{"max_volume_m3": 11077575, "category": "tank"}'::jsonb
        ELSE metadata->'volume_info'
    END,
    true
),
updated_at = CURRENT_TIMESTAMP
WHERE node_id IN ('001', '002', '003', '004');

-- Option 2: If nodes use IDs like those in add_node_coordinates.py
-- Uncomment and adjust this section if your node IDs follow different patterns

/*
-- Example for NODE_287156, NODE_288400, etc.
UPDATE water_infrastructure.nodes
SET node_name = CASE 
    WHEN node_id = 'NODE_287156' THEN 'NODE01'
    WHEN node_id = 'NODE_288400' THEN 'MONITOR02'
    WHEN node_id = 'NODE_215542' THEN 'MONITOR01'
    WHEN node_id = 'NODE_281492' THEN 'TANK01'
    ELSE node_name
END,
node_type = CASE 
    WHEN node_id = 'NODE_287156' THEN 'distribution'
    WHEN node_id = 'NODE_288400' THEN 'monitoring'
    WHEN node_id = 'NODE_215542' THEN 'monitoring'
    WHEN node_id = 'NODE_281492' THEN 'storage'
    ELSE node_type
END,
updated_at = CURRENT_TIMESTAMP
WHERE node_id IN ('NODE_287156', 'NODE_288400', 'NODE_215542', 'NODE_281492');
*/

-- Show results after changes
SELECT node_id, node_name, node_type, 
       metadata->'volume_info' as volume_info
FROM water_infrastructure.nodes 
WHERE is_active = true
ORDER BY node_name;

-- IMPORTANT: Review the changes before committing!
-- If everything looks correct, run: COMMIT;
-- If you want to undo the changes, run: ROLLBACK;

-- COMMIT;  -- Uncomment to apply changes
-- ROLLBACK;  -- Uncomment to undo changes


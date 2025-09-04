-- Insert test data for Consumption Analytics

-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS nodes (
    node_id VARCHAR(50) PRIMARY KEY,
    node_name VARCHAR(100) NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(50) REFERENCES nodes(node_id),
    timestamp TIMESTAMP NOT NULL,
    flow_rate_liters_per_second DECIMAL(10, 2),
    pressure_bar DECIMAL(5, 2),
    temperature_celsius DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test nodes
INSERT INTO nodes (node_id, node_name, node_type) VALUES
    ('VIA_DANTE_1', 'Via Dante Principale', 'main'),
    ('VIA_ROMA_2', 'Via Roma Secondario', 'secondary'),
    ('ZONA_INDUSTRIALE_1', 'Zona Industriale Nord', 'industrial'),
    ('RESIDENZIALE_1', 'Zona Residenziale Centro', 'residential'),
    ('COMMERCIALE_1', 'Zona Commerciale Sud', 'commercial'),
    ('VIA_GARIBALDI_3', 'Via Garibaldi Terziario', 'secondary'),
    ('ZONA_OSPEDALE_1', 'Ospedale Civico', 'main')
ON CONFLICT (node_id) DO NOTHING;

-- Insert sample sensor readings for the last 7 days
-- This will create realistic data for testing

-- Via Dante Principale (main node)
INSERT INTO sensor_readings (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
SELECT 
    'VIA_DANTE_1',
    generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE,
        INTERVAL '1 hour'
    ),
    4.5 + (random() - 0.5) * 0.5,
    3.2 + (random() - 0.5) * 0.3,
    15 + (random() - 0.5) * 10;

-- Via Roma Secondario (secondary node)
INSERT INTO sensor_readings (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
SELECT 
    'VIA_ROMA_2',
    generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE,
        INTERVAL '1 hour'
    ),
    2.8 + (random() - 0.5) * 0.5,
    2.5 + (random() - 0.5) * 0.3,
    15 + (random() - 0.5) * 10;

-- Zona Industriale Nord (industrial node)
INSERT INTO sensor_readings (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
SELECT 
    'ZONA_INDUSTRIALE_1',
    generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE,
        INTERVAL '1 hour'
    ),
    8.7 + (random() - 0.5) * 0.5,
    4.5 + (random() - 0.5) * 0.3,
    15 + (random() - 0.5) * 10;

-- Zona Residenziale Centro (residential node)
INSERT INTO sensor_readings (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
SELECT 
    'RESIDENZIALE_1',
    generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE,
        INTERVAL '1 hour'
    ),
    1.8 + (random() - 0.5) * 0.5,
    2.0 + (random() - 0.5) * 0.3,
    15 + (random() - 0.5) * 10;

-- Zona Commerciale Sud (commercial node)
INSERT INTO sensor_readings (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
SELECT 
    'COMMERCIALE_1',
    generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE,
        INTERVAL '1 hour'
    ),
    3.2 + (random() - 0.5) * 0.5,
    3.0 + (random() - 0.5) * 0.3,
    15 + (random() - 0.5) * 10;

-- Via Garibaldi Terziario (secondary node)
INSERT INTO sensor_readings (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
SELECT 
    'VIA_GARIBALDI_3',
    generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE,
        INTERVAL '1 hour'
    ),
    2.6 + (random() - 0.5) * 0.5,
    2.8 + (random() - 0.5) * 0.3,
    15 + (random() - 0.5) * 10;

-- Ospedale Civico (main node)
INSERT INTO sensor_readings (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
SELECT 
    'ZONA_OSPEDALE_1',
    generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE,
        INTERVAL '1 hour'
    ),
    4.3 + (random() - 0.5) * 0.5,
    3.5 + (random() - 0.5) * 0.3,
    15 + (random() - 0.5) * 10;

-- Show summary
SELECT 
    'Data Summary' as info,
    COUNT(DISTINCT node_id) as total_nodes,
    COUNT(*) as total_readings,
    MIN(timestamp) as earliest_timestamp,
    MAX(timestamp) as latest_timestamp
FROM sensor_readings;

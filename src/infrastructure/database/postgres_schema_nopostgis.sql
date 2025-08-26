-- PostgreSQL + TimescaleDB Schema for Abbanoa Water Infrastructure
-- This schema provides the warm storage layer for operational data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create schema
CREATE SCHEMA IF NOT EXISTS water_infrastructure;

-- Set search path
SET search_path TO water_infrastructure, public;

-- ====================================
-- Core Tables
-- ====================================

-- Node metadata table
CREATE TABLE IF NOT EXISTS nodes (
    node_id VARCHAR(50) PRIMARY KEY,
    node_name VARCHAR(100) NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    location_name VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    installation_date DATE,
    last_maintenance_date DATE,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for node queries
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_active ON nodes(is_active);
CREATE INDEX IF NOT EXISTS idx_nodes_metadata ON nodes USING GIN(metadata);

-- Sensor readings table (main time-series data)
CREATE TABLE IF NOT EXISTS sensor_readings (
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    node_id VARCHAR(50) NOT NULL,
    temperature DECIMAL(5, 2),
    flow_rate DECIMAL(10, 2),
    pressure DECIMAL(6, 2),
    total_flow DECIMAL(12, 2),
    quality_score DECIMAL(3, 2),
    is_interpolated BOOLEAN DEFAULT false,
    raw_data JSONB,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('sensor_readings', 'timestamp', 
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sensor_readings_node_time ON sensor_readings(node_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_flow ON sensor_readings(flow_rate) WHERE flow_rate IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sensor_readings_pressure ON sensor_readings(pressure) WHERE pressure IS NOT NULL;

-- ====================================
-- ML and Analytics Tables
-- ====================================

-- Anomaly detections table
CREATE TABLE IF NOT EXISTS anomalies (
    anomaly_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    node_id VARCHAR(50) NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    measurement_type VARCHAR(50),
    actual_value DECIMAL(10, 2),
    expected_value DECIMAL(10, 2),
    deviation_percentage DECIMAL(5, 2),
    detection_method VARCHAR(50),
    is_confirmed BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

-- Convert to hypertable for time-series queries
SELECT create_hypertable('anomalies', 'timestamp',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- Indexes for anomaly queries
CREATE INDEX IF NOT EXISTS idx_anomalies_node_time ON anomalies(node_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type, severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_unresolved ON anomalies(resolved_at) WHERE resolved_at IS NULL;

-- ML model predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    prediction_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    node_id VARCHAR(50) NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20),
    prediction_type VARCHAR(50) NOT NULL,
    target_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    predicted_value DECIMAL(10, 2),
    confidence_lower DECIMAL(10, 2),
    confidence_upper DECIMAL(10, 2),
    confidence_score DECIMAL(3, 2),
    actual_value DECIMAL(10, 2),
    error_percentage DECIMAL(5, 2),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

-- Convert to hypertable
SELECT create_hypertable('ml_predictions', 'timestamp',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- Indexes for ML predictions
CREATE INDEX IF NOT EXISTS idx_ml_predictions_node_time ON ml_predictions(node_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_model ON ml_predictions(model_name, model_version);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_target ON ml_predictions(target_timestamp);

-- ====================================
-- Operational Tables
-- ====================================

-- Daily aggregates table (materialized for performance)
CREATE TABLE IF NOT EXISTS daily_aggregates (
    date DATE NOT NULL,
    node_id VARCHAR(50) NOT NULL,
    avg_flow_rate DECIMAL(10, 2),
    min_flow_rate DECIMAL(10, 2),
    max_flow_rate DECIMAL(10, 2),
    total_flow_volume DECIMAL(12, 2),
    avg_pressure DECIMAL(6, 2),
    min_pressure DECIMAL(6, 2),
    max_pressure DECIMAL(6, 2),
    avg_temperature DECIMAL(5, 2),
    data_quality_score DECIMAL(3, 2),
    anomaly_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (date, node_id),
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

-- Indexes for daily aggregates
CREATE INDEX IF NOT EXISTS idx_daily_aggregates_node_date ON daily_aggregates(node_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_aggregates_date ON daily_aggregates(date DESC);

-- Network events table
CREATE TABLE IF NOT EXISTS network_events (
    event_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical', 'emergency')),
    affected_nodes TEXT[],
    description TEXT,
    action_taken TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for network events
CREATE INDEX IF NOT EXISTS idx_network_events_timestamp ON network_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_network_events_type ON network_events(event_type, severity);
CREATE INDEX IF NOT EXISTS idx_network_events_unresolved ON network_events(resolved_at) WHERE resolved_at IS NULL;

-- Maintenance records table
CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id SERIAL PRIMARY KEY,
    node_id VARCHAR(50) NOT NULL,
    scheduled_date DATE NOT NULL,
    completed_date DATE,
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT,
    technician_name VARCHAR(100),
    cost DECIMAL(10, 2),
    next_maintenance_date DATE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

-- Indexes for maintenance records
CREATE INDEX IF NOT EXISTS idx_maintenance_node ON maintenance_records(node_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_scheduled ON maintenance_records(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_maintenance_type ON maintenance_records(maintenance_type);

-- ====================================
-- Views for API Access
-- ====================================

-- Current node status view
CREATE OR REPLACE VIEW current_node_status AS
SELECT 
    n.node_id,
    n.node_name,
    n.node_type,
    n.location_name,
    n.latitude,
    n.longitude,
    n.is_active,
    sr.timestamp as last_reading_time,
    sr.flow_rate as current_flow_rate,
    sr.pressure as current_pressure,
    sr.temperature as current_temperature,
    sr.quality_score as current_quality_score,
    CASE 
        WHEN sr.timestamp > CURRENT_TIMESTAMP - INTERVAL '1 hour' THEN 'online'
        WHEN sr.timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours' THEN 'degraded'
        ELSE 'offline'
    END as status
FROM nodes n
LEFT JOIN LATERAL (
    SELECT * FROM sensor_readings 
    WHERE node_id = n.node_id 
    ORDER BY timestamp DESC 
    LIMIT 1
) sr ON true;

-- Daily summary view
CREATE OR REPLACE VIEW daily_summary AS
SELECT 
    date,
    COUNT(DISTINCT node_id) as active_nodes,
    AVG(avg_flow_rate) as network_avg_flow,
    SUM(total_flow_volume) as network_total_volume,
    AVG(avg_pressure) as network_avg_pressure,
    AVG(data_quality_score) as network_quality_score,
    SUM(anomaly_count) as total_anomalies
FROM daily_aggregates
GROUP BY date
ORDER BY date DESC;

-- Recent anomalies view
CREATE OR REPLACE VIEW recent_anomalies AS
SELECT 
    a.anomaly_id,
    a.timestamp,
    n.node_name,
    n.location_name,
    a.anomaly_type,
    a.severity,
    a.measurement_type,
    a.actual_value,
    a.expected_value,
    a.deviation_percentage,
    a.is_confirmed,
    a.resolved_at
FROM anomalies a
JOIN nodes n ON a.node_id = n.node_id
WHERE a.timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY a.timestamp DESC;

-- ====================================
-- Functions and Triggers
-- ====================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_nodes_updated_at BEFORE UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_aggregates_updated_at BEFORE UPDATE ON daily_aggregates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_records_updated_at BEFORE UPDATE ON maintenance_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate daily aggregates
CREATE OR REPLACE FUNCTION calculate_daily_aggregates(target_date DATE, target_node_id VARCHAR(50))
RETURNS void AS $$
BEGIN
    INSERT INTO daily_aggregates (
        date, node_id, 
        avg_flow_rate, min_flow_rate, max_flow_rate, total_flow_volume,
        avg_pressure, min_pressure, max_pressure,
        avg_temperature, data_quality_score, anomaly_count
    )
    SELECT 
        target_date,
        target_node_id,
        AVG(flow_rate),
        MIN(flow_rate),
        MAX(flow_rate),
        SUM(total_flow),
        AVG(pressure),
        MIN(pressure),
        MAX(pressure),
        AVG(temperature),
        AVG(quality_score),
        (SELECT COUNT(*) FROM anomalies 
         WHERE node_id = target_node_id 
         AND DATE(timestamp) = target_date)
    FROM sensor_readings
    WHERE node_id = target_node_id
    AND DATE(timestamp) = target_date
    ON CONFLICT (date, node_id) DO UPDATE SET
        avg_flow_rate = EXCLUDED.avg_flow_rate,
        min_flow_rate = EXCLUDED.min_flow_rate,
        max_flow_rate = EXCLUDED.max_flow_rate,
        total_flow_volume = EXCLUDED.total_flow_volume,
        avg_pressure = EXCLUDED.avg_pressure,
        min_pressure = EXCLUDED.min_pressure,
        max_pressure = EXCLUDED.max_pressure,
        avg_temperature = EXCLUDED.avg_temperature,
        data_quality_score = EXCLUDED.data_quality_score,
        anomaly_count = EXCLUDED.anomaly_count,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- ====================================
-- Continuous Aggregates (TimescaleDB)
-- ====================================

-- Hourly continuous aggregate
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) as hour,
    node_id,
    AVG(flow_rate) as avg_flow_rate,
    MIN(flow_rate) as min_flow_rate,
    MAX(flow_rate) as max_flow_rate,
    AVG(pressure) as avg_pressure,
    MIN(pressure) as min_pressure,
    MAX(pressure) as max_pressure,
    AVG(temperature) as avg_temperature,
    COUNT(*) as reading_count
FROM sensor_readings
GROUP BY hour, node_id
WITH NO DATA;

-- Add refresh policy for hourly aggregate
SELECT add_continuous_aggregate_policy('sensor_readings_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- ====================================
-- Initial Data and Permissions
-- ====================================

-- Insert sample nodes (if not exists)
INSERT INTO nodes (node_id, node_name, node_type, location_name, latitude, longitude, is_active)
VALUES 
    ('VIA_DANTE_1', 'Via Dante Principale', 'main', 'Via Dante', 39.2154, 9.1134, true),
    ('VIA_ROMA_1', 'Via Roma Secondario', 'secondary', 'Via Roma', 39.2200, 9.1100, true),
    ('PIAZZA_ITALIA_1', 'Piazza Italia Distribuzione', 'distribution', 'Piazza Italia', 39.2180, 9.1150, true)
ON CONFLICT (node_id) DO NOTHING;

-- Grant permissions (adjust as needed)
GRANT ALL ON SCHEMA water_infrastructure TO abbanoa_user;
GRANT ALL ON ALL TABLES IN SCHEMA water_infrastructure TO abbanoa_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA water_infrastructure TO abbanoa_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA water_infrastructure TO abbanoa_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Schema creation completed successfully!';
    RAISE NOTICE 'Tables created: nodes, sensor_readings, anomalies, ml_predictions, daily_aggregates, network_events, maintenance_records';
    RAISE NOTICE 'Views created: current_node_status, daily_summary, recent_anomalies';
    RAISE NOTICE 'Continuous aggregates: sensor_readings_hourly';
END $$;
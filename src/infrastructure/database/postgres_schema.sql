-- PostgreSQL + TimescaleDB Schema for Abbanoa Water Infrastructure
-- This schema provides the warm storage layer for operational data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Enable PostGIS for geospatial data (future use)
CREATE EXTENSION IF NOT EXISTS postgis;

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
CREATE INDEX idx_nodes_type ON nodes(node_type);
CREATE INDEX idx_nodes_active ON nodes(is_active);
CREATE INDEX idx_nodes_metadata ON nodes USING GIN(metadata);

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
CREATE INDEX idx_sensor_readings_node_time ON sensor_readings(node_id, timestamp DESC);
CREATE INDEX idx_sensor_readings_flow ON sensor_readings(flow_rate) WHERE flow_rate IS NOT NULL;
CREATE INDEX idx_sensor_readings_pressure ON sensor_readings(pressure) WHERE pressure IS NOT NULL;

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
CREATE INDEX idx_anomalies_node_time ON anomalies(node_id, timestamp DESC);
CREATE INDEX idx_anomalies_type ON anomalies(anomaly_type, severity);
CREATE INDEX idx_anomalies_unresolved ON anomalies(resolved_at) WHERE resolved_at IS NULL;

-- ML model predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    prediction_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    node_id VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20),
    prediction_type VARCHAR(50) NOT NULL,
    prediction_horizon_hours INTEGER NOT NULL,
    predicted_value DECIMAL(10, 2),
    confidence_score DECIMAL(3, 2),
    prediction_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

-- Convert to hypertable
SELECT create_hypertable('ml_predictions', 'timestamp',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- ====================================
-- Continuous Aggregates (Materialized Views)
-- ====================================

-- 5-minute aggregates
CREATE MATERIALIZED VIEW sensor_readings_5min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', timestamp) AS bucket,
    node_id,
    COUNT(*) as reading_count,
    AVG(temperature) as avg_temperature,
    AVG(flow_rate) as avg_flow_rate,
    MAX(flow_rate) as max_flow_rate,
    MIN(flow_rate) as min_flow_rate,
    AVG(pressure) as avg_pressure,
    MAX(pressure) as max_pressure,
    MIN(pressure) as min_pressure,
    SUM(CASE WHEN flow_rate > 0 THEN flow_rate * 5 * 60 / 1000 ELSE 0 END) as total_volume_m3
FROM sensor_readings
GROUP BY bucket, node_id
WITH NO DATA;

-- 1-hour aggregates
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    node_id,
    COUNT(*) as reading_count,
    AVG(temperature) as avg_temperature,
    AVG(flow_rate) as avg_flow_rate,
    MAX(flow_rate) as max_flow_rate,
    MIN(flow_rate) as min_flow_rate,
    STDDEV(flow_rate) as stddev_flow_rate,
    AVG(pressure) as avg_pressure,
    MAX(pressure) as max_pressure,
    MIN(pressure) as min_pressure,
    STDDEV(pressure) as stddev_pressure,
    SUM(CASE WHEN flow_rate > 0 THEN flow_rate * 3600 / 1000 ELSE 0 END) as total_volume_m3,
    AVG(quality_score) as avg_quality_score
FROM sensor_readings
GROUP BY bucket, node_id
WITH NO DATA;

-- Daily aggregates
CREATE MATERIALIZED VIEW sensor_readings_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', timestamp) AS bucket,
    node_id,
    COUNT(*) as reading_count,
    AVG(temperature) as avg_temperature,
    MAX(temperature) as max_temperature,
    MIN(temperature) as min_temperature,
    AVG(flow_rate) as avg_flow_rate,
    MAX(flow_rate) as max_flow_rate,
    MIN(flow_rate) as min_flow_rate,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY flow_rate) as median_flow_rate,
    AVG(pressure) as avg_pressure,
    MAX(pressure) as max_pressure,
    MIN(pressure) as min_pressure,
    SUM(CASE WHEN flow_rate > 0 THEN flow_rate * 86400 / 1000 ELSE 0 END) as total_volume_m3,
    AVG(quality_score) as avg_quality_score,
    COUNT(CASE WHEN quality_score < 0.8 THEN 1 END) as low_quality_readings
FROM sensor_readings
GROUP BY bucket, node_id
WITH NO DATA;

-- Create refresh policies for continuous aggregates
SELECT add_continuous_aggregate_policy('sensor_readings_5min',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes',
    if_not_exists => TRUE
);

SELECT add_continuous_aggregate_policy('sensor_readings_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

SELECT add_continuous_aggregate_policy('sensor_readings_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ====================================
-- System and Audit Tables
-- ====================================

-- ETL job tracking
CREATE TABLE IF NOT EXISTS etl_jobs (
    job_id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    records_processed INTEGER,
    records_failed INTEGER,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etl_jobs_status ON etl_jobs(status, started_at DESC);

-- Cache sync tracking
CREATE TABLE IF NOT EXISTS cache_sync_log (
    sync_id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100),
    sync_status VARCHAR(20) NOT NULL,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ====================================
-- Data Retention Policies
-- ====================================

-- Keep raw data for 90 days
SELECT add_retention_policy('sensor_readings',
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Keep anomalies for 1 year
SELECT add_retention_policy('anomalies',
    INTERVAL '365 days',
    if_not_exists => TRUE
);

-- Keep ML predictions for 30 days
SELECT add_retention_policy('ml_predictions',
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- ====================================
-- Compression Policies
-- ====================================

-- Compress sensor readings older than 7 days
ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'node_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('sensor_readings',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ====================================
-- Helper Functions
-- ====================================

-- Function to get system metrics
CREATE OR REPLACE FUNCTION get_system_metrics(
    time_range INTERVAL DEFAULT INTERVAL '24 hours'
)
RETURNS TABLE (
    active_nodes BIGINT,
    total_nodes BIGINT,
    total_flow DECIMAL,
    avg_pressure DECIMAL,
    total_volume_m3 DECIMAL,
    anomaly_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT sr.node_id) as active_nodes,
        (SELECT COUNT(*) FROM nodes WHERE is_active = true) as total_nodes,
        COALESCE(AVG(sr.flow_rate), 0) as total_flow,
        COALESCE(AVG(sr.pressure), 0) as avg_pressure,
        COALESCE(SUM(sr.flow_rate * EXTRACT(EPOCH FROM time_range) / 1000), 0) as total_volume_m3,
        (SELECT COUNT(*) FROM anomalies 
         WHERE timestamp > CURRENT_TIMESTAMP - time_range 
         AND resolved_at IS NULL) as anomaly_count
    FROM sensor_readings sr
    WHERE sr.timestamp > CURRENT_TIMESTAMP - time_range;
END;
$$ LANGUAGE plpgsql;

-- Function to get node status
CREATE OR REPLACE FUNCTION get_node_status(
    p_node_id VARCHAR(50)
)
RETURNS TABLE (
    node_id VARCHAR(50),
    node_name VARCHAR(100),
    last_reading TIMESTAMP WITH TIME ZONE,
    is_online BOOLEAN,
    current_flow DECIMAL,
    current_pressure DECIMAL,
    anomaly_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        n.node_id,
        n.node_name,
        MAX(sr.timestamp) as last_reading,
        (MAX(sr.timestamp) > CURRENT_TIMESTAMP - INTERVAL '30 minutes') as is_online,
        COALESCE((
            SELECT flow_rate 
            FROM sensor_readings 
            WHERE node_id = n.node_id 
            ORDER BY timestamp DESC 
            LIMIT 1
        ), 0) as current_flow,
        COALESCE((
            SELECT pressure 
            FROM sensor_readings 
            WHERE node_id = n.node_id 
            ORDER BY timestamp DESC 
            LIMIT 1
        ), 0) as current_pressure,
        (SELECT COUNT(*) 
         FROM anomalies 
         WHERE node_id = n.node_id 
         AND timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
         AND resolved_at IS NULL) as anomaly_count
    FROM nodes n
    LEFT JOIN sensor_readings sr ON n.node_id = sr.node_id
    WHERE n.node_id = p_node_id
    GROUP BY n.node_id, n.node_name;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL ON SCHEMA water_infrastructure TO postgres;
GRANT USAGE ON SCHEMA water_infrastructure TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA water_infrastructure TO PUBLIC;
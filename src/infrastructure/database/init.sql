-- Initialization script for Abbanoa Processing Database
-- This script runs automatically when the PostgreSQL container starts

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create PostGIS extension for spatial data (optional)
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- Create the water_infrastructure schema
CREATE SCHEMA IF NOT EXISTS water_infrastructure;

-- Set search path
SET search_path TO water_infrastructure, public;

-- Create user for application (if different from main user)
-- CREATE USER abbanoa_app WITH PASSWORD 'app_password';
-- GRANT ALL PRIVILEGES ON SCHEMA water_infrastructure TO abbanoa_app;

-- Performance settings for TimescaleDB
ALTER SYSTEM SET shared_preload_libraries = 'timescaledb';
ALTER SYSTEM SET timescaledb.telemetry_level = 'off';

-- Connection settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET effective_cache_size = '3GB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET work_mem = '16MB';

-- TimescaleDB specific settings
ALTER SYSTEM SET timescaledb.max_background_workers = 8;
ALTER SYSTEM SET max_worker_processes = 16;

-- Enable pg_stat_statements for query monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Log settings for debugging
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_duration = 'on';
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries taking more than 1 second

-- Create a function to grant permissions on all tables
CREATE OR REPLACE FUNCTION grant_permissions() RETURNS void AS $$
BEGIN
    -- Grant usage on schema
    GRANT USAGE ON SCHEMA water_infrastructure TO abbanoa_user;
    
    -- Grant all privileges on all tables
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA water_infrastructure TO abbanoa_user;
    
    -- Grant all privileges on all sequences
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA water_infrastructure TO abbanoa_user;
    
    -- Grant execute on all functions
    GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA water_infrastructure TO abbanoa_user;
    
    -- Set default privileges for future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA water_infrastructure 
        GRANT ALL PRIVILEGES ON TABLES TO abbanoa_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA water_infrastructure 
        GRANT ALL PRIVILEGES ON SEQUENCES TO abbanoa_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA water_infrastructure 
        GRANT EXECUTE ON FUNCTIONS TO abbanoa_user;
END;
$$ LANGUAGE plpgsql;

-- Execute the function
SELECT grant_permissions();

-- Create a heartbeat table for monitoring
CREATE TABLE IF NOT EXISTS water_infrastructure.system_heartbeat (
    service_name VARCHAR(50) PRIMARY KEY,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'healthy',
    metadata JSONB
);

-- Insert initial heartbeat
INSERT INTO water_infrastructure.system_heartbeat (service_name, status)
VALUES ('database', 'initialized')
ON CONFLICT (service_name) DO UPDATE
SET last_heartbeat = CURRENT_TIMESTAMP,
    status = 'initialized';
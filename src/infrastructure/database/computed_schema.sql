-- Computed results schema for Abbanoa Water Infrastructure
-- This schema stores pre-computed results from the processing service

-- =====================================================
-- COMPUTED METRICS TABLES
-- =====================================================

-- Aggregated metrics by time window
CREATE TABLE IF NOT EXISTS water_infrastructure.computed_metrics (
    node_id VARCHAR(50) NOT NULL,
    time_window VARCHAR(20) NOT NULL, -- '5min', '1hour', '1day', '1week', '1month'
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Flow metrics
    avg_flow_rate DECIMAL(10, 2),
    min_flow_rate DECIMAL(10, 2),
    max_flow_rate DECIMAL(10, 2),
    total_volume DECIMAL(15, 2),
    flow_variance DECIMAL(10, 4),
    
    -- Pressure metrics
    avg_pressure DECIMAL(6, 2),
    min_pressure DECIMAL(6, 2),
    max_pressure DECIMAL(6, 2),
    pressure_variance DECIMAL(6, 4),
    
    -- Temperature metrics
    avg_temperature DECIMAL(5, 2),
    min_temperature DECIMAL(5, 2),
    max_temperature DECIMAL(5, 2),
    
    -- Quality metrics
    data_completeness DECIMAL(5, 2), -- Percentage of expected data points
    anomaly_count INTEGER DEFAULT 0,
    quality_score DECIMAL(3, 2) DEFAULT 1.0,
    
    -- Metadata
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT '1.0.0',
    
    PRIMARY KEY (node_id, time_window, window_start)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_computed_metrics_window ON water_infrastructure.computed_metrics(time_window, window_start);
CREATE INDEX IF NOT EXISTS idx_computed_metrics_node_window ON water_infrastructure.computed_metrics(node_id, window_start);

-- Network efficiency calculations
CREATE TABLE IF NOT EXISTS water_infrastructure.network_efficiency (
    computation_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    computation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    time_window VARCHAR(20) NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Overall network metrics
    total_input_volume DECIMAL(15, 2),
    total_output_volume DECIMAL(15, 2),
    total_loss_volume DECIMAL(15, 2),
    efficiency_percentage DECIMAL(5, 2),
    
    -- Per-zone metrics (JSONB for flexibility)
    zone_metrics JSONB, -- {zone_id: {input, output, loss, efficiency}}
    
    -- Network health
    active_nodes INTEGER,
    total_nodes INTEGER,
    network_availability DECIMAL(5, 2), -- Percentage
    
    -- Anomaly summary
    total_anomalies INTEGER DEFAULT 0,
    critical_anomalies INTEGER DEFAULT 0,
    anomaly_zones JSONB, -- List of zones with anomalies
    
    -- Metadata
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    computation_version VARCHAR(20) DEFAULT '1.0.0'
);

CREATE INDEX IF NOT EXISTS idx_network_efficiency_window ON water_infrastructure.network_efficiency(window_start, window_end);

-- =====================================================
-- ML MODEL MANAGEMENT TABLES
-- =====================================================

-- Model registry
CREATE TABLE IF NOT EXISTS water_infrastructure.ml_models (
    model_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'flow_prediction', 'anomaly_detection', 'efficiency_optimization'
    version VARCHAR(20) NOT NULL,
    
    -- Training information
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    training_started_at TIMESTAMP WITH TIME ZONE,
    training_completed_at TIMESTAMP WITH TIME ZONE,
    training_duration_seconds INTEGER,
    
    -- Model status
    status VARCHAR(20) NOT NULL DEFAULT 'created', -- 'created', 'training', 'validating', 'shadow', 'active', 'retired'
    is_active BOOLEAN DEFAULT FALSE,
    activated_at TIMESTAMP WITH TIME ZONE,
    retired_at TIMESTAMP WITH TIME ZONE,
    
    -- Performance metrics
    metrics JSONB, -- {rmse: 0.95, mae: 0.87, mape: 5.2, r2: 0.92}
    validation_metrics JSONB,
    
    -- Training configuration
    parameters JSONB, -- hyperparameters, feature list, etc.
    training_data_start TIMESTAMP WITH TIME ZONE,
    training_data_end TIMESTAMP WITH TIME ZONE,
    training_samples INTEGER,
    
    -- Model storage
    model_path VARCHAR(500), -- S3/MinIO/local path
    model_size_bytes BIGINT,
    model_hash VARCHAR(64), -- SHA256 of model file
    
    -- Additional metadata
    description TEXT,
    created_by VARCHAR(100) DEFAULT 'system',
    tags JSONB, -- ['production', 'experimental', etc.]
    
    UNIQUE(model_type, version)
);

CREATE INDEX IF NOT EXISTS idx_ml_models_type_status ON water_infrastructure.ml_models(model_type, status);
CREATE INDEX IF NOT EXISTS idx_ml_models_active ON water_infrastructure.ml_models(is_active) WHERE is_active = TRUE;

-- Model performance tracking
CREATE TABLE IF NOT EXISTS water_infrastructure.model_performance (
    model_id UUID REFERENCES water_infrastructure.ml_models(model_id),
    evaluation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    evaluation_window VARCHAR(20) NOT NULL, -- 'hourly', 'daily', 'weekly'
    
    -- Performance metrics
    predictions_count INTEGER,
    rmse DECIMAL(10, 4),
    mae DECIMAL(10, 4),
    mape DECIMAL(5, 2), -- Mean Absolute Percentage Error
    r2_score DECIMAL(5, 4),
    
    -- Detailed metrics by node/zone
    node_metrics JSONB, -- {node_id: {rmse, mae, count}}
    
    -- Drift detection
    feature_drift_score DECIMAL(5, 4),
    prediction_drift_score DECIMAL(5, 4),
    drift_detected BOOLEAN DEFAULT FALSE,
    
    PRIMARY KEY (model_id, evaluation_timestamp, evaluation_window)
);

CREATE INDEX IF NOT EXISTS idx_model_performance_timestamp ON water_infrastructure.model_performance(evaluation_timestamp);

-- Model predictions cache
CREATE TABLE IF NOT EXISTS water_infrastructure.ml_predictions_cache (
    prediction_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_id UUID REFERENCES water_infrastructure.ml_models(model_id),
    node_id VARCHAR(50) NOT NULL,
    
    -- Prediction details
    prediction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    prediction_horizon_hours INTEGER NOT NULL,
    target_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Predictions
    predicted_flow_rate DECIMAL(10, 2),
    predicted_pressure DECIMAL(6, 2),
    predicted_temperature DECIMAL(5, 2),
    
    -- Confidence intervals
    flow_rate_lower DECIMAL(10, 2),
    flow_rate_upper DECIMAL(10, 2),
    pressure_lower DECIMAL(6, 2),
    pressure_upper DECIMAL(6, 2),
    
    -- Metadata
    confidence_score DECIMAL(3, 2),
    features_used JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we don't duplicate predictions
    UNIQUE(model_id, node_id, target_timestamp)
);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_lookup ON water_infrastructure.ml_predictions_cache(node_id, target_timestamp);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_timestamp ON water_infrastructure.ml_predictions_cache(prediction_timestamp);

-- =====================================================
-- PROCESSING STATUS TABLES
-- =====================================================

-- Processing job tracking
CREATE TABLE IF NOT EXISTS water_infrastructure.processing_jobs (
    job_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL, -- 'metrics_computation', 'ml_training', 'anomaly_detection'
    job_name VARCHAR(200),
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'queued', -- 'queued', 'running', 'completed', 'failed'
    priority INTEGER DEFAULT 5, -- 1-10, higher is more important
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Progress tracking
    total_items INTEGER,
    processed_items INTEGER,
    failed_items INTEGER,
    progress_percentage DECIMAL(5, 2),
    
    -- Data range being processed
    data_start_time TIMESTAMP WITH TIME ZONE,
    data_end_time TIMESTAMP WITH TIME ZONE,
    
    -- Results and errors
    result_summary JSONB,
    error_message TEXT,
    error_details JSONB,
    
    -- Metadata
    triggered_by VARCHAR(50) DEFAULT 'scheduler', -- 'scheduler', 'manual', 'event'
    configuration JSONB
);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON water_infrastructure.processing_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_type ON water_infrastructure.processing_jobs(job_type, status);

-- Data quality tracking
CREATE TABLE IF NOT EXISTS water_infrastructure.data_quality_metrics (
    node_id VARCHAR(50) NOT NULL,
    check_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    time_window VARCHAR(20) NOT NULL,
    
    -- Quality metrics
    completeness_score DECIMAL(3, 2), -- 0-1, percentage of expected data
    validity_score DECIMAL(3, 2), -- 0-1, percentage of valid values
    consistency_score DECIMAL(3, 2), -- 0-1, consistency with historical patterns
    overall_quality_score DECIMAL(3, 2), -- 0-1, weighted average
    
    -- Issue tracking
    missing_data_points INTEGER DEFAULT 0,
    invalid_values INTEGER DEFAULT 0,
    outliers_detected INTEGER DEFAULT 0,
    
    -- Detailed issues
    quality_issues JSONB, -- [{type, severity, description, timestamp}]
    
    PRIMARY KEY (node_id, check_timestamp, time_window)
);

CREATE INDEX IF NOT EXISTS idx_data_quality_timestamp ON water_infrastructure.data_quality_metrics(check_timestamp);
CREATE INDEX IF NOT EXISTS idx_data_quality_score ON water_infrastructure.data_quality_metrics(overall_quality_score);

-- =====================================================
-- FUNCTIONS FOR COMPUTED DATA ACCESS
-- =====================================================

-- Function to get latest computed metrics for a node
CREATE OR REPLACE FUNCTION water_infrastructure.get_latest_computed_metrics(
    p_node_id VARCHAR(50),
    p_time_window VARCHAR(20) DEFAULT '1hour'
)
RETURNS TABLE (
    node_id VARCHAR(50),
    window_start TIMESTAMP WITH TIME ZONE,
    window_end TIMESTAMP WITH TIME ZONE,
    avg_flow_rate DECIMAL(10, 2),
    avg_pressure DECIMAL(6, 2),
    total_volume DECIMAL(15, 2),
    anomaly_count INTEGER,
    quality_score DECIMAL(3, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cm.node_id,
        cm.window_start,
        cm.window_end,
        cm.avg_flow_rate,
        cm.avg_pressure,
        cm.total_volume,
        cm.anomaly_count,
        cm.quality_score
    FROM water_infrastructure.computed_metrics cm
    WHERE cm.node_id = p_node_id
    AND cm.time_window = p_time_window
    ORDER BY cm.window_start DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to get active ML model for a type
CREATE OR REPLACE FUNCTION water_infrastructure.get_active_model(
    p_model_type VARCHAR(50)
)
RETURNS TABLE (
    model_id UUID,
    version VARCHAR(20),
    metrics JSONB,
    model_path VARCHAR(500)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.model_id,
        m.version,
        m.metrics,
        m.model_path
    FROM water_infrastructure.ml_models m
    WHERE m.model_type = p_model_type
    AND m.is_active = TRUE
    AND m.status = 'active'
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
-- Performance indexes for prediction tracking system
-- Run this after implementing the tracking system

-- Index for fast lookups by prediction outcome status
CREATE INDEX IF NOT EXISTS idx_ml_predictions_outcome_status 
ON water_infrastructure.ml_predictions(actual_occurred, feedback_at)
WHERE actual_occurred IS NOT NULL;

-- Index for fast lookups by feedback source
CREATE INDEX IF NOT EXISTS idx_ml_predictions_feedback_source 
ON water_infrastructure.ml_predictions(feedback_source, created_at)
WHERE feedback_source IS NOT NULL;

-- Index for fast time-based queries on outcomes
CREATE INDEX IF NOT EXISTS idx_ml_predictions_outcome_timestamp 
ON water_infrastructure.ml_predictions(outcome_timestamp DESC)
WHERE outcome_timestamp IS NOT NULL;

-- Composite index for reconciliation queries
CREATE INDEX IF NOT EXISTS idx_ml_predictions_reconciliation 
ON water_infrastructure.ml_predictions(node_id, predicted_timestamp)
WHERE actual_occurred IS NULL;

-- Index for performance metrics calculation
CREATE INDEX IF NOT EXISTS idx_ml_predictions_metrics 
ON water_infrastructure.ml_predictions(created_at, probability, actual_occurred)
WHERE feedback_at IS NOT NULL;

-- Indexes for operator feedback table
CREATE INDEX IF NOT EXISTS idx_operator_feedback_prediction 
ON water_infrastructure.operator_feedback(prediction_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_operator_feedback_operator_time 
ON water_infrastructure.operator_feedback(operator_id, created_at DESC);

-- Index for performance metrics history
CREATE INDEX IF NOT EXISTS idx_performance_metrics_time_version 
ON water_infrastructure.model_performance_metrics(calculated_at DESC, model_version);

-- Index for performance alerts
CREATE INDEX IF NOT EXISTS idx_performance_alerts_type_time 
ON water_infrastructure.performance_alerts(alert_type, created_at DESC);

-- Partial index for unresolved predictions (most common query)
CREATE INDEX IF NOT EXISTS idx_ml_predictions_unresolved 
ON water_infrastructure.ml_predictions(predicted_timestamp, node_id)
WHERE actual_occurred IS NULL AND predicted_timestamp < NOW();

-- Statistics update (run after creating indexes)
ANALYZE water_infrastructure.ml_predictions;
ANALYZE water_infrastructure.operator_feedback;
ANALYZE water_infrastructure.model_performance_metrics;
ANALYZE water_infrastructure.performance_alerts;
# ARIMA_PLUS Operational Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Model Deployment](#model-deployment)
4. [Daily Operations](#daily-operations)
5. [Monitoring & Alerts](#monitoring--alerts)
6. [Troubleshooting](#troubleshooting)
7. [Model Retraining](#model-retraining)
8. [Performance Optimization](#performance-optimization)

## Quick Start

### Generate 7-Day Forecasts (Production)

```bash
# Option 1: Using BigQuery Console
bq query --use_legacy_sql=false < notebooks/forecast_baseline.sql

# Option 2: Using deployment script
./scripts/deploy/deploy_ml_models.sh prod execute

# Option 3: Manual execution via Python
poetry run python notebooks/execute_forecast_baseline.py
```

### View Current Forecasts

```sql
-- BigQuery Console
SELECT 
  district_id,
  metric_type,
  forecast_date,
  forecast_value,
  lower_bound,
  upper_bound
FROM `abbanoa-464816.ml_models.current_forecasts`
WHERE forecast_date >= CURRENT_DATE()
ORDER BY district_id, metric_type, forecast_date;
```

## Prerequisites

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/abbanoa/water-infrastructure.git
cd water-infrastructure

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Configure Google Cloud
gcloud auth login
gcloud config set project abbanoa-464816
```

### 2. Required Permissions

- **BigQuery Data Editor**: Create/modify ML models
- **BigQuery Job User**: Execute queries
- **BigQuery Data Viewer**: Read results

```bash
# Grant permissions (admin only)
gcloud projects add-iam-policy-binding abbanoa-464816 \
  --member="user:your-email@domain.com" \
  --role="roles/bigquery.dataEditor"
```

### 3. Data Requirements

- **View Dependency**: `water_infrastructure.vw_daily_timeseries` must exist
- **Minimum History**: 2 years of data per district-metric
- **Data Quality**: >95% completeness in last 90 days

## Model Deployment

### Step-by-Step Deployment Process

#### 1. Pre-Deployment Validation

```bash
# Validate environment and data
./scripts/deploy/deploy_ml_models.sh prod validate

# Expected output:
# ✅ All prerequisites met
# ✅ Data validation passed
# ✅ Model requirements validation passed
# ✅ SQL notebook validation passed
```

#### 2. Deploy Models

```bash
# Full deployment (creates all 6 models)
./scripts/deploy/deploy_ml_models.sh prod execute

# Dry run (test without execution)
DRY_RUN=true ./scripts/deploy/deploy_ml_models.sh prod execute
```

#### 3. Verify Deployment

```sql
-- Check model creation
SELECT 
  model_name,
  model_type,
  creation_time,
  training_options
FROM `abbanoa-464816.ml_models.INFORMATION_SCHEMA.MODELS`
WHERE model_type = 'ARIMA_PLUS';

-- Verify model performance
SELECT * FROM `abbanoa-464816.ml_models.model_evaluation`
ORDER BY model_name;
```

### Model Configuration Details

Each model is configured with:
- **Horizon**: 7 days
- **Auto-ARIMA**: Automatic parameter selection
- **Holiday Region**: Italy ('IT')
- **Features**: Spike cleaning, drift adjustment, seasonal decomposition

## Daily Operations

### 1. Generate Daily Forecasts

Create a scheduled query in BigQuery:

```sql
-- Schedule: Daily at 6:00 AM
CREATE OR REPLACE TABLE `abbanoa-464816.ml_models.daily_forecasts_${run_date}`
PARTITION BY forecast_date
AS
WITH forecasts AS (
  SELECT * FROM ML.FORECAST(MODEL `ml_models.arima_dist001_flow_rate`, STRUCT(7 AS horizon))
  UNION ALL
  SELECT * FROM ML.FORECAST(MODEL `ml_models.arima_dist001_pressure`, STRUCT(7 AS horizon))
  UNION ALL
  SELECT * FROM ML.FORECAST(MODEL `ml_models.arima_dist001_reservoir_level`, STRUCT(7 AS horizon))
  UNION ALL
  SELECT * FROM ML.FORECAST(MODEL `ml_models.arima_dist002_flow_rate`, STRUCT(7 AS horizon))
  UNION ALL
  SELECT * FROM ML.FORECAST(MODEL `ml_models.arima_dist002_pressure`, STRUCT(7 AS horizon))
  UNION ALL
  SELECT * FROM ML.FORECAST(MODEL `ml_models.arima_dist002_reservoir_level`, STRUCT(7 AS horizon))
)
SELECT 
  CURRENT_TIMESTAMP() as generation_timestamp,
  REGEXP_EXTRACT(model_name, r'(DIST_\d+)') as district_id,
  REGEXP_EXTRACT(model_name, r'DIST_\d+_(.+)') as metric_type,
  forecast_timestamp as forecast_date,
  forecast_value,
  prediction_interval_lower_bound as lower_bound,
  prediction_interval_upper_bound as upper_bound,
  standard_error,
  confidence_level
FROM forecasts;
```

### 2. Export Forecasts for Dashboard

```python
# export_forecasts.py
from google.cloud import bigquery
import pandas as pd
from datetime import datetime

client = bigquery.Client(project="abbanoa-464816")

# Query latest forecasts
query = """
SELECT 
  district_id,
  metric_type,
  forecast_date,
  forecast_value,
  lower_bound,
  upper_bound
FROM `abbanoa-464816.ml_models.current_forecasts`
WHERE forecast_generated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY district_id, metric_type, forecast_date
"""

df = client.query(query).to_dataframe()

# Export to CSV for dashboard
df.to_csv(f'forecasts_{datetime.now().strftime("%Y%m%d")}.csv', index=False)

# Export to Google Sheets (optional)
# df.to_gbq('dashboard.forecast_data', if_exists='replace')
```

### 3. Operational Checklist

**Daily Tasks:**
- [ ] Verify forecast generation completed
- [ ] Check model performance metrics
- [ ] Review anomaly alerts
- [ ] Update operational dashboard

**Weekly Tasks:**
- [ ] Review model accuracy trends
- [ ] Analyze forecast vs actual comparisons
- [ ] Generate performance report
- [ ] Plan model retraining if needed

## Monitoring & Alerts

### 1. Model Performance Monitoring

```sql
-- Create monitoring view
CREATE OR REPLACE VIEW `ml_models.model_performance_monitor` AS
WITH daily_performance AS (
  SELECT 
    DATE(forecast_date) as date,
    district_id,
    metric_type,
    AVG(ABS(actual_value - forecast_value) / NULLIF(actual_value, 0)) as daily_mape,
    COUNT(*) as prediction_count
  FROM `ml_models.forecast_vs_actual`
  WHERE forecast_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY date, district_id, metric_type
)
SELECT 
  *,
  CASE 
    WHEN daily_mape > 0.25 THEN 'CRITICAL'
    WHEN daily_mape > 0.20 THEN 'WARNING'
    WHEN daily_mape > 0.15 THEN 'ATTENTION'
    ELSE 'GOOD'
  END as performance_status
FROM daily_performance;
```

### 2. Alert Configuration

```python
# monitoring/alert_config.py
ALERT_THRESHOLDS = {
    'daily_mape': {
        'critical': 0.25,  # 25% MAPE
        'warning': 0.20,   # 20% MAPE
        'attention': 0.15  # 15% MAPE
    },
    'consecutive_failures': {
        'critical': 3,     # 3 consecutive days
        'warning': 2       # 2 consecutive days
    },
    'data_freshness': {
        'critical': 48,    # 48 hours
        'warning': 24      # 24 hours
    }
}

# Alert query
PERFORMANCE_ALERT_QUERY = """
SELECT 
  district_id,
  metric_type,
  AVG(daily_mape) as avg_mape_7d,
  MAX(daily_mape) as max_mape_7d,
  COUNT(CASE WHEN performance_status != 'GOOD' THEN 1 END) as days_above_threshold
FROM `ml_models.model_performance_monitor`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY district_id, metric_type
HAVING avg_mape_7d > 0.15 OR days_above_threshold > 2
"""
```

### 3. Automated Alerting

```bash
# Create Cloud Monitoring alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="ARIMA Model Performance Alert" \
  --condition-type=metric-threshold \
  --condition-metric-type="custom.googleapis.com/bigquery/model/mape" \
  --condition-threshold-value=0.20 \
  --condition-threshold-duration=3600s
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Model Training Failures

**Symptom**: Model creation fails with timeout
```
Error: Query exceeded resource limits
```

**Solution**:
```bash
# Increase timeout and reduce data size
poetry run python notebooks/execute_forecast_baseline.py \
  --timeout=3600 \
  --sample-rate=0.8
```

#### 2. Poor Forecast Accuracy

**Symptom**: MAPE > 20% consistently

**Diagnosis**:
```sql
-- Check data quality
SELECT 
  district_id,
  metric_type,
  COUNT(CASE WHEN gap_filled_flag THEN 1 END) / COUNT(*) as gap_fill_rate,
  AVG(data_completeness_pct) as avg_completeness,
  COUNT(DISTINCT date_utc) as days_with_data
FROM `water_infrastructure.vw_daily_timeseries`
WHERE date_utc >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY district_id, metric_type;

-- Check for anomalies
SELECT 
  date_utc,
  district_id,
  metric_type,
  avg_value,
  LAG(avg_value) OVER (PARTITION BY district_id, metric_type ORDER BY date_utc) as prev_value,
  ABS(avg_value - LAG(avg_value) OVER (PARTITION BY district_id, metric_type ORDER BY date_utc)) / 
    NULLIF(LAG(avg_value) OVER (PARTITION BY district_id, metric_type ORDER BY date_utc), 0) as change_rate
FROM `water_infrastructure.vw_daily_timeseries`
WHERE date_utc >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND district_id = 'DIST_001'
  AND metric_type = 'flow_rate'
HAVING change_rate > 0.5;  -- 50% change
```

**Solutions**:
1. Retrain model with clean data
2. Adjust anomaly detection parameters
3. Consider ensemble approach

#### 3. Missing Forecasts

**Symptom**: No forecasts generated for specific date

**Diagnosis**:
```bash
# Check scheduled query logs
bq ls -j --max_results=10 --format=prettyjson | grep forecast

# Check model status
bq show --model abbanoa-464816:ml_models.arima_dist001_flow_rate
```

**Solution**:
```sql
-- Manually generate missing forecasts
INSERT INTO `ml_models.current_forecasts`
SELECT * FROM ML.FORECAST(
  MODEL `ml_models.arima_dist001_flow_rate`,
  STRUCT(7 AS horizon)
);
```

## Model Retraining

### When to Retrain

1. **Scheduled Retraining**: Monthly (first Sunday)
2. **Performance-Based**: When 7-day avg MAPE > 18%
3. **Data-Driven**: After significant infrastructure changes
4. **Seasonal**: Before summer/winter seasons

### Retraining Process

```bash
# 1. Create new model version
export MODEL_VERSION=$(date +%Y%m%d)

# 2. Execute retraining
./scripts/deploy/deploy_ml_models.sh prod execute \
  --model-suffix="_v${MODEL_VERSION}"

# 3. Validate new models
poetry run python notebooks/validate_models.py \
  --version="${MODEL_VERSION}"

# 4. A/B test (optional)
./scripts/deploy/ab_test_models.sh \
  --baseline="production" \
  --challenger="v${MODEL_VERSION}" \
  --duration-days=7

# 5. Promote if successful
./scripts/deploy/promote_models.sh \
  --version="${MODEL_VERSION}"
```

### Automated Retraining Pipeline

```python
# retraining/automated_pipeline.py
from datetime import datetime, timedelta
import logging

class ModelRetrainingPipeline:
    def __init__(self, project_id="abbanoa-464816"):
        self.project_id = project_id
        self.dataset_id = "ml_models"
        
    def should_retrain(self, model_name):
        """Check if model needs retraining"""
        # Check performance
        performance_check = f"""
        SELECT AVG(mape) as avg_mape
        FROM `{self.project_id}.{self.dataset_id}.model_performance_daily`
        WHERE model_name = '{model_name}'
          AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
        """
        
        # Check last training date
        training_check = f"""
        SELECT creation_time
        FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.MODELS`
        WHERE model_name = '{model_name}'
        """
        
        # Logic to determine retraining need
        return True  # Simplified
        
    def retrain_model(self, model_name):
        """Execute model retraining"""
        logging.info(f"Starting retraining for {model_name}")
        
        # Implementation details...
        
        return True
```

## Performance Optimization

### 1. Query Optimization

```sql
-- Use partitioned tables for forecasts
CREATE TABLE `ml_models.forecasts_partitioned`
PARTITION BY DATE(forecast_date)
CLUSTER BY district_id, metric_type
AS SELECT * FROM `ml_models.current_forecasts`;

-- Materialized view for common queries
CREATE MATERIALIZED VIEW `ml_models.forecast_summary_mv`
REFRESH INTERVAL 1 HOUR
AS
SELECT 
  district_id,
  metric_type,
  DATE(forecast_date) as date,
  AVG(forecast_value) as daily_avg_forecast,
  MIN(lower_bound) as daily_min_bound,
  MAX(upper_bound) as daily_max_bound
FROM `ml_models.forecasts_partitioned`
WHERE forecast_date >= CURRENT_DATE()
GROUP BY district_id, metric_type, DATE(forecast_date);
```

### 2. Cost Optimization

```python
# cost_optimization.py
COST_SAVING_STRATEGIES = {
    'use_slots': True,  # Use flat-rate pricing for ML
    'enable_caching': True,
    'partition_tables': True,
    'cluster_by_common_filters': True,
    'materialized_views': True,
    'scheduled_queries': {
        'frequency': 'daily',
        'time': '06:00',
        'time_zone': 'Europe/Rome'
    }
}

# Estimate monthly costs
def estimate_ml_costs():
    """
    Model Training: ~$10/model/month = $60
    Daily Forecasts: ~$0.50/day = $15/month
    Storage: ~$5/month
    Total: ~$80/month
    """
    pass
```

### 3. Performance Benchmarks

| Operation | Target Time | Current Performance |
|-----------|-------------|-------------------|
| Single Model Training | < 5 min | 3-4 min |
| All Models Training | < 30 min | 20-25 min |
| 7-Day Forecast Generation | < 30 sec | 15-20 sec |
| Dashboard Query | < 2 sec | 1-1.5 sec |

## Appendix

### A. SQL Quick Reference

```sql
-- Generate forecast for single model
SELECT * FROM ML.FORECAST(
  MODEL `ml_models.arima_dist001_flow_rate`,
  STRUCT(7 AS horizon)
);

-- Evaluate model performance
SELECT * FROM ML.EVALUATE(
  MODEL `ml_models.arima_dist001_flow_rate`
);

-- Get model info
SELECT * FROM ML.TRAINING_INFO(
  MODEL `ml_models.arima_dist001_flow_rate`
);

-- Explain forecast
SELECT * FROM ML.EXPLAIN_FORECAST(
  MODEL `ml_models.arima_dist001_flow_rate`,
  STRUCT(7 AS horizon)
);
```

### B. Python Helper Functions

```python
# helpers/forecast_utils.py
def get_latest_forecasts(district_id, metric_type):
    """Get latest 7-day forecasts for specific district-metric"""
    query = f"""
    SELECT * FROM `ml_models.current_forecasts`
    WHERE district_id = '{district_id}'
      AND metric_type = '{metric_type}'
      AND forecast_date >= CURRENT_DATE()
    ORDER BY forecast_date
    """
    return client.query(query).to_dataframe()

def calculate_forecast_accuracy(forecast_df, actual_df):
    """Calculate MAPE for forecast vs actual"""
    merged = forecast_df.merge(actual_df, on=['date', 'district_id', 'metric_type'])
    merged['ape'] = abs(merged['actual'] - merged['forecast']) / merged['actual']
    return merged['ape'].mean()
```

### C. Emergency Procedures

**Model Failure Recovery:**
1. Switch to fallback statistical model
2. Use 7-day moving average as temporary forecast
3. Alert on-call engineer
4. Investigate root cause
5. Retrain or rollback model

**Data Pipeline Failure:**
1. Check vw_daily_timeseries view status
2. Verify source data availability
3. Run manual data refresh
4. Generate forecasts with available data
5. Document incident

---

**Support Contact:**
- Data Engineering Team: data-eng@abbanoa.it
- On-Call: +39-XXX-XXXXXXX
- Slack: #ml-models-support
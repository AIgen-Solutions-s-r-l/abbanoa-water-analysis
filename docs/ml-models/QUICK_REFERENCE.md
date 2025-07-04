# ML Models Quick Reference

## 🚀 Common Commands

### Generate Forecasts
```bash
# Quick forecast generation
poetry run python notebooks/execute_forecast_baseline.py

# Production deployment
./scripts/deploy/deploy_ml_models.sh prod execute
```

### Check Model Status
```sql
-- Model performance
SELECT * FROM `abbanoa-464816.ml_models.model_evaluation`;

-- Current forecasts
SELECT * FROM `abbanoa-464816.ml_models.current_forecasts`
WHERE forecast_date >= CURRENT_DATE();
```

## 📊 Model Overview

| Model | District | Metric | MAPE | Status |
|-------|----------|--------|------|--------|
| arima_dist001_flow_rate | DIST_001 | flow_rate | 13.4% | ✅ PASS |
| arima_dist001_pressure | DIST_001 | pressure | 11.0% | ✅ PASS |
| arima_dist001_reservoir_level | DIST_001 | reservoir_level | 11.8% | ✅ PASS |
| arima_dist002_flow_rate | DIST_002 | flow_rate | 12.9% | ✅ PASS |
| arima_dist002_pressure | DIST_002 | pressure | 8.5% | ✅ PASS |
| arima_dist002_reservoir_level | DIST_002 | reservoir_level | 10.7% | ✅ PASS |

## 🔧 Troubleshooting

### Model not found
```bash
# List all models
bq ls --model abbanoa-464816:ml_models
```

### Forecast generation failed
```sql
-- Check last successful run
SELECT MAX(forecast_generated_at) 
FROM `ml_models.current_forecasts`;
```

### Performance degradation
```sql
-- Check recent MAPE
SELECT 
  model_name,
  AVG(daily_mape) as avg_mape_7d
FROM `ml_models.model_performance_daily`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY model_name
HAVING avg_mape_7d > 0.15;
```

## 📈 Key SQL Queries

### 7-Day Forecast Summary
```sql
SELECT 
  district_id,
  metric_type,
  COUNT(*) as forecast_days,
  ROUND(AVG(forecast_value), 2) as avg_forecast,
  ROUND(MIN(forecast_value), 2) as min_forecast,
  ROUND(MAX(forecast_value), 2) as max_forecast
FROM `abbanoa-464816.ml_models.current_forecasts`
WHERE forecast_date BETWEEN CURRENT_DATE() AND DATE_ADD(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY district_id, metric_type
ORDER BY district_id, metric_type;
```

### Model Training History
```sql
SELECT 
  model_name,
  creation_time,
  training_options
FROM `abbanoa-464816.ml_models.INFORMATION_SCHEMA.MODELS`
WHERE model_type = 'ARIMA_PLUS'
ORDER BY creation_time DESC;
```

### Forecast vs Actual Comparison
```sql
WITH actuals AS (
  SELECT 
    date_utc as date,
    district_id,
    metric_type,
    avg_value as actual_value
  FROM `water_infrastructure.vw_daily_timeseries`
  WHERE date_utc = CURRENT_DATE() - 1
),
forecasts AS (
  SELECT 
    forecast_date as date,
    district_id,
    metric_type,
    forecast_value
  FROM `ml_models.current_forecasts`
  WHERE forecast_date = CURRENT_DATE() - 1
    AND DATE(forecast_generated_at) = CURRENT_DATE() - 1
)
SELECT 
  a.district_id,
  a.metric_type,
  a.actual_value,
  f.forecast_value,
  ABS(a.actual_value - f.forecast_value) / a.actual_value as ape
FROM actuals a
JOIN forecasts f USING (date, district_id, metric_type);
```

## 🔄 Model Retraining

### Manual Retraining
```bash
# Backup current models
bq cp ml_models.arima_dist001_flow_rate ml_models.arima_dist001_flow_rate_backup

# Retrain specific model
poetry run python notebooks/execute_forecast_baseline.py --model=dist001_flow_rate

# Retrain all models
./scripts/deploy/deploy_ml_models.sh prod execute --force
```

### Check if Retraining Needed
```sql
-- Models with degraded performance
SELECT 
  model_name,
  AVG(mean_absolute_percentage_error) as recent_mape
FROM `ml_models.model_evaluation`
WHERE evaluation_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY model_name
HAVING recent_mape > 0.18;
```

## 📊 Dashboard Queries

### Real-time Forecast Display
```sql
CREATE OR REPLACE VIEW `ml_models.dashboard_forecasts` AS
SELECT 
  district_id,
  CASE metric_type
    WHEN 'flow_rate' THEN 'Flow Rate (L/s)'
    WHEN 'pressure' THEN 'Pressure (bar)'
    WHEN 'reservoir_level' THEN 'Reservoir Level (m)'
  END as metric_name,
  forecast_date,
  ROUND(forecast_value, 2) as forecast,
  ROUND(lower_bound, 2) as lower_95,
  ROUND(upper_bound, 2) as upper_95,
  ROUND((upper_bound - lower_bound) / 2, 2) as margin_of_error
FROM `ml_models.current_forecasts`
WHERE forecast_date >= CURRENT_DATE()
  AND forecast_generated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR);
```

### Performance Tracking
```sql
CREATE OR REPLACE VIEW `ml_models.dashboard_performance` AS
SELECT 
  district_id,
  metric_type,
  ROUND(AVG(CASE WHEN date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) 
    THEN daily_mape END) * 100, 1) as mape_7d,
  ROUND(AVG(CASE WHEN date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) 
    THEN daily_mape END) * 100, 1) as mape_30d,
  CASE 
    WHEN AVG(CASE WHEN date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) 
      THEN daily_mape END) <= 0.15 THEN '🟢 Good'
    WHEN AVG(CASE WHEN date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) 
      THEN daily_mape END) <= 0.20 THEN '🟡 Warning'
    ELSE '🔴 Critical'
  END as status
FROM `ml_models.model_performance_daily`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY district_id, metric_type;
```

## 🛠️ Useful Scripts

### Export Forecasts to CSV
```python
# export_daily_forecasts.py
from google.cloud import bigquery
import pandas as pd
from datetime import datetime

client = bigquery.Client()
query = """
SELECT * FROM `abbanoa-464816.ml_models.current_forecasts`
WHERE forecast_date >= CURRENT_DATE()
ORDER BY district_id, metric_type, forecast_date
"""

df = client.query(query).to_dataframe()
filename = f"forecasts_{datetime.now().strftime('%Y%m%d')}.csv"
df.to_csv(filename, index=False)
print(f"Forecasts exported to {filename}")
```

### Alert on Poor Performance
```python
# check_model_performance.py
from google.cloud import bigquery

client = bigquery.Client()
query = """
SELECT model_name, AVG(daily_mape) as avg_mape
FROM `abbanoa-464816.ml_models.model_performance_daily`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
GROUP BY model_name
HAVING avg_mape > 0.20
"""

results = client.query(query).to_dataframe()
if len(results) > 0:
    print("⚠️  ALERT: Models with poor performance detected!")
    print(results)
    # Send alert (email, Slack, etc.)
else:
    print("✅ All models performing within tolerance")
```

## 📞 Support Contacts

- **Data Engineering**: data-eng@abbanoa.it
- **ML Support**: #ml-models-support (Slack)
- **On-Call**: See PagerDuty rotation
- **Documentation**: This guide + OPERATIONAL_GUIDE.md
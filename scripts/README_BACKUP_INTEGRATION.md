# Backup Data Integration for ML/AI Processing

This document describes the process for integrating the backup sensor data from `RAWDATA/NEW_DATA/BACKUP` into BigQuery for ML/AI processing.

## Overview

The backup directory contains sensor readings from multiple monitoring nodes in various CSV formats. The integration pipeline normalizes this data and loads it into BigQuery tables optimized for ML/AI algorithms.

## Data Sources

The backup data includes readings from 6 monitoring nodes:
- **215542**: Selargius distribution node
- **215600**: Selargius distribution node  
- **273933**: Selargius distribution node
- **281492**: Selargius monitoring node
- **288399**: Selargius monitoring node
- **288400**: Selargius monitoring node

### File Formats

1. **DATA_LOG files** (`*_DATA_LOG.csv`): Standard sensor readings with 15-second intervals
2. **PROCESS_DATA files** (`*_PROCESS_DATA.csv`): Processed data with additional metrics
3. **D_LOGGER_FORMAT files** (`*_D_LOGGER_FORMAT.csv`): Diagnostic/configuration data

## Integration Process

### 1. Run the Data Processing Script

```bash
cd /home/alessio/Customers/Abbanoa
python scripts/process_backup_data.py
```

This script will:
- Process all backup directories in parallel
- Normalize different CSV formats
- Calculate data quality scores
- Load data into BigQuery table `sensor_readings_ml`
- Create ML-optimized views

### 2. Validate the Integration

```bash
python scripts/validate_ml_data.py
```

This will generate:
- ML readiness score (0-100)
- Data quality report
- Feature distribution plots
- Validation reports in `reports/ml_data_validation/`

## BigQuery Schema

### Main Table: `sensor_readings_ml`

| Field | Type | Description |
|-------|------|-------------|
| timestamp | TIMESTAMP | Reading timestamp (UTC) |
| node_id | STRING | Sensor node identifier |
| district_id | STRING | District name (e.g., "Selargius") |
| node_name | STRING | Human-readable node name |
| node_type | STRING | Node type (distribution/monitoring) |
| flow_rate | FLOAT64 | Water flow rate (L/s) |
| pressure | FLOAT64 | Water pressure (bar) |
| temperature | FLOAT64 | Water temperature (°C) |
| volume | FLOAT64 | Cumulative volume (m³) |
| data_quality_score | FLOAT64 | Quality score (0-1) |
| is_interpolated | BOOLEAN | Whether data was interpolated |
| source_file | STRING | Original CSV filename |
| ingestion_timestamp | TIMESTAMP | When data was loaded |

### ML-Ready Views

1. **`v_sensor_readings_normalized`**: Cleaned and normalized readings for ML training
2. **`v_daily_metrics_ml`**: Daily aggregated metrics for time series analysis

## Data Quality Metrics

The pipeline calculates quality scores based on:
- Completeness of measurements
- Value range validation
- Temporal consistency
- Outlier detection

## ML/AI Compatibility

The integrated data is optimized for:
- **Time Series Forecasting**: ARIMA, Prophet, LSTM models
- **Anomaly Detection**: Isolation Forest, Autoencoders
- **Pattern Recognition**: Clustering, classification
- **Predictive Maintenance**: Regression models

## Monitoring and Maintenance

### Check Data Freshness
```sql
SELECT 
  MAX(timestamp) as latest_reading,
  COUNT(DISTINCT DATE(timestamp)) as days_with_data
FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

### Monitor Data Quality
```sql
SELECT 
  district_id,
  AVG(data_quality_score) as avg_quality,
  COUNT(*) as reading_count
FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
WHERE DATE(timestamp) = CURRENT_DATE()
GROUP BY district_id
```

## Troubleshooting

### Common Issues

1. **Empty dataframes**: Check if CSV files have data
2. **Timestamp parsing errors**: Verify date format in CSV files
3. **Low quality scores**: Review outlier thresholds in `calculate_data_quality_score()`

### Logs

Processing logs are written to console. Redirect to file for debugging:
```bash
python scripts/process_backup_data.py > processing.log 2>&1
```

## Next Steps

1. Schedule regular data ingestion (e.g., daily cron job)
2. Set up data quality alerts
3. Train ML models on the integrated data
4. Create automated anomaly detection pipeline
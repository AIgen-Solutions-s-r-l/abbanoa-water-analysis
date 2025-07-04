#!/bin/bash

# BigQuery ingestion commands
# Update PROJECT_ID before running!

PROJECT_ID="your-gcp-project-id"

# Create dataset
bq mk --dataset --location=EU your-gcp-project-id:water_infrastructure

# Create table with schema
bq mk --table \
  --schema=bigquery_schema.json \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=_source_file,timestamp \
  your-gcp-project-id:water_infrastructure.sensor_data

# Load data
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --allow_quoted_newlines \
  --max_bad_records=10 \
  your-gcp-project-id:water_infrastructure.sensor_data \
  normalized_data.csv

# Query example
bq query --use_legacy_sql=false \
'SELECT 
  DATE(timestamp) as date,
  AVG(metric_3) as avg_flow_rate,
  MAX(metric_3) as max_flow_rate,
  MIN(metric_3) as min_flow_rate
FROM `your-gcp-project-id.water_infrastructure.sensor_data`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY date
ORDER BY date DESC'

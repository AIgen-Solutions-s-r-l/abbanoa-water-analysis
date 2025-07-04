-- BigQuery Monitoring Queries for Water Infrastructure Data

-- Data Freshness
-- Check data freshness
            SELECT 
              MAX(timestamp) as latest_data,
              TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(timestamp), MINUTE) as minutes_behind
            FROM `{project_id}.{dataset_id}.{table_id}`

-- Hourly Patterns
-- Hourly consumption patterns
            SELECT 
              EXTRACT(HOUR FROM timestamp) as hour,
              AVG(metric_3) as avg_flow_rate,
              STDDEV(metric_3) as stddev_flow_rate,
              COUNT(*) as measurements
            FROM `{project_id}.{dataset_id}.{table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY hour
            ORDER BY hour

-- Anomaly Detection
-- Simple anomaly detection (values outside 3 standard deviations)
            WITH stats AS (
              SELECT 
                AVG(metric_3) as mean_value,
                STDDEV(metric_3) as std_value
              FROM `{project_id}.{dataset_id}.{table_id}`
              WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            )
            SELECT 
              timestamp,
              metric_3 as flow_rate,
              ABS(metric_3 - stats.mean_value) / stats.std_value as z_score,
              CASE 
                WHEN ABS(metric_3 - stats.mean_value) > 3 * stats.std_value THEN 'ANOMALY'
                ELSE 'NORMAL'
              END as status
            FROM `{project_id}.{dataset_id}.{table_id}`, stats
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
              AND ABS(metric_3 - stats.mean_value) > 3 * stats.std_value
            ORDER BY timestamp DESC

-- Daily Summary
-- Daily summary statistics
            SELECT 
              DATE(timestamp) as date,
              COUNT(*) as measurements,
              AVG(metric_3) as avg_flow_rate,
              MAX(metric_3) as max_flow_rate,
              MIN(metric_3) as min_flow_rate,
              STDDEV(metric_3) as stddev_flow_rate,
              APPROX_QUANTILES(metric_3, 100)[OFFSET(50)] as median_flow_rate,
              APPROX_QUANTILES(metric_3, 100)[OFFSET(95)] as p95_flow_rate
            FROM `{project_id}.{dataset_id}.{table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY date
            ORDER BY date DESC


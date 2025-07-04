/*
 * View: vw_daily_timeseries
 * Purpose: Daily aggregation of sensor readings with gap-filling for complete time series
 * Owner: Data Engineering Team
 * Created: 2025-07-04
 * Dependencies: raw_data.sensor_readings, reference.district_metadata, reference.metric_definitions
 * 
 * Performance Targets:
 * - Query 5 years of data: < 1 second
 * - Query single month: < 100ms
 * - Query with filters: < 500ms
 * 
 * Features:
 * - Daily UTC aggregation by district and metric type
 * - Gap-filling for missing dates
 * - Statistical aggregations (avg, min, max, percentiles)
 * - Data quality flags
 * - Optimized partitioning and clustering
 */

CREATE OR REPLACE VIEW `abbanoa-464816.water_infrastructure.vw_daily_timeseries`
OPTIONS(
  description="Daily aggregated sensor readings with gap-filling for complete time series analysis",
  labels=[("team", "data_engineering"), ("purpose", "analytics"), ("criticality", "high")]
)
AS

-- Date spine: Generate complete date array for the last 5 years
WITH date_spine AS (
  SELECT 
    date_utc,
    -- Add day of week and month for seasonal analysis
    EXTRACT(DAYOFWEEK FROM date_utc) as day_of_week,
    EXTRACT(MONTH FROM date_utc) as month_number,
    EXTRACT(YEAR FROM date_utc) as year_number
  FROM UNNEST(
    GENERATE_DATE_ARRAY(
      DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 5 YEAR),
      CURRENT_DATE('UTC')
    )
  ) AS date_utc
),

-- District-Metric combinations: All valid district and metric combinations
district_metrics AS (
  SELECT DISTINCT
    d.district_id,
    d.district_name,
    d.population_served,
    m.metric_type,
    m.metric_name,
    m.unit_of_measurement,
    m.expected_frequency_minutes
  FROM `abbanoa-464816.reference.district_metadata` d
  CROSS JOIN `abbanoa-464816.reference.metric_definitions` m
  WHERE d.is_active = TRUE
    AND m.is_active = TRUE
    AND m.metric_type IN ('flow_rate', 'reservoir_level', 'pressure')
),

-- Raw daily aggregates: Aggregate sensor readings by date, district, and metric
daily_aggregates AS (
  SELECT 
    DATE(sr.timestamp, 'UTC') as date_utc,
    sr.district_id,
    sr.metric_type,
    
    -- Core statistical aggregations
    AVG(sr.reading_value) as avg_value,
    MIN(sr.reading_value) as min_value,
    MAX(sr.reading_value) as max_value,
    SUM(sr.reading_value) as sum_value,
    COUNT(sr.reading_value) as count_readings,
    STDDEV(sr.reading_value) as stddev_value,
    
    -- Percentile calculations for outlier detection
    APPROX_QUANTILES(sr.reading_value, 100)[OFFSET(10)] as percentile_10,
    APPROX_QUANTILES(sr.reading_value, 100)[OFFSET(25)] as percentile_25,
    APPROX_QUANTILES(sr.reading_value, 100)[OFFSET(50)] as percentile_50,
    APPROX_QUANTILES(sr.reading_value, 100)[OFFSET(75)] as percentile_75,
    APPROX_QUANTILES(sr.reading_value, 100)[OFFSET(90)] as percentile_90,
    APPROX_QUANTILES(sr.reading_value, 100)[OFFSET(95)] as percentile_95,
    
    -- Data quality metrics
    COUNT(CASE WHEN sr.quality_score >= 0.9 THEN 1 END) as high_quality_readings,
    COUNT(CASE WHEN sr.quality_score < 0.5 THEN 1 END) as low_quality_readings,
    AVG(sr.quality_score) as avg_quality_score,
    
    -- Time coverage analysis
    COUNT(DISTINCT EXTRACT(HOUR FROM sr.timestamp)) as hours_with_data,
    MIN(sr.timestamp) as first_reading_time,
    MAX(sr.timestamp) as last_reading_time,
    
    -- Anomaly indicators
    COUNT(CASE WHEN ABS(sr.reading_value - LAG(sr.reading_value) OVER (
      PARTITION BY sr.district_id, sr.metric_type 
      ORDER BY sr.timestamp
    )) > 3 * STDDEV(sr.reading_value) OVER (
      PARTITION BY sr.district_id, sr.metric_type, DATE(sr.timestamp, 'UTC')
    ) THEN 1 END) as potential_anomalies
    
  FROM `abbanoa-464816.raw_data.sensor_readings` sr
  WHERE 
    -- Partition pruning: Only include recent data
    DATE(sr.timestamp) >= DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 5 YEAR)
    AND sr.reading_value IS NOT NULL
    AND sr.district_id IS NOT NULL
    AND sr.metric_type IS NOT NULL
  GROUP BY 
    DATE(sr.timestamp, 'UTC'),
    sr.district_id,
    sr.metric_type
),

-- Gap-filled data: Join date spine with district-metrics and aggregates
gap_filled_data AS (
  SELECT 
    ds.date_utc,
    ds.day_of_week,
    ds.month_number,
    ds.year_number,
    dm.district_id,
    dm.district_name,
    dm.population_served,
    dm.metric_type,
    dm.metric_name,
    dm.unit_of_measurement,
    dm.expected_frequency_minutes,
    
    -- Aggregated values (NULL for missing dates)
    da.avg_value,
    da.min_value,
    da.max_value,
    da.sum_value,
    da.count_readings,
    da.stddev_value,
    da.percentile_10,
    da.percentile_25,
    da.percentile_50,
    da.percentile_75,
    da.percentile_90,
    da.percentile_95,
    
    -- Data quality metrics
    COALESCE(da.high_quality_readings, 0) as high_quality_readings,
    COALESCE(da.low_quality_readings, 0) as low_quality_readings,
    da.avg_quality_score,
    COALESCE(da.hours_with_data, 0) as hours_with_data,
    da.first_reading_time,
    da.last_reading_time,
    COALESCE(da.potential_anomalies, 0) as potential_anomalies,
    
    -- Gap filling flags and quality indicators
    CASE 
      WHEN da.date_utc IS NULL THEN TRUE 
      ELSE FALSE 
    END as gap_filled_flag,
    
    CASE 
      WHEN da.date_utc IS NULL THEN 'NO_DATA'
      WHEN da.count_readings = 0 THEN 'NO_READINGS'
      WHEN da.avg_quality_score < 0.5 THEN 'POOR_QUALITY'
      WHEN da.hours_with_data < 12 THEN 'INCOMPLETE_DAY'
      WHEN da.potential_anomalies > 5 THEN 'HIGH_ANOMALIES'
      ELSE 'GOOD'
    END as data_quality_flag,
    
    -- Calculate expected vs actual reading count
    CASE 
      WHEN dm.expected_frequency_minutes > 0 THEN
        ROUND((24 * 60) / dm.expected_frequency_minutes, 0)
      ELSE NULL
    END as expected_daily_readings,
    
    CASE 
      WHEN dm.expected_frequency_minutes > 0 AND da.count_readings > 0 THEN
        ROUND(
          (da.count_readings / ((24 * 60) / dm.expected_frequency_minutes)) * 100, 
          2
        )
      ELSE NULL
    END as data_completeness_pct
    
  FROM date_spine ds
  CROSS JOIN district_metrics dm
  LEFT JOIN daily_aggregates da 
    ON ds.date_utc = da.date_utc
    AND dm.district_id = da.district_id
    AND dm.metric_type = da.metric_type
),

-- Forward fill for operational continuity (optional)
forward_filled AS (
  SELECT 
    *,
    
    -- Forward fill last known values for critical operational metrics
    CASE 
      WHEN metric_type IN ('reservoir_level', 'pressure') AND avg_value IS NULL THEN
        LAST_VALUE(avg_value IGNORE NULLS) OVER (
          PARTITION BY district_id, metric_type 
          ORDER BY date_utc 
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )
      ELSE avg_value
    END as avg_value_filled,
    
    CASE 
      WHEN metric_type IN ('reservoir_level', 'pressure') AND avg_value IS NULL THEN TRUE
      ELSE FALSE
    END as forward_filled_flag
    
  FROM gap_filled_data
)

-- Final output with all features
SELECT 
  -- Time dimensions
  date_utc,
  day_of_week,
  month_number,
  year_number,
  
  -- District and metric dimensions
  district_id,
  district_name,
  population_served,
  metric_type,
  metric_name,
  unit_of_measurement,
  
  -- Core aggregated values
  avg_value,
  min_value,
  max_value,
  sum_value,
  count_readings,
  stddev_value,
  
  -- Percentiles for distribution analysis
  percentile_10,
  percentile_25,
  percentile_50 as median_value,
  percentile_75,
  percentile_90,
  percentile_95,
  
  -- Data quality metrics
  high_quality_readings,
  low_quality_readings,
  avg_quality_score,
  hours_with_data,
  first_reading_time,
  last_reading_time,
  potential_anomalies,
  
  -- Data completeness and quality flags
  expected_daily_readings,
  data_completeness_pct,
  gap_filled_flag,
  forward_filled_flag,
  data_quality_flag,
  
  -- Forward-filled values for operational continuity
  avg_value_filled as avg_value_operational,
  
  -- Derived metrics for analysis
  CASE 
    WHEN count_readings > 1 THEN
      (max_value - min_value) / NULLIF(avg_value, 0) * 100
    ELSE NULL
  END as daily_variation_pct,
  
  CASE 
    WHEN percentile_75 > percentile_25 THEN
      percentile_75 - percentile_25
    ELSE NULL
  END as interquartile_range,
  
  -- Seasonal indicators
  CASE 
    WHEN month_number IN (6, 7, 8) THEN 'SUMMER'
    WHEN month_number IN (9, 10, 11) THEN 'FALL'
    WHEN month_number IN (12, 1, 2) THEN 'WINTER'
    WHEN month_number IN (3, 4, 5) THEN 'SPRING'
  END as season,
  
  CASE 
    WHEN day_of_week IN (1, 7) THEN 'WEEKEND'
    ELSE 'WEEKDAY'
  END as day_type

FROM forward_filled

-- Performance optimization: ensure proper ordering for partition pruning
ORDER BY date_utc DESC, district_id, metric_type;
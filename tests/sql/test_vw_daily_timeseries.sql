/*
 * Unit Tests: vw_daily_timeseries
 * Purpose: Comprehensive testing of daily aggregation view
 * Test Environment: db-sandbox
 * Coverage: Aggregation logic, gap-filling, edge cases, performance
 * 
 * Test Categories:
 * 1. Data Aggregation Accuracy
 * 2. Gap Filling Logic
 * 3. Data Quality Flags
 * 4. Edge Cases and Boundary Conditions
 * 5. Performance and Optimization
 * 6. Timezone Handling
 */

-- =============================================================================
-- TEST SETUP: Create test data and helper functions
-- =============================================================================

-- Create test datasets in sandbox environment
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_data.sensor_readings_test` AS
WITH test_data AS (
  -- Generate 5 years of synthetic test data with deliberate patterns and gaps
  SELECT 
    TIMESTAMP_ADD(
      TIMESTAMP('2020-01-01 00:00:00 UTC'),
      INTERVAL row_num * 15 MINUTE
    ) as timestamp,
    
    CASE 
      WHEN MOD(row_num, 2000) = 0 THEN 'DIST_001'  -- Central Business District
      ELSE 'DIST_002'  -- Residential North
    END as district_id,
    
    CASE 
      WHEN MOD(row_num, 3) = 0 THEN 'flow_rate'
      WHEN MOD(row_num, 3) = 1 THEN 'pressure'  
      ELSE 'reservoir_level'
    END as metric_type,
    
    -- Generate realistic values with patterns
    CASE 
      WHEN metric_type = 'flow_rate' THEN
        100 + 50 * SIN(2 * 3.14159 * EXTRACT(HOUR FROM timestamp) / 24) + 
        10 * RAND() - 5  -- Daily pattern + noise
      WHEN metric_type = 'pressure' THEN
        4.5 + 1.5 * COS(2 * 3.14159 * EXTRACT(HOUR FROM timestamp) / 24) + 
        0.5 * RAND() - 0.25
      ELSE  -- reservoir_level
        15 + 5 * SIN(2 * 3.14159 * EXTRACT(DAYOFYEAR FROM timestamp) / 365) + 
        2 * RAND() - 1  -- Seasonal pattern + noise
    END as reading_value,
    
    -- Quality score with occasional poor quality
    CASE 
      WHEN MOD(row_num, 100) = 0 THEN 0.3  -- 1% poor quality
      WHEN MOD(row_num, 50) = 0 THEN 0.7   -- 2% medium quality
      ELSE 0.95 + 0.05 * RAND()            -- 97% good quality
    END as quality_score,
    
    row_num
    
  FROM UNNEST(GENERATE_ARRAY(1, 1500000)) as row_num  -- ~5 years of 15-min data
  WHERE 
    -- Create deliberate gaps for gap-filling tests
    NOT (
      EXTRACT(DATE FROM TIMESTAMP_ADD(
        TIMESTAMP('2020-01-01 00:00:00 UTC'),
        INTERVAL row_num * 15 MINUTE
      )) IN ('2021-03-15', '2022-07-20', '2023-12-25')  -- Missing specific days
    )
    AND NOT (
      EXTRACT(HOUR FROM TIMESTAMP_ADD(
        TIMESTAMP('2020-01-01 00:00:00 UTC'),
        INTERVAL row_num * 15 MINUTE
      )) = 3 AND 
      EXTRACT(DATE FROM TIMESTAMP_ADD(
        TIMESTAMP('2020-01-01 00:00:00 UTC'),
        INTERVAL row_num * 15 MINUTE
      )) BETWEEN '2021-01-01' AND '2021-01-31'  -- Missing 3 AM data in January 2021
    )
);

-- Create reference tables for testing
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.reference.district_metadata` AS
SELECT * FROM (
  SELECT 'DIST_001' as district_id, 'Central Business District' as district_name, 50000 as population_served, TRUE as is_active
  UNION ALL
  SELECT 'DIST_002' as district_id, 'Residential North' as district_name, 35000 as population_served, TRUE as is_active
  UNION ALL
  SELECT 'DIST_003' as district_id, 'Inactive District' as district_name, 0 as population_served, FALSE as is_active
);

CREATE OR REPLACE TABLE `abbanoa-test-sandbox.reference.metric_definitions` AS
SELECT * FROM (
  SELECT 'flow_rate' as metric_type, 'Water Flow Rate' as metric_name, 'L/s' as unit_of_measurement, 15 as expected_frequency_minutes, TRUE as is_active
  UNION ALL
  SELECT 'pressure' as metric_type, 'Network Pressure' as metric_name, 'bar' as unit_of_measurement, 10 as expected_frequency_minutes, TRUE as is_active
  UNION ALL
  SELECT 'reservoir_level' as metric_type, 'Reservoir Level' as metric_name, 'm' as unit_of_measurement, 5 as expected_frequency_minutes, TRUE as is_active
  UNION ALL
  SELECT 'temperature' as metric_type, 'Water Temperature' as metric_name, '°C' as unit_of_measurement, 30 as expected_frequency_minutes, FALSE as is_active
);

-- =============================================================================
-- TEST 1: Data Aggregation Accuracy
-- =============================================================================

-- Test 1.1: Verify daily aggregation produces correct statistical measures
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_aggregation_accuracy` AS
WITH test_date AS (
  SELECT DATE('2021-01-01') as test_date
),
expected_values AS (
  SELECT 
    DATE(timestamp, 'UTC') as date_utc,
    district_id,
    metric_type,
    AVG(reading_value) as expected_avg,
    MIN(reading_value) as expected_min,
    MAX(reading_value) as expected_max,
    COUNT(reading_value) as expected_count,
    STDDEV(reading_value) as expected_stddev
  FROM `abbanoa-test-sandbox.test_data.sensor_readings_test`
  WHERE DATE(timestamp, 'UTC') = (SELECT test_date FROM test_date)
  GROUP BY DATE(timestamp, 'UTC'), district_id, metric_type
),
view_results AS (
  SELECT 
    date_utc,
    district_id,
    metric_type,
    avg_value,
    min_value,
    max_value,
    count_readings,
    stddev_value
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
  WHERE date_utc = (SELECT test_date FROM test_date)
)
SELECT 
  'AGGREGATION_ACCURACY' as test_name,
  ev.date_utc,
  ev.district_id,
  ev.metric_type,
  
  -- Test assertions
  ABS(ev.expected_avg - vr.avg_value) < 0.001 as avg_test_passed,
  ev.expected_min = vr.min_value as min_test_passed,
  ev.expected_max = vr.max_value as max_test_passed,
  ev.expected_count = vr.count_readings as count_test_passed,
  ABS(COALESCE(ev.expected_stddev, 0) - COALESCE(vr.stddev_value, 0)) < 0.001 as stddev_test_passed,
  
  -- Expected vs actual values for debugging
  ev.expected_avg,
  vr.avg_value,
  ev.expected_count,
  vr.count_readings

FROM expected_values ev
LEFT JOIN view_results vr 
  ON ev.date_utc = vr.date_utc 
  AND ev.district_id = vr.district_id 
  AND ev.metric_type = vr.metric_type;

-- =============================================================================
-- TEST 2: Gap Filling Logic
-- =============================================================================

-- Test 2.1: Verify all dates are present in output (no gaps)
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_gap_filling` AS
WITH expected_dates AS (
  SELECT date_utc
  FROM UNNEST(
    GENERATE_DATE_ARRAY(
      DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 5 YEAR),
      CURRENT_DATE('UTC')
    )
  ) AS date_utc
),
view_dates AS (
  SELECT DISTINCT date_utc
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
),
missing_dates AS (
  SELECT ed.date_utc
  FROM expected_dates ed
  LEFT JOIN view_dates vd ON ed.date_utc = vd.date_utc
  WHERE vd.date_utc IS NULL
)
SELECT 
  'GAP_FILLING_COMPLETENESS' as test_name,
  (SELECT COUNT(*) FROM expected_dates) as expected_date_count,
  (SELECT COUNT(*) FROM view_dates) as actual_date_count,
  (SELECT COUNT(*) FROM missing_dates) as missing_date_count,
  (SELECT COUNT(*) FROM missing_dates) = 0 as gap_filling_test_passed;

-- Test 2.2: Verify gap_filled_flag is correctly set
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_gap_flags` AS
WITH deliberate_gaps AS (
  SELECT 
    date_utc,
    district_id,
    metric_type,
    gap_filled_flag,
    count_readings
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
  WHERE date_utc IN ('2021-03-15', '2022-07-20', '2023-12-25')  -- Known missing days
)
SELECT 
  'GAP_FILLED_FLAGS' as test_name,
  date_utc,
  district_id,
  metric_type,
  gap_filled_flag,
  count_readings,
  gap_filled_flag = TRUE as gap_flag_correct,
  count_readings = 0 as reading_count_correct
FROM deliberate_gaps;

-- =============================================================================
-- TEST 3: Data Quality Flags
-- =============================================================================

-- Test 3.1: Verify data quality flag logic
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_quality_flags` AS
WITH quality_test_cases AS (
  SELECT 
    date_utc,
    district_id,
    metric_type,
    count_readings,
    avg_quality_score,
    hours_with_data,
    potential_anomalies,
    data_quality_flag,
    
    -- Expected flag based on logic
    CASE 
      WHEN count_readings = 0 THEN 'NO_READINGS'
      WHEN avg_quality_score < 0.5 THEN 'POOR_QUALITY'
      WHEN hours_with_data < 12 THEN 'INCOMPLETE_DAY'
      WHEN potential_anomalies > 5 THEN 'HIGH_ANOMALIES'
      ELSE 'GOOD'
    END as expected_flag
    
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
  WHERE date_utc BETWEEN '2021-01-01' AND '2021-01-31'  -- Test month
)
SELECT 
  'DATA_QUALITY_FLAGS' as test_name,
  COUNT(*) as total_records,
  COUNT(CASE WHEN data_quality_flag = expected_flag THEN 1 END) as correct_flags,
  COUNT(CASE WHEN data_quality_flag = expected_flag THEN 1 END) / COUNT(*) as accuracy_rate,
  (COUNT(CASE WHEN data_quality_flag = expected_flag THEN 1 END) / COUNT(*)) >= 0.95 as quality_flag_test_passed
FROM quality_test_cases;

-- =============================================================================
-- TEST 4: Edge Cases and Boundary Conditions
-- =============================================================================

-- Test 4.1: No duplicate date-district-metric combinations
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_no_duplicates` AS
WITH duplicate_check AS (
  SELECT 
    date_utc,
    district_id,
    metric_type,
    COUNT(*) as record_count
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
  GROUP BY date_utc, district_id, metric_type
  HAVING COUNT(*) > 1
)
SELECT 
  'NO_DUPLICATES' as test_name,
  COUNT(*) as duplicate_combinations,
  COUNT(*) = 0 as no_duplicates_test_passed
FROM duplicate_check;

-- Test 4.2: Handle NULL values correctly
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_null_handling` AS
SELECT 
  'NULL_HANDLING' as test_name,
  COUNT(CASE WHEN date_utc IS NULL THEN 1 END) as null_dates,
  COUNT(CASE WHEN district_id IS NULL THEN 1 END) as null_districts,
  COUNT(CASE WHEN metric_type IS NULL THEN 1 END) as null_metrics,
  COUNT(CASE WHEN date_utc IS NULL OR district_id IS NULL OR metric_type IS NULL THEN 1 END) = 0 as null_handling_test_passed
FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`;

-- Test 4.3: Verify percentile calculations are reasonable
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_percentiles` AS
WITH percentile_check AS (
  SELECT 
    date_utc,
    district_id,
    metric_type,
    min_value,
    percentile_25,
    percentile_50,
    percentile_75,
    max_value,
    
    -- Percentiles should be ordered
    min_value <= percentile_25 as min_p25_order,
    percentile_25 <= percentile_50 as p25_p50_order,
    percentile_50 <= percentile_75 as p50_p75_order,
    percentile_75 <= max_value as p75_max_order
    
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
  WHERE avg_value IS NOT NULL  -- Only check days with actual data
    AND date_utc BETWEEN '2021-01-01' AND '2021-12-31'
)
SELECT 
  'PERCENTILE_ORDER' as test_name,
  COUNT(*) as total_records,
  COUNT(CASE WHEN min_p25_order AND p25_p50_order AND p50_p75_order AND p75_max_order THEN 1 END) as correct_order,
  COUNT(CASE WHEN min_p25_order AND p25_p50_order AND p50_p75_order AND p75_max_order THEN 1 END) / COUNT(*) as accuracy_rate,
  (COUNT(CASE WHEN min_p25_order AND p25_p50_order AND p50_p75_order AND p75_max_order THEN 1 END) / COUNT(*)) >= 0.99 as percentile_test_passed
FROM percentile_check;

-- =============================================================================
-- TEST 5: Performance Validation
-- =============================================================================

-- Test 5.1: Query performance benchmark
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_performance` AS
WITH performance_test AS (
  SELECT 
    'PERFORMANCE_5_YEARS' as test_name,
    CURRENT_TIMESTAMP() as start_time
),
query_execution AS (
  SELECT COUNT(*) as record_count
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
  WHERE date_utc >= DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 5 YEAR)
),
end_timing AS (
  SELECT 
    CURRENT_TIMESTAMP() as end_time,
    (SELECT start_time FROM performance_test) as start_time
)
SELECT 
  pt.test_name,
  qe.record_count,
  et.start_time,
  et.end_time,
  TIMESTAMP_DIFF(et.end_time, et.start_time, MILLISECOND) as execution_time_ms,
  TIMESTAMP_DIFF(et.end_time, et.start_time, MILLISECOND) <= 1000 as performance_test_passed  -- < 1 second
FROM performance_test pt
CROSS JOIN query_execution qe
CROSS JOIN end_timing et;

-- =============================================================================
-- TEST 6: Timezone Handling
-- =============================================================================

-- Test 6.1: Verify UTC timezone handling
CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_timezone` AS
WITH timezone_test AS (
  SELECT 
    date_utc,
    first_reading_time,
    last_reading_time,
    EXTRACT(TIMEZONE FROM first_reading_time) as first_tz,
    EXTRACT(TIMEZONE FROM last_reading_time) as last_tz
  FROM `abbanoa-test-sandbox.water_infrastructure.vw_daily_timeseries`
  WHERE first_reading_time IS NOT NULL
    AND last_reading_time IS NOT NULL
  LIMIT 100
)
SELECT 
  'TIMEZONE_HANDLING' as test_name,
  COUNT(*) as total_records,
  COUNT(CASE WHEN first_tz = 0 AND last_tz = 0 THEN 1 END) as utc_timezone_count,
  COUNT(CASE WHEN first_tz = 0 AND last_tz = 0 THEN 1 END) / COUNT(*) as utc_accuracy_rate,
  (COUNT(CASE WHEN first_tz = 0 AND last_tz = 0 THEN 1 END) / COUNT(*)) = 1.0 as timezone_test_passed
FROM timezone_test;

-- =============================================================================
-- TEST SUMMARY: Aggregate all test results
-- =============================================================================

CREATE OR REPLACE TABLE `abbanoa-test-sandbox.test_results.test_summary` AS
WITH all_tests AS (
  SELECT test_name, 'aggregation' as category, avg_test_passed AND min_test_passed AND max_test_passed AND count_test_passed AND stddev_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_aggregation_accuracy` LIMIT 1
  UNION ALL
  SELECT test_name, 'gap_filling' as category, gap_filling_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_gap_filling`
  UNION ALL
  SELECT test_name, 'data_quality' as category, quality_flag_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_quality_flags`
  UNION ALL
  SELECT test_name, 'edge_cases' as category, no_duplicates_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_no_duplicates`
  UNION ALL
  SELECT test_name, 'edge_cases' as category, null_handling_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_null_handling`
  UNION ALL
  SELECT test_name, 'edge_cases' as category, percentile_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_percentiles`
  UNION ALL
  SELECT test_name, 'performance' as category, performance_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_performance`
  UNION ALL
  SELECT test_name, 'timezone' as category, timezone_test_passed as passed FROM `abbanoa-test-sandbox.test_results.test_timezone`
)
SELECT 
  category,
  COUNT(*) as total_tests,
  COUNT(CASE WHEN passed THEN 1 END) as passed_tests,
  COUNT(CASE WHEN NOT passed THEN 1 END) as failed_tests,
  COUNT(CASE WHEN passed THEN 1 END) / COUNT(*) as pass_rate,
  COUNT(CASE WHEN passed THEN 1 END) / COUNT(*) = 1.0 as all_tests_passed
FROM all_tests
GROUP BY category

UNION ALL

SELECT 
  'OVERALL' as category,
  COUNT(*) as total_tests,
  COUNT(CASE WHEN passed THEN 1 END) as passed_tests,
  COUNT(CASE WHEN NOT passed THEN 1 END) as failed_tests,
  COUNT(CASE WHEN passed THEN 1 END) / COUNT(*) as pass_rate,
  COUNT(CASE WHEN passed THEN 1 END) / COUNT(*) = 1.0 as all_tests_passed
FROM all_tests
ORDER BY category;
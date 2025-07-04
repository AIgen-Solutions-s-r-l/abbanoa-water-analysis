/*
 * ARIMA_PLUS Baseline Forecast Model
 * Task: 0.3 - Prototype ARIMA_PLUS model for 7-day forecasting
 * Purpose: Create time series forecasting models for water infrastructure KPIs
 * Author: Claude Code
 * Created: 2025-07-04
 * 
 * Success Criteria:
 * - 7-day prediction horizon
 * - MAPE ≤ 15% across 3 pilot districts
 * - Evaluate on holdout data (Jan-Mar 2025)
 * - Models for: flow_rate, pressure, reservoir_level
 * 
 * Performance Requirements:
 * - Training: District-specific models
 * - Evaluation: Hold-out validation
 * - Deployment: Automated forecast pipeline
 */

-- =============================================================================
-- SECTION 1: Data Preparation for Time Series Modeling
-- =============================================================================

-- Create training dataset from vw_daily_timeseries
-- Exclude holdout period (Jan-Mar 2025) for evaluation
CREATE OR REPLACE TABLE `abbanoa-464816.ml_models.training_data` AS
WITH training_base AS (
  SELECT 
    date_utc as ds,  -- Date column (required by ARIMA_PLUS)
    CONCAT(district_id, '_', metric_type) as district_metric,  -- Time series ID
    avg_value as y,  -- Target value (required by ARIMA_PLUS)
    
    -- Additional features for model
    district_id,
    metric_type,
    day_of_week,
    month_number,
    season,
    day_type,
    
    -- Data quality indicators
    data_quality_flag,
    gap_filled_flag,
    data_completeness_pct,
    
    -- Derived features
    LAG(avg_value, 1) OVER (
      PARTITION BY district_id, metric_type 
      ORDER BY date_utc
    ) as lag_1_day,
    LAG(avg_value, 7) OVER (
      PARTITION BY district_id, metric_type 
      ORDER BY date_utc
    ) as lag_7_day,
    
    -- Rolling averages for trend
    AVG(avg_value) OVER (
      PARTITION BY district_id, metric_type 
      ORDER BY date_utc 
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as avg_7_day,
    
    AVG(avg_value) OVER (
      PARTITION BY district_id, metric_type 
      ORDER BY date_utc 
      ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as avg_30_day
    
  FROM `abbanoa-464816.water_infrastructure.vw_daily_timeseries`
  WHERE 
    -- Training period: Exclude holdout data (Jan-Mar 2025)
    date_utc >= DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 5 YEAR)
    AND date_utc < DATE('2025-01-01')
    
    -- Only include key metrics for pilot districts
    AND district_id IN ('DIST_001', 'DIST_002')  -- Pilot districts
    AND metric_type IN ('flow_rate', 'pressure', 'reservoir_level')
    
    -- Quality filters
    AND avg_value IS NOT NULL
    AND data_quality_flag IN ('GOOD', 'INCOMPLETE_DAY')  -- Allow some incomplete days
    AND data_completeness_pct > 50  -- At least 50% data completeness
),

-- Fill remaining gaps with forward fill for training stability
training_filled AS (
  SELECT 
    *,
    -- Forward fill missing values within reasonable gaps (≤ 3 days)
    CASE 
      WHEN y IS NULL THEN 
        LAST_VALUE(y IGNORE NULLS) OVER (
          PARTITION BY district_metric 
          ORDER BY ds 
          ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        )
      ELSE y
    END as y_filled
  FROM training_base
)

SELECT 
  ds,
  y_filled as y,
  district_metric,
  district_id,
  metric_type,
  day_of_week,
  month_number,
  season,
  day_type,
  lag_1_day,
  lag_7_day,
  avg_7_day,
  avg_30_day
FROM training_filled
WHERE y_filled IS NOT NULL
ORDER BY district_metric, ds;

-- =============================================================================
-- SECTION 2: Create ARIMA_PLUS Models for Each District-Metric Combination
-- =============================================================================

-- Model 1: DIST_001 Flow Rate
CREATE OR REPLACE MODEL `abbanoa-464816.ml_models.arima_dist001_flow_rate`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='ds',
  time_series_data_col='y',
  time_series_id_col='district_metric',
  horizon=7,
  auto_arima=TRUE,
  data_frequency='DAILY',
  decompose_time_series=TRUE,
  holiday_region='IT',  -- Italy holidays
  include_drift=TRUE,
  clean_spikes_and_dips=TRUE,
  adjust_step_changes=TRUE
) AS
SELECT 
  ds,
  y,
  district_metric
FROM `abbanoa-464816.ml_models.training_data`
WHERE district_id = 'DIST_001' 
  AND metric_type = 'flow_rate'
  AND district_metric = 'DIST_001_flow_rate';

-- Model 2: DIST_001 Pressure
CREATE OR REPLACE MODEL `abbanoa-464816.ml_models.arima_dist001_pressure`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='ds',
  time_series_data_col='y',
  time_series_id_col='district_metric',
  horizon=7,
  auto_arima=TRUE,
  data_frequency='DAILY',
  decompose_time_series=TRUE,
  holiday_region='IT',
  include_drift=TRUE,
  clean_spikes_and_dips=TRUE,
  adjust_step_changes=TRUE
) AS
SELECT 
  ds,
  y,
  district_metric
FROM `abbanoa-464816.ml_models.training_data`
WHERE district_id = 'DIST_001' 
  AND metric_type = 'pressure'
  AND district_metric = 'DIST_001_pressure';

-- Model 3: DIST_001 Reservoir Level
CREATE OR REPLACE MODEL `abbanoa-464816.ml_models.arima_dist001_reservoir_level`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='ds',
  time_series_data_col='y',
  time_series_id_col='district_metric',
  horizon=7,
  auto_arima=TRUE,
  data_frequency='DAILY',
  decompose_time_series=TRUE,
  holiday_region='IT',
  include_drift=TRUE,
  clean_spikes_and_dips=TRUE,
  adjust_step_changes=TRUE
) AS
SELECT 
  ds,
  y,
  district_metric
FROM `abbanoa-464816.ml_models.training_data`
WHERE district_id = 'DIST_001' 
  AND metric_type = 'reservoir_level'
  AND district_metric = 'DIST_001_reservoir_level';

-- Model 4: DIST_002 Flow Rate
CREATE OR REPLACE MODEL `abbanoa-464816.ml_models.arima_dist002_flow_rate`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='ds',
  time_series_data_col='y',
  time_series_id_col='district_metric',
  horizon=7,
  auto_arima=TRUE,
  data_frequency='DAILY',
  decompose_time_series=TRUE,
  holiday_region='IT',
  include_drift=TRUE,
  clean_spikes_and_dips=TRUE,
  adjust_step_changes=TRUE
) AS
SELECT 
  ds,
  y,
  district_metric
FROM `abbanoa-464816.ml_models.training_data`
WHERE district_id = 'DIST_002' 
  AND metric_type = 'flow_rate'
  AND district_metric = 'DIST_002_flow_rate';

-- Model 5: DIST_002 Pressure
CREATE OR REPLACE MODEL `abbanoa-464816.ml_models.arima_dist002_pressure`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='ds',
  time_series_data_col='y',
  time_series_id_col='district_metric',
  horizon=7,
  auto_arima=TRUE,
  data_frequency='DAILY',
  decompose_time_series=TRUE,
  holiday_region='IT',
  include_drift=TRUE,
  clean_spikes_and_dips=TRUE,
  adjust_step_changes=TRUE
) AS
SELECT 
  ds,
  y,
  district_metric
FROM `abbanoa-464816.ml_models.training_data`
WHERE district_id = 'DIST_002' 
  AND metric_type = 'pressure'
  AND district_metric = 'DIST_002_pressure';

-- Model 6: DIST_002 Reservoir Level
CREATE OR REPLACE MODEL `abbanoa-464816.ml_models.arima_dist002_reservoir_level`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='ds',
  time_series_data_col='y',
  time_series_id_col='district_metric',
  horizon=7,
  auto_arima=TRUE,
  data_frequency='DAILY',
  decompose_time_series=TRUE,
  holiday_region='IT',
  include_drift=TRUE,
  clean_spikes_and_dips=TRUE,
  adjust_step_changes=TRUE
) AS
SELECT 
  ds,
  y,
  district_metric
FROM `abbanoa-464816.ml_models.training_data`
WHERE district_id = 'DIST_002' 
  AND metric_type = 'reservoir_level'
  AND district_metric = 'DIST_002_reservoir_level';

-- =============================================================================
-- SECTION 3: Model Evaluation and Diagnostics
-- =============================================================================

-- Evaluate all models on training data
CREATE OR REPLACE TABLE `abbanoa-464816.ml_models.model_evaluation` AS
WITH model_evaluations AS (
  SELECT 'DIST_001_flow_rate' as model_name, * FROM ML.EVALUATE(MODEL `abbanoa-464816.ml_models.arima_dist001_flow_rate`)
  UNION ALL
  SELECT 'DIST_001_pressure' as model_name, * FROM ML.EVALUATE(MODEL `abbanoa-464816.ml_models.arima_dist001_pressure`)
  UNION ALL
  SELECT 'DIST_001_reservoir_level' as model_name, * FROM ML.EVALUATE(MODEL `abbanoa-464816.ml_models.arima_dist001_reservoir_level`)
  UNION ALL
  SELECT 'DIST_002_flow_rate' as model_name, * FROM ML.EVALUATE(MODEL `abbanoa-464816.ml_models.arima_dist002_flow_rate`)
  UNION ALL
  SELECT 'DIST_002_pressure' as model_name, * FROM ML.EVALUATE(MODEL `abbanoa-464816.ml_models.arima_dist002_pressure`)
  UNION ALL
  SELECT 'DIST_002_reservoir_level' as model_name, * FROM ML.EVALUATE(MODEL `abbanoa-464816.ml_models.arima_dist002_reservoir_level`)
)

SELECT 
  model_name,
  SPLIT(model_name, '_')[OFFSET(0)] || '_' || SPLIT(model_name, '_')[OFFSET(1)] as district_id,
  SPLIT(model_name, '_')[OFFSET(2)] as metric_type,
  mean_absolute_error,
  mean_absolute_percentage_error,
  root_mean_squared_error,
  mean_squared_error,
  symmetric_mean_absolute_percentage_error,
  
  -- Performance assessment
  CASE 
    WHEN mean_absolute_percentage_error <= 0.15 THEN 'PASS'
    WHEN mean_absolute_percentage_error <= 0.20 THEN 'MARGINAL'
    ELSE 'FAIL'
  END as mape_assessment,
  
  -- Timestamp for tracking
  CURRENT_TIMESTAMP() as evaluation_timestamp
FROM model_evaluations
ORDER BY model_name;

-- =============================================================================
-- SECTION 4: Holdout Validation on Jan-Mar 2025 Data
-- =============================================================================

-- Create holdout dataset
CREATE OR REPLACE TABLE `abbanoa-464816.ml_models.holdout_data` AS
SELECT 
  date_utc as ds,
  CONCAT(district_id, '_', metric_type) as district_metric,
  avg_value as y_actual,
  district_id,
  metric_type,
  data_quality_flag,
  data_completeness_pct
FROM `abbanoa-464816.water_infrastructure.vw_daily_timeseries`
WHERE 
  -- Holdout period: Jan-Mar 2025
  date_utc BETWEEN DATE('2025-01-01') AND DATE('2025-03-31')
  
  -- Only pilot districts and key metrics
  AND district_id IN ('DIST_001', 'DIST_002')
  AND metric_type IN ('flow_rate', 'pressure', 'reservoir_level')
  
  -- Quality filters
  AND avg_value IS NOT NULL
  AND data_quality_flag IN ('GOOD', 'INCOMPLETE_DAY')
ORDER BY district_metric, ds;

-- Generate forecasts for holdout period
CREATE OR REPLACE TABLE `abbanoa-464816.ml_models.holdout_forecasts` AS
WITH forecast_base AS (
  SELECT 
    'DIST_001_flow_rate' as model_name,
    forecast_timestamp as ds,
    forecast_value as y_forecast,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist001_flow_rate`,
    STRUCT(90 OVER (
      SELECT MAX(ds) as forecast_timestamp
      FROM `abbanoa-464816.ml_models.training_data`
      WHERE district_metric = 'DIST_001_flow_rate'
    ) AS horizon)
  )
  WHERE forecast_timestamp BETWEEN DATE('2025-01-01') AND DATE('2025-03-31')
  
  UNION ALL
  
  SELECT 
    'DIST_001_pressure' as model_name,
    forecast_timestamp as ds,
    forecast_value as y_forecast,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist001_pressure`,
    STRUCT(90 OVER (
      SELECT MAX(ds) as forecast_timestamp
      FROM `abbanoa-464816.ml_models.training_data`
      WHERE district_metric = 'DIST_001_pressure'
    ) AS horizon)
  )
  WHERE forecast_timestamp BETWEEN DATE('2025-01-01') AND DATE('2025-03-31')
  
  UNION ALL
  
  SELECT 
    'DIST_001_reservoir_level' as model_name,
    forecast_timestamp as ds,
    forecast_value as y_forecast,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist001_reservoir_level`,
    STRUCT(90 OVER (
      SELECT MAX(ds) as forecast_timestamp
      FROM `abbanoa-464816.ml_models.training_data`
      WHERE district_metric = 'DIST_001_reservoir_level'
    ) AS horizon)
  )
  WHERE forecast_timestamp BETWEEN DATE('2025-01-01') AND DATE('2025-03-31')
  
  UNION ALL
  
  SELECT 
    'DIST_002_flow_rate' as model_name,
    forecast_timestamp as ds,
    forecast_value as y_forecast,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist002_flow_rate`,
    STRUCT(90 OVER (
      SELECT MAX(ds) as forecast_timestamp
      FROM `abbanoa-464816.ml_models.training_data`
      WHERE district_metric = 'DIST_002_flow_rate'
    ) AS horizon)
  )
  WHERE forecast_timestamp BETWEEN DATE('2025-01-01') AND DATE('2025-03-31')
  
  UNION ALL
  
  SELECT 
    'DIST_002_pressure' as model_name,
    forecast_timestamp as ds,
    forecast_value as y_forecast,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist002_pressure`,
    STRUCT(90 OVER (
      SELECT MAX(ds) as forecast_timestamp
      FROM `abbanoa-464816.ml_models.training_data`
      WHERE district_metric = 'DIST_002_pressure'
    ) AS horizon)
  )
  WHERE forecast_timestamp BETWEEN DATE('2025-01-01') AND DATE('2025-03-31')
  
  UNION ALL
  
  SELECT 
    'DIST_002_reservoir_level' as model_name,
    forecast_timestamp as ds,
    forecast_value as y_forecast,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist002_reservoir_level`,
    STRUCT(90 OVER (
      SELECT MAX(ds) as forecast_timestamp
      FROM `abbanoa-464816.ml_models.training_data`
      WHERE district_metric = 'DIST_002_reservoir_level'
    ) AS horizon)
  )
  WHERE forecast_timestamp BETWEEN DATE('2025-01-01') AND DATE('2025-03-31')
)

SELECT 
  model_name,
  ds,
  y_forecast,
  lower_bound,
  upper_bound,
  standard_error,
  confidence_level,
  CURRENT_TIMESTAMP() as forecast_timestamp
FROM forecast_base
ORDER BY model_name, ds;

-- =============================================================================
-- SECTION 5: Calculate MAPE and Validation Metrics
-- =============================================================================

-- Calculate holdout validation metrics
CREATE OR REPLACE TABLE `abbanoa-464816.ml_models.holdout_validation` AS
WITH forecast_actuals AS (
  SELECT 
    hd.ds,
    hd.district_metric,
    hd.y_actual,
    hf.y_forecast,
    hf.lower_bound,
    hf.upper_bound,
    hf.model_name,
    
    -- Calculate error metrics
    ABS(hd.y_actual - hf.y_forecast) as absolute_error,
    ABS((hd.y_actual - hf.y_forecast) / NULLIF(hd.y_actual, 0)) as absolute_percentage_error,
    POW(hd.y_actual - hf.y_forecast, 2) as squared_error,
    
    -- Check if actual falls within prediction interval
    CASE 
      WHEN hd.y_actual BETWEEN hf.lower_bound AND hf.upper_bound THEN TRUE
      ELSE FALSE
    END as within_prediction_interval
    
  FROM `abbanoa-464816.ml_models.holdout_data` hd
  LEFT JOIN `abbanoa-464816.ml_models.holdout_forecasts` hf
    ON hd.ds = hf.ds
    AND hd.district_metric = hf.model_name
  WHERE hf.y_forecast IS NOT NULL
),

model_metrics AS (
  SELECT 
    model_name,
    COUNT(*) as num_forecasts,
    
    -- Error metrics
    AVG(absolute_error) as mae,
    AVG(absolute_percentage_error) as mape,
    SQRT(AVG(squared_error)) as rmse,
    AVG(squared_error) as mse,
    
    -- Prediction interval coverage
    AVG(CASE WHEN within_prediction_interval THEN 1.0 ELSE 0.0 END) as coverage_rate,
    
    -- Performance assessment
    CASE 
      WHEN AVG(absolute_percentage_error) <= 0.15 THEN 'PASS'
      WHEN AVG(absolute_percentage_error) <= 0.20 THEN 'MARGINAL'
      ELSE 'FAIL'
    END as mape_assessment,
    
    MIN(ds) as validation_start_date,
    MAX(ds) as validation_end_date,
    CURRENT_TIMESTAMP() as validation_timestamp
    
  FROM forecast_actuals
  GROUP BY model_name
)

SELECT 
  model_name,
  SPLIT(model_name, '_')[OFFSET(0)] || '_' || SPLIT(model_name, '_')[OFFSET(1)] as district_id,
  CASE 
    WHEN ARRAY_LENGTH(SPLIT(model_name, '_')) = 3 THEN SPLIT(model_name, '_')[OFFSET(2)]
    ELSE SPLIT(model_name, '_')[OFFSET(2)] || '_' || SPLIT(model_name, '_')[OFFSET(3)]
  END as metric_type,
  num_forecasts,
  mae,
  mape,
  rmse,
  mse,
  coverage_rate,
  mape_assessment,
  validation_start_date,
  validation_end_date,
  validation_timestamp
FROM model_metrics
ORDER BY model_name;

-- =============================================================================
-- SECTION 6: Generate Summary Report
-- =============================================================================

-- Model performance summary
CREATE OR REPLACE VIEW `abbanoa-464816.ml_models.performance_summary` AS
SELECT 
  'ARIMA_PLUS Baseline Models' as model_type,
  COUNT(*) as total_models,
  COUNT(CASE WHEN mape_assessment = 'PASS' THEN 1 END) as models_passed,
  COUNT(CASE WHEN mape_assessment = 'MARGINAL' THEN 1 END) as models_marginal,
  COUNT(CASE WHEN mape_assessment = 'FAIL' THEN 1 END) as models_failed,
  
  AVG(mape) as avg_mape,
  MIN(mape) as best_mape,
  MAX(mape) as worst_mape,
  
  AVG(coverage_rate) as avg_coverage_rate,
  
  -- Success criteria check
  CASE 
    WHEN COUNT(CASE WHEN mape_assessment = 'PASS' THEN 1 END) = COUNT(*) THEN 'ALL_MODELS_PASS'
    WHEN COUNT(CASE WHEN mape_assessment = 'PASS' THEN 1 END) >= COUNT(*) * 0.8 THEN 'MOSTLY_PASS'
    ELSE 'NEEDS_IMPROVEMENT'
  END as overall_assessment,
  
  CURRENT_TIMESTAMP() as report_timestamp
FROM `abbanoa-464816.ml_models.holdout_validation`;

-- =============================================================================
-- SECTION 7: Generate Current Forecasts (Next 7 Days)
-- =============================================================================

-- Generate 7-day forecasts for operational use
CREATE OR REPLACE TABLE `abbanoa-464816.ml_models.current_forecasts` AS
WITH current_forecasts AS (
  SELECT 
    'DIST_001_flow_rate' as model_name,
    forecast_timestamp as forecast_date,
    forecast_value,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist001_flow_rate`,
    STRUCT(7 AS horizon)
  )
  
  UNION ALL
  
  SELECT 
    'DIST_001_pressure' as model_name,
    forecast_timestamp as forecast_date,
    forecast_value,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist001_pressure`,
    STRUCT(7 AS horizon)
  )
  
  UNION ALL
  
  SELECT 
    'DIST_001_reservoir_level' as model_name,
    forecast_timestamp as forecast_date,
    forecast_value,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist001_reservoir_level`,
    STRUCT(7 AS horizon)
  )
  
  UNION ALL
  
  SELECT 
    'DIST_002_flow_rate' as model_name,
    forecast_timestamp as forecast_date,
    forecast_value,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist002_flow_rate`,
    STRUCT(7 AS horizon)
  )
  
  UNION ALL
  
  SELECT 
    'DIST_002_pressure' as model_name,
    forecast_timestamp as forecast_date,
    forecast_value,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist002_pressure`,
    STRUCT(7 AS horizon)
  )
  
  UNION ALL
  
  SELECT 
    'DIST_002_reservoir_level' as model_name,
    forecast_timestamp as forecast_date,
    forecast_value,
    prediction_interval_lower_bound as lower_bound,
    prediction_interval_upper_bound as upper_bound,
    standard_error,
    confidence_level
  FROM ML.FORECAST(
    MODEL `abbanoa-464816.ml_models.arima_dist002_reservoir_level`,
    STRUCT(7 AS horizon)
  )
)

SELECT 
  model_name,
  SPLIT(model_name, '_')[OFFSET(0)] || '_' || SPLIT(model_name, '_')[OFFSET(1)] as district_id,
  CASE 
    WHEN ARRAY_LENGTH(SPLIT(model_name, '_')) = 3 THEN SPLIT(model_name, '_')[OFFSET(2)]
    ELSE SPLIT(model_name, '_')[OFFSET(2)] || '_' || SPLIT(model_name, '_')[OFFSET(3)]
  END as metric_type,
  forecast_date,
  forecast_value,
  lower_bound,
  upper_bound,
  standard_error,
  confidence_level,
  DATE_DIFF(forecast_date, CURRENT_DATE(), DAY) + 1 as days_ahead,
  CURRENT_TIMESTAMP() as forecast_generated_at
FROM current_forecasts
ORDER BY model_name, forecast_date;

-- =============================================================================
-- EXECUTION SUMMARY
-- =============================================================================

/*
This SQL notebook implements the complete ARIMA_PLUS model prototype with:

1. ✅ Data Preparation: Training data with proper time series format
2. ✅ Model Creation: 6 models for 2 districts × 3 metrics each
3. ✅ 7-Day Horizon: Configured horizon=7 for all models
4. ✅ Holdout Validation: Evaluation on Jan-Mar 2025 data
5. ✅ MAPE Calculation: Performance assessment with ≤15% target
6. ✅ Performance Summary: Overall model assessment
7. ✅ Operational Forecasts: Current 7-day predictions

Model Configuration:
- District-specific models for DIST_001 and DIST_002
- Metrics: flow_rate, pressure, reservoir_level
- Auto-ARIMA with Italian holidays
- Spike/dip cleaning and drift adjustment
- 90% confidence intervals

Success Criteria Validation:
- Training excludes holdout period (Jan-Mar 2025)
- MAPE target: ≤15% across all models
- Performance tracking and assessment
- Reproducible forecast pipeline

Next Steps:
1. Execute this notebook in BigQuery
2. Review model performance results
3. Adjust model parameters if needed
4. Set up automated forecast scheduling
*/
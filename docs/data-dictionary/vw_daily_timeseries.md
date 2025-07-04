# Data Dictionary: vw_daily_timeseries

**View Name:** `vw_daily_timeseries`  
**Purpose:** Daily aggregated sensor readings with gap-filling for complete time series analysis  
**Owner:** Data Engineering Team  
**Created:** 2025-07-04  
**Last Updated:** 2025-07-04  
**Version:** 1.0  

## Overview

The `vw_daily_timeseries` view provides a comprehensive daily aggregation of sensor readings across the water distribution network. It includes statistical aggregations, data quality metrics, gap-filling for missing dates, and derived analytical features to support operational monitoring and predictive analytics.

### Key Features
- **Complete Time Series**: Ensures no missing dates with gap-filling logic
- **Multi-Metric Support**: Aggregates flow rate, pressure, and reservoir level data
- **Statistical Analysis**: Provides percentiles, standard deviation, and variation metrics
- **Data Quality Tracking**: Includes quality scores and completeness indicators
- **Performance Optimized**: Sub-second query performance for 5 years of data

## Schema Definition

### Time Dimensions

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `date_utc` | DATE | Date in UTC timezone | `2024-01-15` |
| `day_of_week` | INTEGER | Day of week (1=Sunday, 7=Saturday) | `2` (Monday) |
| `month_number` | INTEGER | Month number (1-12) | `1` (January) |
| `year_number` | INTEGER | Year | `2024` |
| `season` | STRING | Seasonal indicator | `WINTER`, `SPRING`, `SUMMER`, `FALL` |
| `day_type` | STRING | Day type indicator | `WEEKDAY`, `WEEKEND` |

### Location and Metric Dimensions

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `district_id` | STRING | Unique district identifier | `DIST_001` |
| `district_name` | STRING | Human-readable district name | `Central Business District` |
| `population_served` | INTEGER | Population served by district | `50000` |
| `metric_type` | STRING | Type of measurement | `flow_rate`, `pressure`, `reservoir_level` |
| `metric_name` | STRING | Human-readable metric name | `Water Flow Rate` |
| `unit_of_measurement` | STRING | Measurement unit | `L/s`, `bar`, `m` |

### Core Aggregated Values

| Column | Data Type | Description | Range/Notes |
|--------|-----------|-------------|-------------|
| `avg_value` | FLOAT64 | Daily average of readings | Varies by metric type |
| `min_value` | FLOAT64 | Minimum daily reading | Varies by metric type |
| `max_value` | FLOAT64 | Maximum daily reading | Varies by metric type |
| `sum_value` | FLOAT64 | Sum of all readings (for volumetric metrics) | ≥ 0 |
| `count_readings` | INTEGER | Number of readings for the day | 0 to expected_daily_readings |
| `stddev_value` | FLOAT64 | Standard deviation of readings | ≥ 0, NULL if count_readings ≤ 1 |

### Percentile Analysis

| Column | Data Type | Description | Usage |
|--------|-----------|-------------|-------|
| `percentile_10` | FLOAT64 | 10th percentile value | Lower bound analysis |
| `percentile_25` | FLOAT64 | 25th percentile (Q1) | Quartile analysis |
| `median_value` | FLOAT64 | 50th percentile (median) | Central tendency |
| `percentile_75` | FLOAT64 | 75th percentile (Q3) | Quartile analysis |
| `percentile_90` | FLOAT64 | 90th percentile | Upper bound analysis |
| `percentile_95` | FLOAT64 | 95th percentile | Outlier detection |

### Data Quality Metrics

| Column | Data Type | Description | Interpretation |
|--------|-----------|-------------|----------------|
| `high_quality_readings` | INTEGER | Count of readings with quality_score ≥ 0.9 | Higher = better data quality |
| `low_quality_readings` | INTEGER | Count of readings with quality_score < 0.5 | Lower = better data quality |
| `avg_quality_score` | FLOAT64 | Average quality score for the day | 0.0 to 1.0, higher = better |
| `hours_with_data` | INTEGER | Number of hours with at least one reading | 0 to 24 |
| `first_reading_time` | TIMESTAMP | Timestamp of first reading of the day | UTC timezone |
| `last_reading_time` | TIMESTAMP | Timestamp of last reading of the day | UTC timezone |
| `potential_anomalies` | INTEGER | Count of potential anomalous readings | Lower = more stable |

### Data Completeness and Quality Flags

| Column | Data Type | Description | Values |
|--------|-----------|-------------|--------|
| `expected_daily_readings` | INTEGER | Expected number of readings per day | Based on metric frequency |
| `data_completeness_pct` | FLOAT64 | Percentage of expected readings received | 0.0 to 100.0 |
| `gap_filled_flag` | BOOLEAN | Indicates if this is a gap-filled record | `TRUE` = no actual data |
| `forward_filled_flag` | BOOLEAN | Indicates if values were forward-filled | `TRUE` = interpolated |
| `data_quality_flag` | STRING | Overall data quality assessment | See values below |

#### Data Quality Flag Values

| Value | Description | Criteria |
|-------|-------------|----------|
| `GOOD` | High-quality, complete data | Complete day, good quality, minimal anomalies |
| `NO_DATA` | No sensor readings available | Gap-filled record |
| `NO_READINGS` | Day exists but no valid readings | count_readings = 0 |
| `POOR_QUALITY` | Low-quality sensor readings | avg_quality_score < 0.5 |
| `INCOMPLETE_DAY` | Partial day coverage | hours_with_data < 12 |
| `HIGH_ANOMALIES` | Many anomalous readings | potential_anomalies > 5 |

### Operational Values

| Column | Data Type | Description | Notes |
|--------|-----------|-------------|-------|
| `avg_value_operational` | FLOAT64 | Forward-filled average for operational continuity | Used for critical metrics when avg_value is NULL |

### Derived Analytics

| Column | Data Type | Description | Calculation |
|--------|-----------|-------------|-------------|
| `daily_variation_pct` | FLOAT64 | Daily variation as percentage of average | `(max_value - min_value) / avg_value * 100` |
| `interquartile_range` | FLOAT64 | Spread between Q3 and Q1 | `percentile_75 - percentile_25` |

## Data Sources

### Primary Sources
- **`raw_data.sensor_readings`**: Raw sensor measurements with 15-minute frequency
- **`reference.district_metadata`**: District configuration and metadata
- **`reference.metric_definitions`**: Metric type definitions and specifications

### Data Lineage
```
sensor_readings (raw) 
    → daily_aggregates (CTE)
    → gap_filled_data (CTE) 
    → forward_filled (CTE)
    → vw_daily_timeseries (final view)
```

## Usage Guidelines

### Recommended Query Patterns

#### 1. Time-Series Analysis
```sql
SELECT 
    date_utc,
    district_id,
    metric_type,
    avg_value,
    median_value
FROM `abbanoa-464816.water_infrastructure.vw_daily_timeseries`
WHERE date_utc BETWEEN '2024-01-01' AND '2024-12-31'
    AND district_id = 'DIST_001'
    AND metric_type = 'flow_rate'
    AND data_quality_flag = 'GOOD'
ORDER BY date_utc
```

#### 2. Data Quality Assessment
```sql
SELECT 
    district_id,
    metric_type,
    COUNT(*) as total_days,
    COUNT(CASE WHEN data_quality_flag = 'GOOD' THEN 1 END) as good_days,
    AVG(data_completeness_pct) as avg_completeness
FROM `abbanoa-464816.water_infrastructure.vw_daily_timeseries`
WHERE date_utc BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY district_id, metric_type
```

#### 3. Seasonal Pattern Analysis
```sql
SELECT 
    season,
    metric_type,
    AVG(avg_value) as seasonal_average,
    STDDEV(avg_value) as seasonal_variation
FROM `abbanoa-464816.water_infrastructure.vw_daily_timeseries`
WHERE data_quality_flag = 'GOOD'
    AND avg_value IS NOT NULL
GROUP BY season, metric_type
```

### Performance Optimization Tips

1. **Always use date filters**: Include `date_utc` filters to enable partition pruning
2. **Filter early**: Apply `district_id` and `metric_type` filters for better performance
3. **Use LIMIT**: Add LIMIT clause for exploratory queries
4. **Consider data quality**: Filter by `data_quality_flag = 'GOOD'` for analysis

#### Efficient Query Example
```sql
SELECT *
FROM `abbanoa-464816.water_infrastructure.vw_daily_timeseries`
WHERE date_utc >= '2024-01-01'  -- Partition pruning
    AND district_id IN ('DIST_001', 'DIST_002')  -- Clustering optimization
    AND metric_type = 'flow_rate'  -- Further filtering
    AND data_quality_flag = 'GOOD'  -- Quality filtering
LIMIT 1000  -- Limit results
```

## Data Quality Considerations

### Expected Data Patterns

| Metric Type | Typical Range | Expected Pattern |
|-------------|---------------|------------------|
| `flow_rate` | 50-8,000 L/s | Daily peaks during business hours |
| `pressure` | 2.0-8.0 bar | Relatively stable with demand variations |
| `reservoir_level` | 1.0-20.0 m | Gradual changes, seasonal patterns |

### Gap-Filling Logic

1. **Date Spine**: Complete date range generated for last 5 years
2. **Cross Join**: All district-metric combinations included
3. **Left Join**: Actual data joined where available
4. **Forward Fill**: Critical metrics (pressure, reservoir_level) use last known value
5. **Flags**: `gap_filled_flag` and `forward_filled_flag` indicate interpolated data

### Data Freshness

- **Update Frequency**: View reflects latest raw data (near real-time)
- **Data Latency**: Sensor readings typically arrive within 2 hours
- **Historical Coverage**: 5 years of data available
- **Gap Handling**: Automatic gap detection and filling

## Performance Characteristics

### Query Performance Targets

| Query Type | Target Time | Typical Result Size |
|------------|-------------|-------------------|
| 5-year full scan | < 1 second | ~500K rows |
| Single month | < 100ms | ~3K rows |
| Filtered query | < 500ms | Variable |

### Optimization Features

- **Partitioning**: By `date_utc` for optimal time-range queries
- **Clustering**: By `district_id` and `metric_type` for filtered queries
- **Approximation**: Uses `APPROX_QUANTILES` for percentile calculations
- **Efficient CTEs**: Optimized Common Table Expression structure

## Monitoring and Alerting

### Automated Monitoring

- **Query Performance**: Alerts if queries exceed 2-second threshold
- **Data Freshness**: Alerts if data is older than 25 hours
- **Error Rate**: Alerts if view query error rate > 5%
- **Usage Patterns**: Monitors for unusual query patterns

### Key Metrics to Monitor

1. **Daily Row Count**: Should be consistent (~6 districts × 3 metrics × days)
2. **Data Quality Distribution**: Track percentage of 'GOOD' vs other flags
3. **Gap-Filled Percentage**: Monitor percentage of gap-filled records
4. **Query Performance**: Track 95th percentile query response times

## Change Management

### Version Control
- **Schema Changes**: Require approval from Data Architecture team
- **Breaking Changes**: Must include migration plan and user notification
- **Backward Compatibility**: Maintain for at least 6 months

### Deployment Process
1. Deploy to `dev` environment first
2. Run comprehensive test suite
3. Deploy to `staging` for user acceptance testing
4. Deploy to `prod` with monitoring
5. Post-deployment validation and performance testing

## Support and Troubleshooting

### Common Issues

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Slow queries | Query timeout or >2s execution | Add date filter, check partition pruning |
| Missing data | Unexpected gap_filled_flag=TRUE | Check raw sensor_readings table |
| Quality issues | High low_quality_readings count | Investigate sensor calibration |
| Anomaly spikes | High potential_anomalies count | Review raw data for sensor malfunction |

### Contact Information

- **Primary Owner**: Data Engineering Team (data-engineers@abbanoa.com)
- **Secondary Contact**: Water Operations Team (operations-team@abbanoa.com)
- **On-Call Support**: PagerDuty "Water Data Platform" service

### Related Documentation

- [Functional Scope Document](../functional-scope.md)
- [KPI Definitions](../kpi-definitions.md)
- [BigQuery Best Practices](../engineering/bigquery-guidelines.md)
- [Data Quality Standards](../engineering/data-quality-standards.md)
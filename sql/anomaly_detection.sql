-- Detect consumption anomalies using statistical thresholds
WITH consumption_stats AS (
    SELECT 
        _pcr_unit,
        _data_type,
        AVG(value) as mean_value,
        STDDEV(value) as stddev_value
    FROM `abbanoa-464816.teatinos_infrastructure.sensor_data`
    WHERE _data_type IN ('consumption', 'consumption-flow')
        AND datetime >= DATE_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
    GROUP BY _pcr_unit, _data_type
),
anomalies AS (
    SELECT 
        r.datetime,
        r._pcr_unit,
        r._data_type,
        r.value,
        s.mean_value,
        s.stddev_value,
        ABS(r.value - s.mean_value) / s.stddev_value as z_score
    FROM `abbanoa-464816.teatinos_infrastructure.sensor_data` r
    JOIN consumption_stats s 
        ON r._pcr_unit = s._pcr_unit 
        AND r._data_type = s._data_type
    WHERE r.datetime >= DATE_SUB(CURRENT_DATETIME(), INTERVAL 7 DAY)
        AND s.stddev_value > 0
)
SELECT *
FROM anomalies
WHERE z_score > 2.5  -- Values more than 2.5 standard deviations from mean
ORDER BY z_score DESC, datetime DESC
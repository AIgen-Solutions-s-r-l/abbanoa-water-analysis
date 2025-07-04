-- Flow rate monitoring analysis
SELECT 
    DATETIME_TRUNC(datetime, HOUR) as hour,
    _pcr_unit,
    ROUND(AVG(value), 3) as avg_flow_rate,
    ROUND(STDDEV(value), 3) as flow_variance,
    COUNT(*) as measurements
FROM `abbanoa-464816.teatinos_infrastructure.sensor_data`
WHERE _data_type = 'consumption-flow'
    AND datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 7 DAY)
GROUP BY hour, _pcr_unit
ORDER BY hour DESC
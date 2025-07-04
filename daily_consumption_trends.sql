-- Daily consumption trends for Teatinos site
SELECT 
    DATE(datetime) as date,
    _pcr_unit,
    _sensor_type,
    ROUND(AVG(value), 2) as avg_daily_consumption,
    ROUND(MIN(value), 2) as min_consumption,
    ROUND(MAX(value), 2) as max_consumption,
    unit
FROM `abbanoa-464816.teatinos_infrastructure.sensor_data`
WHERE _data_type = 'consumption'
    AND datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY DATE(datetime), _pcr_unit, _sensor_type, unit
ORDER BY date DESC, _pcr_unit
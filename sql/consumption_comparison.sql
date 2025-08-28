-- Compare consumption between PCR units
WITH daily_consumption AS (
    SELECT 
        DATE(datetime) as date,
        _pcr_unit,
        SUM(value) as total_consumption
    FROM `abbanoa-464816.teatinos_infrastructure.sensor_data`
    WHERE _data_type = 'consumption'
        AND datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    GROUP BY DATE(datetime), _pcr_unit
)
SELECT 
    date,
    SUM(CASE WHEN _pcr_unit LIKE '%PCR-4%' THEN total_consumption END) as pcr4_consumption,
    SUM(CASE WHEN _pcr_unit LIKE '%PCR-5%' THEN total_consumption END) as pcr5_consumption,
    SUM(total_consumption) as total_site_consumption
FROM daily_consumption
GROUP BY date
ORDER BY date DESC
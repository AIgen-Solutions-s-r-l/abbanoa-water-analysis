-- ============================================
-- LOOKER STUDIO CUSTOM QUERIES
-- Copy and paste these queries when setting up data sources
-- ============================================

-- ============================================
-- QUERY 1: Real-Time Metrics
-- Use this for: KPI cards, time series charts, current status
-- ============================================

WITH latest_data AS (
  SELECT 
    data,
    ora,
    selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as sant_anna_flow,
    selargius_nodo_via_seneca_portata_w_istantanea_diretta as seneca_flow,
    selargius_serbatoio_selargius_portata_uscita as tank_output,
    quartucciu_serbatoio_cuccuru_linu_portata_selargius as external_supply,
    selargius_nodo_via_sant_anna_temperatura_interna as sant_anna_temp,
    selargius_nodo_via_seneca_temperatura_interna as seneca_temp,
    DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as datetime_combined,
    _ingestion_timestamp,
    ROW_NUMBER() OVER (ORDER BY _ingestion_timestamp DESC) as row_num
  FROM `abbanoa-464816.water_infrastructure.sensor_data`
  WHERE data IS NOT NULL AND ora IS NOT NULL
)
SELECT 
  datetime_combined,
  data as date_string,
  ora as time_string,
  sant_anna_flow,
  seneca_flow,
  tank_output,
  external_supply,
  sant_anna_temp,
  seneca_temp,
  CASE 
    WHEN sant_anna_flow > 120 THEN 'HIGH'
    WHEN sant_anna_flow < 30 THEN 'LOW' 
    ELSE 'NORMAL'
  END as flow_status,
  COALESCE(sant_anna_flow, 0) + COALESCE(seneca_flow, 0) + COALESCE(external_supply, 0) as total_input,
  COALESCE(sant_anna_flow, 0) + COALESCE(seneca_flow, 0) + COALESCE(external_supply, 0) - COALESCE(tank_output, 0) as apparent_loss
FROM latest_data
ORDER BY datetime_combined DESC

-- ============================================
-- QUERY 2: Hourly Patterns
-- Use this for: Heatmaps, hourly analysis, consumption patterns
-- ============================================

SELECT 
  EXTRACT(HOUR FROM PARSE_TIME('%H:%M:%S', ora)) as hour_of_day,
  EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data)) as day_of_week,
  CASE EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data))
    WHEN 1 THEN 'Sunday'
    WHEN 2 THEN 'Monday'
    WHEN 3 THEN 'Tuesday'
    WHEN 4 THEN 'Wednesday'
    WHEN 5 THEN 'Thursday'
    WHEN 6 THEN 'Friday'
    WHEN 7 THEN 'Saturday'
  END as day_name,
  AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as avg_flow_rate,
  STDDEV(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as stddev_flow_rate,
  MIN(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as min_flow_rate,
  MAX(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as max_flow_rate,
  COUNT(*) as measurements,
  AVG(selargius_serbatoio_selargius_portata_uscita) as avg_tank_output
FROM `abbanoa-464816.water_infrastructure.sensor_data`
WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
  AND ora IS NOT NULL 
  AND data IS NOT NULL
GROUP BY hour_of_day, day_of_week, day_name
ORDER BY day_of_week, hour_of_day

-- ============================================
-- QUERY 3: Daily Aggregates
-- Use this for: Historical trends, efficiency metrics, summary tables
-- ============================================

SELECT 
  PARSE_DATE('%d/%m/%Y', data) as date_parsed,
  data as date_string,
  COUNT(*) as total_measurements,
  AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as avg_sant_anna_flow,
  MAX(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as max_sant_anna_flow,
  MIN(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as min_sant_anna_flow,
  AVG(selargius_serbatoio_selargius_portata_uscita) as avg_tank_output,
  AVG(quartucciu_serbatoio_cuccuru_linu_portata_selargius) as avg_external_supply,
  AVG(selargius_nodo_via_sant_anna_temperatura_interna) as avg_temperature,
  SUM(selargius_nodo_via_sant_anna_portata_w_totale_diretta) as total_volume_m3,
  AVG(COALESCE(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta, 0) + 
      COALESCE(selargius_nodo_via_seneca_portata_w_istantanea_diretta, 0) + 
      COALESCE(quartucciu_serbatoio_cuccuru_linu_portata_selargius, 0) - 
      COALESCE(selargius_serbatoio_selargius_portata_uscita, 0)) as avg_apparent_loss
FROM `abbanoa-464816.water_infrastructure.sensor_data`
WHERE data IS NOT NULL
GROUP BY data, date_parsed
ORDER BY date_parsed DESC

-- ============================================
-- BONUS QUERY 4: Current Status (Single Row)
-- Use this for: Real-time status widgets, alerts
-- ============================================

WITH latest_reading AS (
  SELECT 
    data,
    ora,
    selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as current_flow,
    selargius_serbatoio_selargius_portata_uscita as current_tank_output,
    selargius_nodo_via_sant_anna_temperatura_interna as current_temperature,
    DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as last_reading_time,
    ROW_NUMBER() OVER (ORDER BY _ingestion_timestamp DESC) as rn
  FROM `abbanoa-464816.water_infrastructure.sensor_data`
  WHERE data IS NOT NULL AND ora IS NOT NULL
)
SELECT 
  last_reading_time,
  current_flow,
  current_tank_output,
  current_temperature,
  CASE 
    WHEN current_flow > 120 THEN 'HIGH FLOW ALERT'
    WHEN current_flow < 30 THEN 'LOW FLOW WARNING'
    WHEN current_temperature > 25 THEN 'HIGH TEMPERATURE'
    ELSE 'SYSTEM NORMAL'
  END as system_status,
  CASE 
    WHEN current_flow > 120 OR current_flow < 30 OR current_temperature > 25 THEN 'ATTENTION_NEEDED'
    ELSE 'OK'
  END as alert_level
FROM latest_reading 
WHERE rn = 1 
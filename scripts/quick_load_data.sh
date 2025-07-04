#!/bin/bash
# Quick script to load sample data into BigQuery using bq CLI

PROJECT_ID="abbanoa-464816"
DATASET_ID="water_infrastructure"

# Create tables using bq CLI
echo "Creating tables..."

# Create water_networks table
bq mk --table \
  --project_id=$PROJECT_ID \
  $DATASET_ID.water_networks \
  id:STRING,name:STRING,service_area:STRING,total_nodes:INTEGER,total_length_km:FLOAT,created_at:TIMESTAMP,updated_at:TIMESTAMP

# Create monitoring_nodes table  
bq mk --table \
  --project_id=$PROJECT_ID \
  $DATASET_ID.monitoring_nodes \
  id:STRING,network_id:STRING,name:STRING,node_type:STRING,location_lat:FLOAT,location_lon:FLOAT,installation_date:DATE,is_active:BOOLEAN,metadata:JSON,created_at:TIMESTAMP,updated_at:TIMESTAMP

# Create sensor_readings table with partitioning
bq mk --table \
  --project_id=$PROJECT_ID \
  --time_partitioning_field=timestamp \
  --clustering_fields=node_id,timestamp \
  $DATASET_ID.sensor_readings \
  id:STRING,node_id:STRING,timestamp:TIMESTAMP,temperature:FLOAT,flow_rate:FLOAT,pressure:FLOAT,volume:FLOAT,is_anomalous:BOOLEAN,created_at:TIMESTAMP,updated_at:TIMESTAMP

echo "Tables created!"

# Insert sample data
echo "Inserting sample data..."

# Insert network
bq query --project_id=$PROJECT_ID --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.water_networks\`
VALUES
  ('net-001', 'Selargius Water Network', 'Selargius', 4, 50.5, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
"

# Insert nodes
bq query --project_id=$PROJECT_ID --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.monitoring_nodes\`
VALUES
  ('node-001', 'net-001', 'SELARGIUS NODO VIA SANT ANNA', 'distribution', 39.2238, 9.1422, NULL, true, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
  ('node-002', 'net-001', 'SELARGIUS NODO VIA SENECA', 'distribution', 39.2238, 9.1422, NULL, true, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
  ('node-003', 'net-001', 'SELARGIUS SERBATOIO SELARGIUS', 'storage', 39.2238, 9.1422, NULL, true, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
  ('node-004', 'net-001', 'QUARTUCCIU SERBATOIO CUCCURU LINU', 'storage', 39.2238, 9.1422, NULL, true, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
"

# Insert some sample readings
bq query --project_id=$PROJECT_ID --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.sensor_readings\`
SELECT
  GENERATE_UUID() as id,
  node_id,
  TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -n HOUR) as timestamp,
  20.0 + RAND() * 5 as temperature,
  80.0 + RAND() * 40 as flow_rate,
  3.5 + RAND() * 1.5 as pressure,
  1000.0 + n * 50 as volume,
  false as is_anomalous,
  CURRENT_TIMESTAMP() as created_at,
  CURRENT_TIMESTAMP() as updated_at
FROM 
  UNNEST(['node-001', 'node-002', 'node-003', 'node-004']) as node_id,
  UNNEST(GENERATE_ARRAY(0, 24)) as n
"

echo "Sample data loaded!"

# Test query
echo "Testing data..."
bq query --project_id=$PROJECT_ID --use_legacy_sql=false "
SELECT 
  COUNT(*) as total_readings,
  COUNT(DISTINCT node_id) as unique_nodes,
  AVG(flow_rate) as avg_flow_rate,
  AVG(pressure) as avg_pressure
FROM \`$PROJECT_ID.$DATASET_ID.sensor_readings\`
"

echo "✅ Done! Sample data is now in BigQuery."
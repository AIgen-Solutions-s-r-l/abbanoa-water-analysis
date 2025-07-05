#!/usr/bin/env python3
"""Load sample data using BigQuery REST API."""

import json
import subprocess
from datetime import datetime, timedelta
import uuid

# Configuration
PROJECT_ID = "abbanoa-464816"
DATASET_ID = "water_infrastructure"

# Get access token
token = subprocess.check_output(['gcloud', 'auth', 'application-default', 'print-access-token']).decode().strip()

def execute_query(query):
    """Execute a BigQuery query using REST API."""
    import requests
    
    url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT_ID}/queries"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "query": query,
        "useLegacySql": False,
        "location": "EU"
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Query executed successfully")
        if 'rows' in result:
            for row in result['rows']:
                print(row)
    
    return result


def main():
    """Main function."""
    print("Loading sample data into BigQuery...")
    
    # Create tables
    print("\n1. Creating tables...")
    
    # Create water_networks table
    query1 = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.water_networks` (
        id STRING NOT NULL,
        name STRING NOT NULL,
        service_area STRING NOT NULL,
        total_nodes INT64 NOT NULL,
        total_length_km FLOAT64 NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    )
    """
    execute_query(query1)
    
    # Create monitoring_nodes table
    query2 = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.monitoring_nodes` (
        id STRING NOT NULL,
        network_id STRING NOT NULL,
        name STRING NOT NULL,
        node_type STRING NOT NULL,
        location_lat FLOAT64,
        location_lon FLOAT64,
        installation_date DATE,
        is_active BOOLEAN NOT NULL,
        metadata JSON,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    )
    """
    execute_query(query2)
    
    # Create sensor_readings table
    query3 = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.sensor_readings` (
        id STRING NOT NULL,
        node_id STRING NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        temperature FLOAT64,
        flow_rate FLOAT64,
        pressure FLOAT64,
        volume FLOAT64,
        is_anomalous BOOLEAN NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    )
    PARTITION BY DATE(timestamp)
    CLUSTER BY node_id, timestamp
    """
    execute_query(query3)
    
    print("\n2. Inserting sample data...")
    
    # Insert network
    network_id = str(uuid.uuid4())
    query4 = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.water_networks`
    VALUES
      ('{network_id}', 'Selargius Water Network', 'Selargius', 4, 50.5, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
    """
    execute_query(query4)
    
    # Insert nodes
    nodes = [
        ('node-001', 'SELARGIUS NODO VIA SANT ANNA', 'distribution'),
        ('node-002', 'SELARGIUS NODO VIA SENECA', 'distribution'),
        ('node-003', 'SELARGIUS SERBATOIO SELARGIUS', 'storage'),
        ('node-004', 'QUARTUCCIU SERBATOIO CUCCURU LINU', 'storage')
    ]
    
    values = []
    for node_id, name, node_type in nodes:
        values.append(f"('{node_id}', '{network_id}', '{name}', '{node_type}', 39.2238, 9.1422, NULL, true, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())")
    
    query5 = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.monitoring_nodes`
    VALUES {', '.join(values)}
    """
    execute_query(query5)
    
    # Insert readings for last 24 hours
    print("\n3. Inserting sensor readings...")
    
    now = datetime.utcnow()
    readings = []
    
    for hour in range(24):
        timestamp = now - timedelta(hours=hour)
        for node_id, _, _ in nodes:
            reading_id = str(uuid.uuid4())
            temp = 20.0 + (hour % 12) * 0.5  # Temperature varies during day
            flow = 80.0 + (hour % 8) * 5.0   # Flow rate pattern
            pressure = 4.0 + (hour % 6) * 0.1 # Pressure variation
            volume = 1000.0 + hour * 50       # Cumulative volume
            
            readings.append(
                f"('{reading_id}', '{node_id}', TIMESTAMP('{timestamp.isoformat()}'), "
                f"{temp}, {flow}, {pressure}, {volume}, false, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())"
            )
    
    # Insert in batches
    batch_size = 100
    for i in range(0, len(readings), batch_size):
        batch = readings[i:i+batch_size]
        query = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.sensor_readings`
        VALUES {', '.join(batch)}
        """
        execute_query(query)
    
    print("\n4. Testing data...")
    
    # Test query
    test_query = f"""
    SELECT 
      COUNT(*) as total_readings,
      COUNT(DISTINCT node_id) as unique_nodes,
      AVG(flow_rate) as avg_flow_rate,
      AVG(pressure) as avg_pressure,
      MIN(timestamp) as earliest,
      MAX(timestamp) as latest
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings`
    """
    execute_query(test_query)
    
    print("\n✅ Sample data loaded successfully!")
    print(f"\nYou can now access the data in BigQuery:")
    print(f"  Project: {PROJECT_ID}")
    print(f"  Dataset: {DATASET_ID}")
    print(f"  Tables: water_networks, monitoring_nodes, sensor_readings")


if __name__ == "__main__":
    main()
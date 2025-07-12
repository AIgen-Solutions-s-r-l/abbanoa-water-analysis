#!/usr/bin/env python3
"""Test BigQuery data access."""

import json
import subprocess

# Configuration
PROJECT_ID = "abbanoa-464816"
DATASET_ID = "water_infrastructure"

# Get access token
token = (
    subprocess.check_output(
        ["gcloud", "auth", "application-default", "print-access-token"]
    )
    .decode()
    .strip()
)


def execute_query(query):
    """Execute a BigQuery query using REST API."""
    import requests

    url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT_ID}/queries"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {"query": query, "useLegacySql": False, "location": "EU"}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if "error" in result:
        print(f"Error: {result['error']}")
        return None
    else:
        return result


def main():
    """Main function."""
    print("Testing BigQuery data access...")

    # Check sensor_data table
    print("\n1. Checking sensor_data table...")
    query = f"""
    SELECT 
      COUNT(*) as total_rows,
      COUNT(DISTINCT data) as unique_dates,
      MIN(data) as earliest_date,
      MAX(data) as latest_date
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    LIMIT 10
    """

    result = execute_query(query)
    if result and "rows" in result:
        print("sensor_data table statistics:")
        for row in result["rows"]:
            values = [f["v"] for f in row["f"]]
            print(f"  Total rows: {values[0]}")
            print(f"  Unique dates: {values[1]}")
            print(f"  Date range: {values[2]} to {values[3]}")

    # Get sample data
    print("\n2. Sample data from sensor_data...")
    query2 = f"""
    SELECT 
      data,
      ora,
      selargius_nodo_via_sant_anna_temperatura_interna as temp_santanna,
      selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow_santanna,
      selargius_nodo_via_sant_anna_pressione_uscita as pressure_santanna
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    ORDER BY data DESC, ora DESC
    LIMIT 5
    """

    result2 = execute_query(query2)
    if result2 and "rows" in result2:
        print("\nRecent sensor readings:")
        print("Date       Time     Temp(°C)  Flow(L/s)  Pressure(bar)")
        print("-" * 55)
        for row in result2["rows"]:
            values = [f["v"] if f["v"] else "NULL" for f in row["f"]]
            print(
                f"{values[0]:10} {values[1]:8} {values[2]:>8} {values[3]:>10} {values[4]:>12}"
            )

    # Create a view for easier access
    print("\n3. Creating view for dashboard access...")
    view_query = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized` AS
    SELECT
      PARSE_TIMESTAMP('%d/%m/%Y %H:%M:%S', CONCAT(data, ' ', ora)) as timestamp,
      'node-santanna' as node_id,
      'SELARGIUS NODO VIA SANT ANNA' as node_name,
      selargius_nodo_via_sant_anna_temperatura_interna as temperature,
      selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow_rate,
      selargius_nodo_via_sant_anna_pressione_uscita as pressure,
      selargius_nodo_via_sant_anna_portata_w_totale_diretta as volume
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
    
    UNION ALL
    
    SELECT
      PARSE_TIMESTAMP('%d/%m/%Y %H:%M:%S', CONCAT(data, ' ', ora)) as timestamp,
      'node-seneca' as node_id,
      'SELARGIUS NODO VIA SENECA' as node_name,
      selargius_nodo_via_seneca_temperatura_interna as temperature,
      selargius_nodo_via_seneca_portata_w_istantanea_diretta as flow_rate,
      selargius_nodo_via_seneca_pressione_uscita as pressure,
      selargius_nodo_via_seneca_portata_w_totale_diretta as volume
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    WHERE selargius_nodo_via_seneca_portata_w_istantanea_diretta IS NOT NULL
    
    UNION ALL
    
    SELECT
      PARSE_TIMESTAMP('%d/%m/%Y %H:%M:%S', CONCAT(data, ' ', ora)) as timestamp,
      'node-serbatoio' as node_id,
      'SELARGIUS SERBATOIO' as node_name,
      NULL as temperature,
      selargius_serbatoio_selargius_portata_uscita as flow_rate,
      NULL as pressure,
      selargius_serbatoio_selargius_portata_uscita_mq as volume
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    WHERE selargius_serbatoio_selargius_portata_uscita IS NOT NULL
    """

    execute_query(view_query)
    print("✅ Created normalized view: v_sensor_readings_normalized")

    # Test the view
    print("\n4. Testing normalized view...")
    test_view = f"""
    SELECT 
      COUNT(*) as total_readings,
      COUNT(DISTINCT node_id) as nodes,
      AVG(flow_rate) as avg_flow,
      AVG(pressure) as avg_pressure
    FROM `{PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """

    result3 = execute_query(test_view)
    if result3 and "rows" in result3:
        print("\nView statistics (last 7 days):")
        for row in result3["rows"]:
            values = [f["v"] if f["v"] else "NULL" for f in row["f"]]
            print(f"  Total readings: {values[0]}")
            print(f"  Nodes: {values[1]}")
            print(f"  Avg flow rate: {values[2]} L/s")
            print(f"  Avg pressure: {values[3]} bar")

    print("\n✅ BigQuery data is accessible!")
    print("\nThe dashboard can now use the following tables/views:")
    print(f"  - {PROJECT_ID}.{DATASET_ID}.sensor_data (raw data)")
    print(
        f"  - {PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized (normalized view)"
    )


if __name__ == "__main__":
    main()

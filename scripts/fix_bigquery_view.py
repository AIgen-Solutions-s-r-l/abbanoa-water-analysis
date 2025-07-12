#!/usr/bin/env python3
"""Fix the BigQuery view to correctly parse dates."""

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
    print("Fixing BigQuery view date parsing...")

    # First, let's check the actual timestamp format
    print("\n1. Checking parsed timestamps...")
    query_check = """
    SELECT
      data,
      ora,
      PARSE_TIMESTAMP('%d/%m/%Y %H:%M:%S', CONCAT(data, ' ', ora)) as parsed_timestamp,
      FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', PARSE_TIMESTAMP('%d/%m/%Y %H:%M:%S', CONCAT(data, ' ', ora))) as formatted_timestamp
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    ORDER BY PARSE_TIMESTAMP('%d/%m/%Y %H:%M:%S', CONCAT(data, ' ', ora)) DESC
    LIMIT 5
    """

    result = execute_query(query_check)
    if result and "rows" in result:
        print("Sample parsed timestamps:")
        for row in result["rows"]:
            values = [f["v"] for f in row["f"]]
            print(f"  {values[0]} {values[1]} -> {values[3]}")

    # Recreate the view with proper formatting
    print("\n2. Recreating normalized view with proper date handling...")
    view_query = """
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
    print("✅ View recreated successfully")

    # Test the updated view
    print("\n3. Testing updated view...")
    test_query = """
    SELECT
      node_id,
      node_name,
      FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', MAX(timestamp)) as latest_reading,
      FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', MIN(timestamp)) as earliest_reading,
      COUNT(*) as total_readings,
      AVG(flow_rate) as avg_flow_rate
    FROM `{PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized`
    GROUP BY node_id, node_name
    ORDER BY node_id
    """

    result3 = execute_query(test_query)
    if result3 and "rows" in result3:
        print("\nNode statistics:")
        print(
            "Node ID         | Latest Reading      | Earliest Reading    | Total | Avg Flow"
        )
        print("-" * 85)
        for row in result3["rows"]:
            values = [f["v"] if f["v"] else "NULL" for f in row["f"]]
            print(
                f"{values[0]:15} | {values[2]:19} | {values[3]:19} | {values[4]:5} | {float(values[5]):.2f}"
            )

    # Check recent data
    print("\n4. Recent data sample:")
    recent_query = """
    SELECT
      FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', timestamp) as timestamp,
      node_id,
      ROUND(flow_rate, 2) as flow_rate,
      ROUND(pressure, 2) as pressure,
      ROUND(temperature, 1) as temperature
    FROM `{PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
    ORDER BY timestamp DESC
    LIMIT 10
    """

    result4 = execute_query(recent_query)
    if result4 and "rows" in result4:
        print("Timestamp            | Node           | Flow  | Press | Temp")
        print("-" * 65)
        for row in result4["rows"]:
            values = [f["v"] if f["v"] else "NULL" for f in row["f"]]
            print(
                f"{values[0]:20} | {values[1]:14} | {values[2]:5} | {values[3]:5} | {values[4]:4}"
            )


if __name__ == "__main__":
    main()

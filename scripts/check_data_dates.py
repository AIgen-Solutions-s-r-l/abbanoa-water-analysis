#!/usr/bin/env python3
"""Check the actual date range of data in BigQuery."""

import subprocess
import json

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
        return None
    else:
        return result


def main():
    """Main function."""
    print("Checking actual date ranges in BigQuery data...")
    
    # Check raw sensor_data table dates
    print("\n1. Date range in sensor_data table:")
    query1 = f"""
    SELECT 
      MIN(PARSE_DATE('%d/%m/%Y', data)) as earliest_date,
      MAX(PARSE_DATE('%d/%m/%Y', data)) as latest_date,
      COUNT(DISTINCT data) as unique_dates
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    """
    
    result = execute_query(query1)
    if result and 'rows' in result:
        for row in result['rows']:
            values = [f['v'] for f in row['f']]
            print(f"  Earliest date: {values[0]}")
            print(f"  Latest date: {values[1]}")
            print(f"  Unique dates: {values[2]}")
    
    # Check normalized view dates
    print("\n2. Date range in normalized view:")
    query2 = f"""
    SELECT 
      MIN(timestamp) as earliest_timestamp,
      MAX(timestamp) as latest_timestamp,
      COUNT(*) as total_readings,
      COUNT(DISTINCT DATE(timestamp)) as unique_dates
    FROM `{PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized`
    """
    
    result2 = execute_query(query2)
    if result2 and 'rows' in result2:
        for row in result2['rows']:
            values = [f['v'] if f['v'] else 'NULL' for f in row['f']]
            print(f"  Earliest timestamp: {values[0]}")
            print(f"  Latest timestamp: {values[1]}")
            print(f"  Total readings: {values[2]}")
            print(f"  Unique dates: {values[3]}")
    
    # Get the most recent data available
    print("\n3. Most recent data by node:")
    query3 = f"""
    SELECT 
      node_id,
      node_name,
      MAX(timestamp) as latest_reading,
      COUNT(*) as total_readings
    FROM `{PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized`
    GROUP BY node_id, node_name
    ORDER BY node_id
    """
    
    result3 = execute_query(query3)
    if result3 and 'rows' in result3:
        print("  Node ID         | Node Name                      | Latest Reading        | Total")
        print("  " + "-" * 80)
        for row in result3['rows']:
            values = [f['v'] if f['v'] else 'NULL' for f in row['f']]
            print(f"  {values[0]:15} | {values[1]:30} | {values[2]:20} | {values[3]}")
    
    # Check if we need to adjust date parsing
    print("\n4. Sample of raw dates from sensor_data:")
    query4 = f"""
    SELECT 
      data,
      ora,
      COUNT(*) as count
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_data`
    GROUP BY data, ora
    ORDER BY data DESC, ora DESC
    LIMIT 10
    """
    
    result4 = execute_query(query4)
    if result4 and 'rows' in result4:
        print("  Date       | Time     | Count")
        print("  " + "-" * 30)
        for row in result4['rows']:
            values = [f['v'] for f in row['f']]
            print(f"  {values[0]:10} | {values[1]:8} | {values[2]}")


if __name__ == "__main__":
    main()
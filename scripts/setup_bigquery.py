#!/usr/bin/env python3
"""Script to set up BigQuery tables for Abbanoa water infrastructure."""

import os
import sys
from pathlib import Path
from google.cloud import bigquery
from google.cloud.exceptions import Conflict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID", "abbanoa-464816")
DATASET_ID = os.getenv("BIGQUERY_DATASET_ID", "water_infrastructure")
LOCATION = os.getenv("BIGQUERY_LOCATION", "EU")


def create_dataset(client: bigquery.Client) -> None:
    """Create the BigQuery dataset if it doesn't exist."""
    dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = LOCATION

    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"✅ Dataset {dataset_id} is ready")
    except Exception as e:
        print(f"❌ Error creating dataset: {e}")
        raise


def create_tables(client: bigquery.Client) -> None:
    """Create the required tables."""

    # Water Networks table
    water_networks_schema = [
        bigquery.SchemaField(
            "id", "STRING", mode="REQUIRED", description="UUID primary key"
        ),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("service_area", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("total_nodes", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("total_length_km", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Monitoring Nodes table
    monitoring_nodes_schema = [
        bigquery.SchemaField(
            "id", "STRING", mode="REQUIRED", description="UUID primary key"
        ),
        bigquery.SchemaField(
            "network_id",
            "STRING",
            mode="REQUIRED",
            description="Foreign key to water_networks",
        ),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField(
            "node_type",
            "STRING",
            mode="REQUIRED",
            description="SENSOR, PUMP, VALVE, TANK",
        ),
        bigquery.SchemaField("location_lat", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("location_lon", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("installation_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Sensor Readings table
    sensor_readings_schema = [
        bigquery.SchemaField(
            "id", "STRING", mode="REQUIRED", description="UUID primary key"
        ),
        bigquery.SchemaField(
            "node_id",
            "STRING",
            mode="REQUIRED",
            description="Foreign key to monitoring_nodes",
        ),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField(
            "temperature",
            "FLOAT",
            mode="NULLABLE",
            description="Temperature in Celsius",
        ),
        bigquery.SchemaField(
            "flow_rate", "FLOAT", mode="NULLABLE", description="Flow rate in L/s"
        ),
        bigquery.SchemaField(
            "pressure", "FLOAT", mode="NULLABLE", description="Pressure in bar"
        ),
        bigquery.SchemaField(
            "volume", "FLOAT", mode="NULLABLE", description="Volume in m³"
        ),
        bigquery.SchemaField(
            "is_anomalous", "BOOLEAN", mode="REQUIRED", field_type="BOOLEAN"
        ),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Tables to create
    tables = [
        ("water_networks", water_networks_schema),
        ("monitoring_nodes", monitoring_nodes_schema),
        ("sensor_readings", sensor_readings_schema),
    ]

    for table_name, schema in tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)

        # Add clustering for sensor_readings
        if table_name == "sensor_readings":
            table.clustering_fields = ["node_id", "timestamp"]
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY, field="timestamp"
            )

        try:
            table = client.create_table(table, exists_ok=True)
            print(f"✅ Table {table_name} is ready")
        except Exception as e:
            print(f"❌ Error creating table {table_name}: {e}")
            raise


def main():
    """Main setup function."""
    print(f"Setting up BigQuery for project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Location: {LOCATION}")
    print()

    # Initialize client
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print("✅ Connected to BigQuery")
    except Exception as e:
        print(f"❌ Failed to connect to BigQuery: {e}")
        print("\nMake sure you have set up authentication:")
        print("  export GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json")
        print("  OR")
        print("  gcloud auth application-default login")
        return 1

    # Create dataset
    create_dataset(client)

    # Create tables
    create_tables(client)

    print("\n✅ BigQuery setup complete!")
    print(f"\nTables created in {PROJECT_ID}.{DATASET_ID}:")
    print("  - water_networks")
    print("  - monitoring_nodes")
    print("  - sensor_readings")

    return 0


if __name__ == "__main__":
    sys.exit(main())

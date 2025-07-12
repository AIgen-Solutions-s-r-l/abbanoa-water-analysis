#!/usr/bin/env python3
"""Simplified script to set up BigQuery tables."""

import os
import sys

# Set environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
    "~/.config/gcloud/application_default_credentials.json"
)

# Try to import after setting env var
try:
    from google.cloud import bigquery

    print("✅ Successfully imported BigQuery")
except ImportError as e:
    print(f"❌ Failed to import BigQuery: {e}")
    print("\nTrying alternative import method...")

    # Add common virtualenv paths
    venv_paths = [
        "/home/alessio/.cache/pypoetry/virtualenvs/abbanoa-water-infrastructure-RTCwCU-i-py3.12/lib/python3.12/site-packages",
        "/home/alessio/.local/lib/python3.12/site-packages",
    ]

    for path in venv_paths:
        if os.path.exists(path):
            sys.path.insert(0, path)

    try:
        from google.cloud import bigquery

        print("✅ Successfully imported BigQuery from alternative path")
    except ImportError:
        print("❌ Still cannot import BigQuery")
        print("\nPlease ensure google-cloud-bigquery is installed:")
        print("  pip install google-cloud-bigquery")
        sys.exit(1)

# Configuration
PROJECT_ID = "abbanoa-464816"
DATASET_ID = "water_infrastructure"
LOCATION = "EU"


def main():
    """Main setup function."""
    print("\nSetting up BigQuery:")
    print(f"  Project: {PROJECT_ID}")
    print(f"  Dataset: {DATASET_ID}")
    print(f"  Location: {LOCATION}")

    try:
        # Initialize client
        client = bigquery.Client(project=PROJECT_ID)
        print("\n✅ Connected to BigQuery!")

        # Check if dataset exists
        dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
        try:
            dataset = client.get_dataset(dataset_id)
            print(f"✅ Dataset {DATASET_ID} already exists")
        except:
            # Create dataset
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = LOCATION
            dataset = client.create_dataset(dataset)
            print(f"✅ Created dataset {DATASET_ID}")

        # Create tables
        tables = {
            "water_networks": """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.water_networks` (
                    id STRING NOT NULL,
                    name STRING NOT NULL,
                    service_area STRING NOT NULL,
                    total_nodes INT64 NOT NULL,
                    total_length_km FLOAT64 NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """,
            "monitoring_nodes": """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.monitoring_nodes` (
                    id STRING NOT NULL,
                    network_id STRING NOT NULL,
                    name STRING NOT NULL,
                    node_type STRING NOT NULL,
                    location_lat FLOAT64 NOT NULL,
                    location_lon FLOAT64 NOT NULL,
                    installation_date DATE NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    metadata JSON,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """,
            "sensor_readings": """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.sensor_readings` (
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
            """,
        }

        for table_name, create_sql in tables.items():
            query = create_sql.format(project=PROJECT_ID, dataset=DATASET_ID)
            job = client.query(query)
            job.result()  # Wait for completion
            print(f"✅ Table {table_name} is ready")

        print("\n✅ BigQuery setup complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

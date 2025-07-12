#!/usr/bin/env python3
"""Run data ingestion pipeline to load CSV data into BigQuery."""

import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
    "~/.config/gcloud/application_default_credentials.json"
)
os.environ["BIGQUERY_PROJECT_ID"] = "abbanoa-464816"
os.environ["BIGQUERY_DATASET_ID"] = "water_infrastructure"

from src.infrastructure.persistence.bigquery_config import BigQueryConfig
from src.infrastructure.external_services.bigquery_service import BigQueryService
from src.infrastructure.normalization.selargius_normalizer import (
    SelargiusDataNormalizer,
)
from google.cloud import bigquery
import pandas as pd


def create_tables(service: BigQueryService):
    """Create the required tables."""
    print("Creating tables...")

    # Water Networks table schema
    water_networks_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("service_area", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("total_nodes", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("total_length_km", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Monitoring Nodes table schema
    monitoring_nodes_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("network_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("node_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("location_lat", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("location_lon", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("installation_date", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Sensor Readings table schema
    sensor_readings_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("node_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("temperature", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("flow_rate", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("pressure", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("volume", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("is_anomalous", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Create tables
    service.create_table_from_schema("water_networks", water_networks_schema)
    print("✅ Created water_networks table")

    service.create_table_from_schema("monitoring_nodes", monitoring_nodes_schema)
    print("✅ Created monitoring_nodes table")

    service.create_table_from_schema(
        "sensor_readings",
        sensor_readings_schema,
        partition_field="timestamp",
        clustering_fields=["node_id", "timestamp"],
    )
    print("✅ Created sensor_readings table")


def ingest_selargius_data(service: BigQueryService, csv_path: str):
    """Ingest Selargius CSV data into BigQuery."""
    print(f"\nIngesting data from: {csv_path}")

    # Initialize normalizer
    normalizer = SelargiusDataNormalizer()

    # Normalize the file
    print("Normalizing CSV data...")
    nodes, readings, quality_metrics = normalizer.normalize_file(csv_path)

    print(f"Found {len(nodes)} nodes and {len(readings)} readings")
    print(f"Data quality: {quality_metrics.coverage_percentage:.1f}% coverage")

    # Create a default network if needed
    network_id = str(uuid4())
    network_df = pd.DataFrame(
        [
            {
                "id": network_id,
                "name": "Selargius Water Network",
                "service_area": "Selargius",
                "total_nodes": len(nodes),
                "total_length_km": 0.0,  # Unknown
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        ]
    )

    print("\nLoading water network...")
    service.load_dataframe(
        network_df, "water_networks", write_disposition="WRITE_TRUNCATE"
    )
    print("✅ Loaded water network")

    # Convert nodes to DataFrame
    nodes_data = []
    for node in nodes:
        nodes_data.append(
            {
                "id": str(node.id),
                "network_id": network_id,
                "name": node.name,
                "node_type": node.node_type,
                "location_lat": 39.2238,  # Selargius coordinates
                "location_lon": 9.1422,
                "installation_date": None,
                "is_active": True,
                "metadata": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

    nodes_df = pd.DataFrame(nodes_data)
    print(f"\nLoading {len(nodes_df)} monitoring nodes...")
    service.load_dataframe(
        nodes_df, "monitoring_nodes", write_disposition="WRITE_TRUNCATE"
    )
    print("✅ Loaded monitoring nodes")

    # Convert readings to DataFrame (in batches for large datasets)
    batch_size = 10000
    total_loaded = 0

    for i in range(0, len(readings), batch_size):
        batch_readings = readings[i : i + batch_size]
        readings_data = []

        for reading in batch_readings:
            readings_data.append(
                {
                    "id": str(reading.id),
                    "node_id": str(reading.node_id),
                    "timestamp": reading.timestamp,
                    "temperature": (
                        reading.temperature.value if reading.temperature else None
                    ),
                    "flow_rate": reading.flow_rate.value if reading.flow_rate else None,
                    "pressure": reading.pressure.value if reading.pressure else None,
                    "volume": reading.volume.value if reading.volume else None,
                    "is_anomalous": reading.is_anomalous(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )

        readings_df = pd.DataFrame(readings_data)

        # First batch truncates, rest append
        disposition = "WRITE_TRUNCATE" if i == 0 else "WRITE_APPEND"

        print(f"\nLoading batch {i//batch_size + 1} ({len(readings_df)} readings)...")
        service.load_dataframe(
            readings_df, "sensor_readings", write_disposition=disposition
        )
        total_loaded += len(readings_df)
        print(f"✅ Loaded {total_loaded}/{len(readings)} readings")

    print("\n✅ Data ingestion complete!")

    # Get table statistics
    stats = service.get_table_statistics("sensor_readings", days_back=365)
    print("\nTable statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def main():
    """Main function."""
    print("=== BigQuery Data Ingestion Pipeline ===")

    # Initialize BigQuery configuration
    config = BigQueryConfig(
        project_id=os.getenv("BIGQUERY_PROJECT_ID"),
        dataset_id=os.getenv("BIGQUERY_DATASET_ID"),
        location="EU",
    )

    # Initialize service
    service = BigQueryService(config)

    # Ensure dataset exists
    print(f"\nEnsuring dataset '{config.dataset_id}' exists...")
    service.ensure_dataset_exists()
    print("✅ Dataset ready")

    # Create tables
    create_tables(service)

    # Create monitoring views
    print("\nCreating monitoring views...")
    service.create_monitoring_views()
    print("✅ Created monitoring views")

    # Ingest data
    csv_path = (
        project_root
        / "RAWDATA"
        / "REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv"
    )

    if csv_path.exists():
        ingest_selargius_data(service, str(csv_path))
    else:
        print(f"\n❌ CSV file not found: {csv_path}")
        return 1

    print("\n✅ Pipeline complete! Data is now available in BigQuery.")
    print("\nYou can query the data at:")
    print(f"  Project: {config.project_id}")
    print(f"  Dataset: {config.dataset_id}")
    print("  Tables: water_networks, monitoring_nodes, sensor_readings")

    return 0


if __name__ == "__main__":
    sys.exit(main())

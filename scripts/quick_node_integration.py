#!/usr/bin/env python3
"""
Quick integration script to add new nodes to the dashboard configuration.
This script makes minimal changes to get the new nodes working quickly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Quick integration of new nodes."""
    print("=== Quick Node Integration ===\n")

    # 1. Update the static repository to include node mappings from sensor_readings_ml
    static_repo_path = (
        project_root
        / "src/infrastructure/repositories/static_monitoring_node_repository.py"
    )

    if static_repo_path.exists():
        print("1. Updating static repository to include BigQuery node mappings...")

        # Add an additional mapping at the end of the file
        additional_code = """

# Additional node mappings for new backup data nodes
BACKUP_NODE_MAPPING = {
    "215542": {"name": "Distribution 215542", "type": "distribution"},
    "215600": {"name": "Distribution 215600", "type": "distribution"},
    "273933": {"name": "Distribution 273933", "type": "distribution"},
    "281492": {"name": "Monitoring 281492", "type": "monitoring"},
    "288399": {"name": "Monitoring 288399", "type": "monitoring"},
    "288400": {"name": "Monitoring 288400", "type": "monitoring"},
}
"""

        with open(static_repo_path, "a") as f:
            f.write(additional_code)
        print("✅ Added backup node mapping")

    # 2. Create a simple configuration override file
    config_override_path = project_root / "src/config/node_overrides.py"
    config_override_path.parent.mkdir(exist_ok=True)

    override_content = '''"""
Node configuration overrides for new backup data nodes.

This file provides a simple way to extend the existing node configuration
without modifying all the existing files.
"""

# New node configurations that can be imported and used
NEW_BACKUP_NODES = {
    "215542": {
        "node_id": "215542",
        "name": "Distribution 215542",
        "type": "distribution",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml"
    },
    "215600": {
        "node_id": "215600",
        "name": "Distribution 215600",
        "type": "distribution",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml"
    },
    "273933": {
        "node_id": "273933",
        "name": "Distribution 273933",
        "type": "distribution",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml"
    },
    "281492": {
        "node_id": "281492",
        "name": "Monitoring 281492",
        "type": "monitoring",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml"
    },
    "288399": {
        "node_id": "288399",
        "name": "Monitoring 288399",
        "type": "monitoring",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml"
    },
    "288400": {
        "node_id": "288400",
        "name": "Monitoring 288400",
        "type": "monitoring",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml"
    }
}

def get_all_node_names():
    """Get all node names including new ones."""
    original_nodes = ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"]
    new_nodes = [node["name"] for node in NEW_BACKUP_NODES.values()]
    return original_nodes + new_nodes

def get_node_config(node_name):
    """Get configuration for a specific node."""
    # Check new nodes first
    for node_id, config in NEW_BACKUP_NODES.items():
        if config["name"] == node_name:
            return config
    return None
'''

    with open(config_override_path, "w") as f:
        f.write(override_content)
    print("\n2. Created node override configuration")

    # 3. Create a query adapter for the new nodes
    adapter_path = project_root / "src/infrastructure/adapters/backup_node_adapter.py"
    adapter_path.parent.mkdir(exist_ok=True)

    adapter_content = '''"""
Adapter for querying backup node data from sensor_readings_ml table.
"""

from typing import List, Optional, Dict
import pandas as pd
from datetime import datetime, timedelta
from google.cloud import bigquery


class BackupNodeAdapter:
    """Adapter for accessing backup node data from BigQuery."""

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.table_id = "sensor_readings_ml"

    def get_node_data(
        self,
        node_ids: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        metrics: List[str] = None
    ) -> pd.DataFrame:
        """Get sensor data for backup nodes."""

        if not start_time:
            start_time = datetime.now() - timedelta(days=7)
        if not end_time:
            end_time = datetime.now()

        # Default metrics
        if not metrics:
            metrics = ["flow_rate", "pressure", "temperature", "volume"]

        # Build query
        node_list = ", ".join([f"'{node_id}'" for node_id in node_ids])
        metric_cols = ", ".join(metrics)

        query = """
        SELECT
            timestamp,
            node_id,
            node_name,
            district_id,
            {metric_cols},
            data_quality_score
        FROM `{{project_id}}.{{dataset_id}}.{self.table_id}`
        WHERE node_id IN ({node_list})
            AND timestamp >= @start_time
            AND timestamp <= @end_time
            AND data_quality_score > 0.5
        ORDER BY timestamp DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
            ]
        )

        # Execute query
        df = self.client.query(query, job_config=job_config).to_dataframe()
        return df

    def get_latest_readings(self, node_ids: List[str]) -> pd.DataFrame:
        """Get latest readings for nodes."""
        return self.get_node_data(
            node_ids=node_ids,
            start_time=datetime.now() - timedelta(hours=1)
        )
'''

    with open(adapter_path, "w") as f:
        f.write(adapter_content)
    print("✅ Created backup node adapter\n")

    # Print usage instructions
    print("=== Integration Complete ===\n")
    print("New nodes are now available in the configuration.")
    print("\nTo use the new nodes in your code:")
    print("\n1. Import the configuration:")
    print(
        "   from src.config.node_overrides import NEW_BACKUP_NODES, get_all_node_names"
    )
    print("\n2. Query data using the adapter:")
    print(
        "   from src.infrastructure.adapters.backup_node_adapter import BackupNodeAdapter"
    )
    print("   adapter = BackupNodeAdapter(bigquery_client)")
    print("   data = adapter.get_node_data(['215542', '281492'])")
    print("\n3. Access nodes in BigQuery:")
    print(
        "   SELECT * FROM sensor_readings_ml WHERE node_id IN ('215542', '215600', ...)"
    )
    print("\nNext steps:")
    print("- Test the dashboard with new nodes")
    print("- Update visualizations to include node grouping")
    print("- Add data quality indicators to the UI")


if __name__ == "__main__":
    main()

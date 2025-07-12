"""
Adapter for querying backup node data from sensor_readings_ml table.
"""

from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
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
        metrics: List[str] = None,
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

        query = f"""
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
            node_ids=node_ids, start_time=datetime.now() - timedelta(hours=1)
        )

"""BigQuery service for data persistence and querying."""

from typing import Any, Dict, List, Optional

import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
from google.cloud.exceptions import NotFound
from src.infrastructure.persistence.bigquery_config import (
    BigQueryConfig,
    BigQueryConnection,
)


class BigQueryService:
    """Service for interacting with Google BigQuery."""

    def __init__(self, config: BigQueryConfig) -> None:
        self.config = config
        self.connection = BigQueryConnection(config)

    def ensure_dataset_exists(self) -> None:
        """Ensure the dataset exists, create if not."""
        dataset_id = f"{self.config.project_id}.{self.config.dataset_id}"

        try:
            self.connection.client.get_dataset(dataset_id)
        except NotFound:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = self.config.location
            dataset.description = "Water infrastructure monitoring data"
            self.connection.client.create_dataset(dataset)

    def create_table_from_schema(
        self,
        table_name: str,
        schema: List[bigquery.SchemaField],
        partition_field: Optional[str] = None,
        clustering_fields: Optional[List[str]] = None,
    ) -> bigquery.Table:
        """Create a table with the specified schema."""
        table_ref = f"{self.config.dataset_ref}.{table_name}"

        table = bigquery.Table(table_ref, schema=schema)

        # Add partitioning
        if partition_field:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY, field=partition_field
            )

        # Add clustering
        if clustering_fields:
            table.clustering_fields = clustering_fields

        # Create table
        return self.connection.client.create_table(table, exists_ok=True)

    def load_dataframe(
        self, df: pd.DataFrame, table_name: str, write_disposition: str = "WRITE_APPEND"
    ) -> bigquery.LoadJob:
        """Load a pandas DataFrame to BigQuery."""
        table_ref = f"{self.config.dataset_ref}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
        )

        job = self.connection.client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )

        return job.result()  # Wait for job to complete

    def query(
        self, query_string: str, parameters: Optional[List[ScalarQueryParameter]] = None
    ) -> pd.DataFrame:
        """Execute a query and return results as DataFrame."""
        job_config = QueryJobConfig()

        if parameters:
            job_config.query_parameters = parameters

        query_job = self.connection.client.query(query_string, job_config=job_config)

        return query_job.to_dataframe()

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table."""
        table_ref = f"{self.config.dataset_ref}.{table_name}"

        try:
            table = self.connection.client.get_table(table_ref)

            return {
                "table_id": table.table_id,
                "created": table.created,
                "modified": table.modified,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "schema": [
                    {"name": field.name, "type": field.field_type}
                    for field in table.schema
                ],
                "partitioning": {
                    "type": (
                        table.time_partitioning.type_
                        if table.time_partitioning
                        else None
                    ),
                    "field": (
                        table.time_partitioning.field
                        if table.time_partitioning
                        else None
                    ),
                },
                "clustering_fields": table.clustering_fields,
            }
        except NotFound:
            return None

    def create_monitoring_views(self) -> None:
        """Create useful monitoring views."""
        views = {
            "v_latest_readings": """
                CREATE OR REPLACE VIEW `{dataset}.v_latest_readings` AS
                SELECT 
                    node_id,
                    MAX(timestamp) as latest_reading,
                    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(timestamp), MINUTE) as minutes_since_reading
                FROM `{dataset}.sensor_readings`
                GROUP BY node_id
            """,
            "v_hourly_aggregates": """
                CREATE OR REPLACE VIEW `{dataset}.v_hourly_aggregates` AS
                SELECT 
                    node_id,
                    TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
                    AVG(flow_rate) as avg_flow_rate,
                    MAX(flow_rate) as max_flow_rate,
                    MIN(flow_rate) as min_flow_rate,
                    AVG(pressure) as avg_pressure,
                    COUNT(*) as reading_count
                FROM `{dataset}.sensor_readings`
                GROUP BY node_id, hour
            """,
            "v_daily_consumption": """
                CREATE OR REPLACE VIEW `{dataset}.v_daily_consumption` AS
                SELECT 
                    node_id,
                    DATE(timestamp) as date,
                    SUM(volume) as total_volume,
                    AVG(flow_rate) * 86400 / 1000 as estimated_volume_from_flow,
                    COUNT(*) as reading_count,
                    COUNT(DISTINCT EXTRACT(HOUR FROM timestamp)) as hours_with_data
                FROM `{dataset}.sensor_readings`
                GROUP BY node_id, date
            """,
            "v_anomaly_candidates": """
                CREATE OR REPLACE VIEW `{dataset}.v_anomaly_candidates` AS
                WITH stats AS (
                    SELECT 
                        node_id,
                        AVG(flow_rate) as mean_flow,
                        STDDEV(flow_rate) as std_flow,
                        AVG(pressure) as mean_pressure,
                        STDDEV(pressure) as std_pressure
                    FROM `{dataset}.sensor_readings`
                    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                    GROUP BY node_id
                )
                SELECT 
                    r.*,
                    ABS(r.flow_rate - s.mean_flow) / NULLIF(s.std_flow, 0) as flow_z_score,
                    ABS(r.pressure - s.mean_pressure) / NULLIF(s.std_pressure, 0) as pressure_z_score
                FROM `{dataset}.sensor_readings` r
                JOIN stats s ON r.node_id = s.node_id
                WHERE 
                    timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
                    AND (
                        ABS(r.flow_rate - s.mean_flow) > 3 * s.std_flow
                        OR ABS(r.pressure - s.mean_pressure) > 3 * s.std_pressure
                    )
            """,
        }

        dataset_ref = self.config.dataset_ref

        for view_name, view_query in views.items():
            query = view_query.format(dataset=dataset_ref)
            self.connection.client.query(query).result()

    def export_to_gcs(
        self, table_name: str, gcs_path: str, export_format: str = "CSV"
    ) -> bigquery.ExtractJob:
        """Export table data to Google Cloud Storage."""
        table_ref = f"{self.config.dataset_ref}.{table_name}"

        job_config = bigquery.ExtractJobConfig()
        job_config.destination_format = (
            bigquery.DestinationFormat.CSV
            if export_format == "CSV"
            else bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON
        )

        job = self.connection.client.extract_table(
            table_ref, gcs_path, job_config=job_config
        )

        return job.result()

    def get_table_statistics(
        self, table_name: str, days_back: int = 30
    ) -> Dict[str, Any]:
        """Get statistics about data in a table."""
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT node_id) as unique_nodes,
            MIN(timestamp) as earliest_reading,
            MAX(timestamp) as latest_reading,
            AVG(flow_rate) as avg_flow_rate,
            AVG(pressure) as avg_pressure,
            COUNTIF(flow_rate IS NULL) as null_flow_readings,
            COUNTIF(pressure IS NULL) as null_pressure_readings
        FROM `{self.config.dataset_ref}.{table_name}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days_back} DAY)
        """

        result = self.query(query)

        if not result.empty:
            return result.iloc[0].to_dict()
        return {}

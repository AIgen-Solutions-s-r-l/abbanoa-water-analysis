"""
BigQuery Ingestion Pipeline for Water Infrastructure Data
Handles authentication, table creation, data upload, and monitoring
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

# Import normalizer
from data_normalizer import WaterDataNormalizer, create_bigquery_table_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryPipeline:
    """Pipeline for ingesting water sensor data into BigQuery"""

    def __init__(self, project_id: str, dataset_id: str = "water_infrastructure"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = None
        self.normalizer = WaterDataNormalizer()

    def initialize_client(self):
        """Initialize BigQuery client (placeholder for actual implementation)"""
        logger.info(f"Initializing BigQuery client for project: {self.project_id}")

        # In production, this would initialize the actual BigQuery client:
        # from google.cloud import bigquery
        # self.client = bigquery.Client(project=self.project_id)

        # For now, we'll simulate it
        self.client = {"project": self.project_id, "dataset": self.dataset_id}

    def create_dataset_if_not_exists(self):
        """Create BigQuery dataset if it doesn't exist"""
        logger.info(f"Checking dataset: {self.dataset_id}")

        # In production:
        # dataset_id = f"{self.project_id}.{self.dataset_id}"
        # dataset = bigquery.Dataset(dataset_id)
        # dataset.location = "EU"
        # dataset = self.client.create_dataset(dataset, exists_ok=True)

        return True

    def create_or_update_table(self, table_config: Dict):
        """Create or update BigQuery table with schema"""
        table_id = table_config["table_id"]
        logger.info(f"Creating/updating table: {table_id}")

        # In production:
        # table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
        # table = bigquery.Table(table_ref, schema=table_config['schema'])
        # table.time_partitioning = bigquery.TimePartitioning(**table_config['time_partitioning'])
        # table.clustering_fields = table_config['clustering_fields']
        # table = self.client.create_table(table, exists_ok=True)

        return f"{self.dataset_id}.{table_id}"

    def process_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict, Dict]:
        """Process a single CSV file through the normalization pipeline"""
        logger.info(f"Processing file: {file_path}")

        # Normalize data
        normalized_df, metadata = self.normalizer.normalize_data(file_path)

        # Generate schema and config
        bq_schema = self.normalizer.generate_bigquery_schema(normalized_df, metadata)
        table_config = create_bigquery_table_config(bq_schema, metadata)

        # Add pipeline metadata
        metadata["pipeline"] = {
            "processed_at": datetime.now().isoformat(),
            "project_id": self.project_id,
            "dataset_id": self.dataset_id,
            "table_id": table_config["table_id"],
        }

        return normalized_df, metadata, table_config

    def upload_data(
        self, df: pd.DataFrame, table_id: str, write_disposition: str = "WRITE_APPEND"
    ):
        """Upload dataframe to BigQuery"""
        logger.info(f"Uploading {len(df)} rows to {table_id}")

        # In production:
        # job_config = bigquery.LoadJobConfig(
        #     write_disposition=write_disposition,
        #     schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        # )
        # job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        # job.result()  # Wait for job to complete

        # For now, save to file
        output_file = f"bq_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Data saved to {output_file} (simulated upload)")

        return {"status": "success", "rows_uploaded": len(df)}

    def run_pipeline(self, input_files: List[str], dry_run: bool = False) -> Dict:
        """Run the complete ingestion pipeline"""
        logger.info(f"Starting pipeline for {len(input_files)} files")

        results = {
            "status": "success",
            "files_processed": 0,
            "total_rows": 0,
            "errors": [],
            "details": [],
        }

        # Initialize
        self.initialize_client()

        if not dry_run:
            self.create_dataset_if_not_exists()

        # Process each file
        for file_path in input_files:
            try:
                # Process file
                df, metadata, table_config = self.process_file(file_path)

                if not dry_run:
                    # Create table
                    table_id = self.create_or_update_table(table_config)

                    # Upload data
                    upload_result = self.upload_data(df, table_id)

                    results["files_processed"] += 1
                    results["total_rows"] += len(df)
                    results["details"].append(
                        {
                            "file": file_path,
                            "rows": len(df),
                            "table": table_id,
                            "quality_score": metadata["validation"]["quality_score"],
                        }
                    )
                else:
                    # Dry run - just validate
                    results["details"].append(
                        {
                            "file": file_path,
                            "rows": len(df),
                            "table": f"{self.dataset_id}.{table_config['table_id']}",
                            "quality_score": metadata["validation"]["quality_score"],
                            "dry_run": True,
                        }
                    )

            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                results["errors"].append({"file": file_path, "error": str(e)})
                results["status"] = (
                    "partial_success" if results["files_processed"] > 0 else "failed"
                )

        return results


def generate_bq_commands(
    project_id: str, dataset_id: str, schema_file: str, data_file: str
) -> List[str]:
    """Generate BigQuery CLI commands for manual execution"""

    commands = [
        "# Create dataset",
        f"bq mk --dataset --location=EU {project_id}:{dataset_id}",
        "",
        "# Create table with schema",
        "bq mk --table \\",
        f"  --schema={schema_file} \\",
        "  --time_partitioning_field=timestamp \\",
        "  --time_partitioning_type=DAY \\",
        "  --clustering_fields=_source_file,timestamp \\",
        f"  {project_id}:{dataset_id}.sensor_data",
        "",
        "# Load data",
        "bq load \\",
        "  --source_format=CSV \\",
        "  --skip_leading_rows=1 \\",
        "  --allow_quoted_newlines \\",
        "  --max_bad_records=10 \\",
        f"  {project_id}:{dataset_id}.sensor_data \\",
        f"  {data_file}",
        "",
        "# Query example",
        "bq query --use_legacy_sql=false \\",
        "'SELECT ",
        "  DATE(timestamp) as date,",
        "  AVG(metric_3) as avg_flow_rate,",
        "  MAX(metric_3) as max_flow_rate,",
        "  MIN(metric_3) as min_flow_rate",
        f"FROM `{project_id}.{dataset_id}.sensor_data`",
        "WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)",
        "GROUP BY date",
        "ORDER BY date DESC'",
    ]

    return commands


def create_monitoring_queries() -> Dict[str, str]:
    """Create useful monitoring queries for the data"""

    queries = {
        "data_freshness": """
            -- Check data freshness
            SELECT
              MAX(timestamp) as latest_data,
              TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(timestamp), MINUTE) as minutes_behind
            FROM `{project_id}.{dataset_id}.{table_id}`
        """,
        "hourly_patterns": """
            -- Hourly consumption patterns
            SELECT
              EXTRACT(HOUR FROM timestamp) as hour,
              AVG(metric_3) as avg_flow_rate,
              STDDEV(metric_3) as stddev_flow_rate,
              COUNT(*) as measurements
            FROM `{project_id}.{dataset_id}.{table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY hour
            ORDER BY hour
        """,
        "anomaly_detection": """
            -- Simple anomaly detection (values outside 3 standard deviations)
            WITH stats AS (
              SELECT
                AVG(metric_3) as mean_value,
                STDDEV(metric_3) as std_value
              FROM `{project_id}.{dataset_id}.{table_id}`
              WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            )
            SELECT
              timestamp,
              metric_3 as flow_rate,
              ABS(metric_3 - stats.mean_value) / stats.std_value as z_score,
              CASE
                WHEN ABS(metric_3 - stats.mean_value) > 3 * stats.std_value THEN 'ANOMALY'
                ELSE 'NORMAL'
              END as status
            FROM `{project_id}.{dataset_id}.{table_id}`, stats
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
              AND ABS(metric_3 - stats.mean_value) > 3 * stats.std_value
            ORDER BY timestamp DESC
        """,
        "daily_summary": """
            -- Daily summary statistics
            SELECT
              DATE(timestamp) as date,
              COUNT(*) as measurements,
              AVG(metric_3) as avg_flow_rate,
              MAX(metric_3) as max_flow_rate,
              MIN(metric_3) as min_flow_rate,
              STDDEV(metric_3) as stddev_flow_rate,
              APPROX_QUANTILES(metric_3, 100)[OFFSET(50)] as median_flow_rate,
              APPROX_QUANTILES(metric_3, 100)[OFFSET(95)] as p95_flow_rate
            FROM `{project_id}.{dataset_id}.{table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY date
            ORDER BY date DESC
        """,
    }

    return queries


# Example usage and documentation
if __name__ == "__main__":
    # Configuration
    PROJECT_ID = "your-gcp-project-id"  # Replace with actual project ID
    DATASET_ID = "water_infrastructure"

    # Initialize pipeline
    pipeline = BigQueryPipeline(PROJECT_ID, DATASET_ID)

    # Find CSV files
    csv_files = [
        "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv"
    ]

    # Run pipeline in dry-run mode
    results = pipeline.run_pipeline(csv_files, dry_run=True)

    print("\n=== PIPELINE RESULTS ===")
    print(json.dumps(results, indent=2))

    # Generate BigQuery commands
    commands = generate_bq_commands(
        PROJECT_ID, DATASET_ID, "bigquery_schema.json", "normalized_data.csv"
    )

    # Save commands
    with open("bigquery_commands.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("# BigQuery ingestion commands\n")
        f.write("# Update PROJECT_ID before running!\n\n")
        f.write('PROJECT_ID="your-gcp-project-id"\n\n')
        for cmd in commands:
            f.write(cmd + "\n")

    # Save monitoring queries
    queries = create_monitoring_queries()
    with open("bigquery_monitoring_queries.sql", "w") as f:
        f.write("-- BigQuery Monitoring Queries for Water Infrastructure Data\n\n")
        for name, query in queries.items():
            f.write(f"-- {name.replace('_', ' ').title()}\n")
            f.write(query.strip() + "\n\n")

    print("\n✓ Pipeline configuration complete")
    print("✓ BigQuery commands saved to: bigquery_commands.sh")
    print("✓ Monitoring queries saved to: bigquery_monitoring_queries.sql")
    print("\nNext steps:")
    print("1. Update PROJECT_ID in the files")
    print("2. Authenticate with: gcloud auth login")
    print("3. Run: bash bigquery_commands.sh")

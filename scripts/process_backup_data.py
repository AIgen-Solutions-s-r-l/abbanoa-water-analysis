#!/usr/bin/env python3
"""
Process and integrate backup sensor data into BigQuery for ML/AI analysis.

This script handles multiple CSV formats from the backup directory and normalizes
them for consistent storage and ML/AI processing.
"""

import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
BACKUP_DIR = project_root / "RAWDATA" / "NEW_DATA" / "BACKUP"
PROJECT_ID = os.environ.get("BIGQUERY_PROJECT_ID", "abbanoa-464816")
DATASET_ID = os.environ.get("BIGQUERY_DATASET_ID", "water_infrastructure")
ML_DATASET_ID = os.environ.get("ML_DATASET_ID", "ml_models")

# Node ID mapping (from filename to district/location)
NODE_MAPPING = {
    "215542": {"district": "Selargius", "name": "Node 215542", "type": "distribution"},
    "215600": {"district": "Selargius", "name": "Node 215600", "type": "distribution"},
    "273933": {"district": "Selargius", "name": "Node 273933", "type": "distribution"},
    "281492": {"district": "Selargius", "name": "Node 281492", "type": "monitoring"},
    "288399": {"district": "Selargius", "name": "Node 288399", "type": "monitoring"},
    "288400": {"district": "Selargius", "name": "Node 288400", "type": "monitoring"},
}


class BackupDataProcessor:
    """Process backup sensor data files."""

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.processed_files = set()
        self.error_files = []

    def process_backup_directory(self, backup_dir: Path) -> Dict[str, pd.DataFrame]:
        """Process all files in a backup directory."""
        results = {"sensor_readings": [], "process_data": [], "logger_format": []}

        for file_path in backup_dir.glob("*.csv"):
            try:
                df, file_type = self.process_file(file_path)
                if df is not None and not df.empty:
                    results[file_type].append(df)
                    self.processed_files.add(str(file_path))
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                self.error_files.append((str(file_path), str(e)))

        # Combine dataframes
        combined = {}
        for key, dfs in results.items():
            if dfs:
                combined[key] = pd.concat(dfs, ignore_index=True)

        return combined

    def process_file(self, file_path: Path) -> Tuple[Optional[pd.DataFrame], str]:
        """Process a single CSV file based on its format."""
        filename = file_path.name

        # Extract node ID from filename
        node_id_match = re.match(r"^(\d+)_", filename)
        if not node_id_match:
            logger.warning(f"Could not extract node ID from {filename}")
            return None, "unknown"

        node_id = node_id_match.group(1)

        # Determine file type
        if "DATA_LOG" in filename:
            return self.process_data_log(file_path, node_id), "sensor_readings"
        elif "PROCESS_DATA" in filename:
            return self.process_process_data(file_path, node_id), "process_data"
        elif "D_LOGGER_FORMAT" in filename:
            return self.process_logger_format(file_path, node_id), "logger_format"
        else:
            logger.warning(f"Unknown file format: {filename}")
            return None, "unknown"

    def process_data_log(self, file_path: Path, node_id: str) -> Optional[pd.DataFrame]:
        """Process DATA_LOG format files (standard sensor readings)."""
        try:
            # Read with semicolon separator, try different encodings
            encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(
                        file_path, sep=";", encoding=encoding, low_memory=False
                    )
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise Exception("Unable to decode file with any encoding")

            if df.empty:
                return None

            # Extract date from filename for validation
            date_match = re.search(r"(\d{4})_(\d{2})_(\d{2})", file_path.name)
            if date_match:
                file_date = (
                    f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                )
            else:
                file_date = None

            # Process timestamp columns
            if 1 in df.columns and 2 in df.columns:  # Columns by index
                df["timestamp"] = pd.to_datetime(
                    df[1].astype(str) + " " + df[2].astype(str),
                    format="%Y/%m/%d %H:%M:%S",
                    errors="coerce",
                )
            else:
                logger.warning(f"Timestamp columns not found in {file_path}")
                return None

            # Filter out invalid timestamps
            df = df[df["timestamp"].notna()]
            if df.empty:
                return None

            # Add node information
            df["node_id"] = node_id
            df["district_id"] = NODE_MAPPING.get(node_id, {}).get("district", "Unknown")
            df["node_name"] = NODE_MAPPING.get(node_id, {}).get(
                "name", f"Node {node_id}"
            )
            df["node_type"] = NODE_MAPPING.get(node_id, {}).get("type", "unknown")

            # Extract numeric columns (skip first 3 columns: index, date, time)
            numeric_cols = []
            for col in df.columns[3:]:
                if col not in [
                    "timestamp",
                    "node_id",
                    "district_id",
                    "node_name",
                    "node_type",
                ]:
                    # Try to convert to numeric
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                    if df[col].notna().any():
                        numeric_cols.append(col)

            # Map columns to standard metrics based on position and patterns
            metric_mapping = self.identify_metrics(df, numeric_cols)

            # Create normalized dataframe
            normalized_rows = []
            for idx, row in df.iterrows():
                base_row = {
                    "timestamp": row["timestamp"],
                    "node_id": node_id,
                    "district_id": row["district_id"],
                    "node_name": row["node_name"],
                    "node_type": row["node_type"],
                    "file_date": file_date,
                    "source_file": file_path.name,
                }

                # Add metrics
                for metric, col in metric_mapping.items():
                    if col and not pd.isna(row[col]):
                        base_row[metric] = float(row[col])
                    else:
                        base_row[metric] = None

                normalized_rows.append(base_row)

            return pd.DataFrame(normalized_rows)

        except Exception as e:
            logger.error(f"Error processing DATA_LOG file {file_path}: {e}")
            return None

    def process_process_data(
        self, file_path: Path, node_id: str
    ) -> Optional[pd.DataFrame]:
        """Process PROCESS_DATA format files."""
        try:
            # First line contains headers with units
            with open(file_path, "r", encoding="utf-8") as f:
                header_line = f.readline().strip()

            # Parse headers
            headers = []
            parts = header_line.split(";")

            for i, part in enumerate(parts):
                if "=" in part:
                    header = part.split("=")[0]
                    headers.append(header)
                elif part.strip():
                    headers.append(f"col_{i}")

            # Read data with different encodings
            encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(
                        file_path, sep=";", skiprows=1, names=headers, encoding=encoding
                    )
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise Exception("Unable to decode file with any encoding")

            if df.empty:
                return None

            # Process timestamp
            if "DATE" in df.columns and "TIME" in df.columns:
                df["timestamp"] = pd.to_datetime(
                    df["DATE"].astype(str) + " " + df["TIME"].astype(str),
                    format="%Y/%m/%d %H:%M:%S",
                    errors="coerce",
                )
            else:
                return None

            # Add node information
            df["node_id"] = node_id
            df["district_id"] = NODE_MAPPING.get(node_id, {}).get("district", "Unknown")
            df["node_name"] = NODE_MAPPING.get(node_id, {}).get(
                "name", f"Node {node_id}"
            )
            df["node_type"] = NODE_MAPPING.get(node_id, {}).get("type", "unknown")
            df["data_format"] = "PROCESS_DATA"

            # Map known columns
            column_mapping = {
                "TOT_T": "total_volume",
                "FLOW_R": "flow_rate",
                "A_IN1": "pressure_1",
                "A_IN2": "pressure_2",
                "CPU_T": "temperature",
            }

            # Create normalized dataframe
            result_df = pd.DataFrame()
            result_df["timestamp"] = df["timestamp"]
            result_df["node_id"] = df["node_id"]
            result_df["district_id"] = df["district_id"]
            result_df["node_name"] = df["node_name"]
            result_df["node_type"] = df["node_type"]
            result_df["source_file"] = file_path.name

            # Add mapped metrics
            for original, mapped in column_mapping.items():
                if original in df.columns:
                    result_df[mapped] = pd.to_numeric(df[original], errors="coerce")

            # Calculate average pressure if both available
            if "pressure_1" in result_df.columns and "pressure_2" in result_df.columns:
                result_df["pressure"] = result_df[["pressure_1", "pressure_2"]].mean(
                    axis=1
                )

            return result_df[result_df["timestamp"].notna()]

        except Exception as e:
            logger.error(f"Error processing PROCESS_DATA file {file_path}: {e}")
            return None

    def process_logger_format(
        self, file_path: Path, node_id: str
    ) -> Optional[pd.DataFrame]:
        """Process D_LOGGER_FORMAT files (diagnostic data)."""
        # These files contain diagnostic/configuration data
        # For now, we'll skip these as they're not primary sensor readings
        logger.debug(f"Skipping logger format file: {file_path}")
        return None

    def identify_metrics(
        self, df: pd.DataFrame, numeric_cols: List[str]
    ) -> Dict[str, str]:
        """Identify metrics from column patterns and values."""
        metric_mapping = {
            "flow_rate": None,
            "pressure": None,
            "temperature": None,
            "volume": None,
        }

        # Simple heuristic based on column position and value ranges
        for i, col in enumerate(numeric_cols):
            values = df[col].dropna()
            if len(values) == 0:
                continue

            mean_val = values.mean()
            max_val = values.max()

            # Temperature: typically 20-40 range
            if 15 <= mean_val <= 45 and max_val < 50:
                if not metric_mapping["temperature"]:
                    metric_mapping["temperature"] = col
            # Pressure: typically 0-10 bar range
            elif 0 <= mean_val <= 15 and max_val < 20:
                if not metric_mapping["pressure"]:
                    metric_mapping["pressure"] = col
            # Flow rate: variable but typically < 1000
            elif mean_val < 1000 and i < len(numeric_cols) // 2:
                if not metric_mapping["flow_rate"]:
                    metric_mapping["flow_rate"] = col
            # Volume: cumulative, typically large numbers
            elif mean_val > 100:
                if not metric_mapping["volume"]:
                    metric_mapping["volume"] = col

        return metric_mapping


def create_ml_ready_tables(client: bigquery.Client):
    """Create tables optimized for ML/AI processing."""
    dataset_ref = client.dataset(DATASET_ID)

    # Create sensor_readings_ml table
    ml_table_schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("node_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("district_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("node_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("node_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("flow_rate", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("pressure", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("temperature", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("volume", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("pressure_1", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("pressure_2", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("data_quality_score", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("is_interpolated", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("source_file", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    table_ref = dataset_ref.table("sensor_readings_ml")

    try:
        client.get_table(table_ref)
        logger.info("Table sensor_readings_ml already exists")
    except NotFound:
        table = bigquery.Table(table_ref, schema=ml_table_schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY, field="timestamp"
        )
        table.clustering_fields = ["district_id", "node_id", "timestamp"]

        table = client.create_table(table)
        logger.info(
            f"Created table {table.project}.{table.dataset_id}.{table.table_id}"
        )


def calculate_data_quality_score(row: pd.Series) -> float:
    """Calculate data quality score for a reading."""
    score = 1.0

    # Check for missing values
    metrics = ["flow_rate", "pressure", "temperature", "volume"]
    available_metrics = sum(1 for m in metrics if m in row and pd.notna(row[m]))
    score *= available_metrics / len(metrics)

    # Check for outliers (simple z-score based)
    # This is simplified - in production, use historical data
    if "flow_rate" in row and pd.notna(row["flow_rate"]):
        if row["flow_rate"] < 0 or row["flow_rate"] > 1000:
            score *= 0.5

    if "pressure" in row and pd.notna(row["pressure"]):
        if row["pressure"] < 0 or row["pressure"] > 20:
            score *= 0.5

    if "temperature" in row and pd.notna(row["temperature"]):
        if row["temperature"] < 0 or row["temperature"] > 50:
            score *= 0.5

    return round(score, 3)


def load_to_bigquery(client: bigquery.Client, df: pd.DataFrame, table_name: str):
    """Load DataFrame to BigQuery table."""
    if df.empty:
        logger.warning(f"Empty dataframe for {table_name}, skipping")
        return

    # Add ingestion timestamp
    df["ingestion_timestamp"] = datetime.now(timezone.utc)

    # Calculate data quality scores
    if "sensor_readings" in table_name:
        df["data_quality_score"] = df.apply(calculate_data_quality_score, axis=1)
        df["is_interpolated"] = False

    # Configure load job
    job_config = bigquery.LoadJobConfig(
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        time_partitioning=bigquery.TimePartitioning(field="timestamp"),
    )

    # Load data
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for job to complete

    logger.info(f"Loaded {len(df)} rows to {table_id}")


def create_ml_views(client: bigquery.Client):
    """Create views for ML/AI processing."""

    # Create normalized view for ML training
    view_query = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_sensor_readings_normalized` AS
    WITH latest_readings AS (
        SELECT 
            timestamp,
            node_id,
            district_id,
            node_name,
            node_type,
            flow_rate,
            pressure,
            temperature,
            volume,
            data_quality_score,
            ROW_NUMBER() OVER (PARTITION BY node_id, DATE(timestamp) ORDER BY timestamp DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
        WHERE data_quality_score > 0.5
            AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 730 DAY)
    )
    SELECT 
        timestamp,
        node_id,
        district_id,
        node_name,
        node_type,
        flow_rate,
        pressure,
        temperature,
        volume,
        data_quality_score
    FROM latest_readings
    WHERE rn = 1
    """

    client.query(view_query).result()
    logger.info("Created v_sensor_readings_normalized view")

    # Create aggregated daily view for ML
    daily_view_query = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.v_daily_metrics_ml` AS
    SELECT 
        DATE(timestamp) as date,
        node_id,
        district_id,
        AVG(flow_rate) as avg_flow_rate,
        MIN(flow_rate) as min_flow_rate,
        MAX(flow_rate) as max_flow_rate,
        STDDEV(flow_rate) as stddev_flow_rate,
        AVG(pressure) as avg_pressure,
        MIN(pressure) as min_pressure,
        MAX(pressure) as max_pressure,
        AVG(temperature) as avg_temperature,
        MAX(volume) - MIN(volume) as daily_volume,
        COUNT(*) as reading_count,
        AVG(data_quality_score) as avg_quality_score
    FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
    WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 730 DAY)
    GROUP BY date, node_id, district_id
    """

    client.query(daily_view_query).result()
    logger.info("Created v_daily_metrics_ml view")


def main():
    """Main processing function."""
    logger.info("Starting backup data processing")

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Create ML-ready tables
    logger.info("Creating ML-ready tables...")
    create_ml_ready_tables(client)

    # Initialize processor
    processor = BackupDataProcessor(client)

    # Get all backup directories
    backup_dirs = sorted([d for d in BACKUP_DIR.iterdir() if d.is_dir()])
    logger.info(f"Found {len(backup_dirs)} backup directories")

    # Process directories in batches
    batch_size = 10
    all_sensor_readings = []

    with tqdm(total=len(backup_dirs), desc="Processing backup directories") as pbar:
        for i in range(0, len(backup_dirs), batch_size):
            batch_dirs = backup_dirs[i : i + batch_size]

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(processor.process_backup_directory, d): d
                    for d in batch_dirs
                }

                for future in as_completed(futures):
                    dir_path = futures[future]
                    try:
                        results = future.result()
                        if (
                            "sensor_readings" in results
                            and not results["sensor_readings"].empty
                        ):
                            all_sensor_readings.append(results["sensor_readings"])
                    except Exception as e:
                        logger.error(f"Error processing {dir_path}: {e}")
                    finally:
                        pbar.update(1)

    # Combine all sensor readings
    if all_sensor_readings:
        logger.info("Combining all sensor readings...")
        combined_df = pd.concat(all_sensor_readings, ignore_index=True)

        # Remove duplicates based on timestamp and node_id
        combined_df = combined_df.drop_duplicates(subset=["timestamp", "node_id"])

        logger.info(f"Total unique readings: {len(combined_df)}")

        # Load to BigQuery in chunks
        chunk_size = 50000
        for i in range(0, len(combined_df), chunk_size):
            chunk = combined_df.iloc[i : i + chunk_size]
            load_to_bigquery(client, chunk, "sensor_readings_ml")

    # Create ML views
    logger.info("Creating ML views...")
    create_ml_views(client)

    # Print summary
    logger.info("\n=== Processing Summary ===")
    logger.info(f"Processed files: {len(processor.processed_files)}")
    logger.info(f"Error files: {len(processor.error_files)}")

    if processor.error_files:
        logger.error("\nFiles with errors:")
        for file_path, error in processor.error_files[:10]:  # Show first 10
            logger.error(f"  {file_path}: {error}")

    logger.info("\n✅ Backup data processing complete!")
    logger.info(f"Data is available in: {PROJECT_ID}.{DATASET_ID}.sensor_readings_ml")


if __name__ == "__main__":
    main()

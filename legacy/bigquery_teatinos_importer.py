"""
BigQuery Importer for Teatinos Hidroconta Data
Creates a separate dataset for the Teatinos site infrastructure data
"""

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import json
import os
from datetime import datetime


class TeatinoBigQueryImporter:
    """BigQuery importer for Teatinos Hidroconta sensor data"""

    def __init__(self, project_id="abbanoa-464816"):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_id = "teatinos_infrastructure"  # Separate dataset for Teatinos
        self.table_id = "sensor_data"

    def create_dataset(self):
        """Create the teatinos_infrastructure dataset"""
        dataset_ref = self.client.dataset(self.dataset_id)

        try:
            self.client.get_dataset(dataset_ref)
            print(f"✅ Dataset {self.dataset_id} already exists")
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "europe-west1"  # Use EU region for GDPR compliance
            dataset.description = """
            Infrastructure monitoring data from Teatinos water treatment facility.
            Contains sensor readings from Hidroconta system including:
            - Daily water consumption measurements
            - Hourly consumption tracking  
            - Flow rate monitoring
            - Data from PCR-4 and PCR-5 units
            
            Data source: Hidroconta sensor network
            Site: Teatinos, Sardinia
            Date range: 2023-2025
            """

            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"✅ Created dataset {self.project_id}.{self.dataset_id}")

    def create_table_with_schema(self, schema_file):
        """Create the sensor_data table with the provided schema"""

        # Load schema
        with open(schema_file, "r") as f:
            schema_json = json.load(f)

        # Convert to BigQuery schema
        schema = []
        for field in schema_json:
            field_mode = "REQUIRED" if field.get("mode") == "REQUIRED" else "NULLABLE"

            schema.append(
                bigquery.SchemaField(
                    name=field["name"],
                    field_type=field["type"],
                    mode=field_mode,
                    description=field.get("description", ""),
                )
            )

        # Create table reference
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)

        try:
            table = self.client.get_table(table_ref)
            print(f"✅ Table {self.dataset_id}.{self.table_id} already exists")
            return table
        except NotFound:
            table = bigquery.Table(table_ref, schema=schema)
            table.description = """
            Teatinos infrastructure sensor data from Hidroconta system.
            
            Contains time-series measurements from water treatment facility:
            - Consumption metrics (daily, hourly, flow rates)
            - PCR unit monitoring data
            - Quality and metadata tracking
            
            Data ingestion: Automated from CSV exports
            Update frequency: Batch imports as needed
            Retention: Indefinite for historical analysis
            """

            # Set table options
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY, field="datetime"
            )

            table.clustering_fields = ["_data_type", "_pcr_unit", "_sensor_type"]

            table = self.client.create_table(table, timeout=30)
            print(
                f"✅ Created table {self.project_id}.{self.dataset_id}.{self.table_id}"
            )
            return table

    def upload_data(self, csv_file, metadata_file):
        """Upload the normalized data to BigQuery"""

        print(f"📤 Starting upload from {csv_file}...")

        # Load metadata for validation
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        print(f"📊 Data summary:")
        print(f"   Records: {metadata['total_records']:,}")
        print(f"   Files: {metadata['files_processed']}")
        print(f"   Data types: {', '.join(metadata['data_types'].keys())}")
        print(
            f"   Date range: {metadata['date_range']['min_date']} to {metadata['date_range']['max_date']}"
        )

        # Configure job
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,  # Skip header
            autodetect=False,  # Use our schema
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Replace data
            max_bad_records=1000,  # Allow some parsing errors
            create_disposition=bigquery.CreateDisposition.CREATE_NEVER,  # Table should exist
        )

        # Start upload job
        with open(csv_file, "rb") as source_file:
            job = self.client.load_table_from_file(
                source_file, table_ref, job_config=job_config
            )

        print("⏳ Upload in progress...")
        job.result()  # Wait for completion

        if job.errors:
            print(f"❌ Upload errors:")
            for error in job.errors:
                print(f"   • {error}")
            return False

        # Verify upload
        table = self.client.get_table(table_ref)
        print(f"✅ Upload successful!")
        print(f"   📊 Rows in BigQuery: {table.num_rows:,}")
        print(f"   💾 Table size: {table.num_bytes / (1024*1024):.1f} MB")
        print(f"   📅 Last modified: {table.modified}")

        return True

    def run_data_quality_checks(self):
        """Run quality checks on the uploaded data"""

        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"

        checks = [
            {
                "name": "Total record count",
                "query": f"SELECT COUNT(*) as count FROM `{table_ref}`",
            },
            {
                "name": "Data type distribution",
                "query": f"""
                SELECT _data_type, COUNT(*) as count 
                FROM `{table_ref}` 
                GROUP BY _data_type 
                ORDER BY count DESC
                """,
            },
            {
                "name": "PCR unit distribution",
                "query": f"""
                SELECT _pcr_unit, _sensor_type, COUNT(*) as count
                FROM `{table_ref}`
                GROUP BY _pcr_unit, _sensor_type
                ORDER BY count DESC
                """,
            },
            {
                "name": "Date range coverage",
                "query": f"""
                SELECT 
                    MIN(datetime) as earliest_date,
                    MAX(datetime) as latest_date,
                    DATE_DIFF(DATE(MAX(datetime)), DATE(MIN(datetime)), DAY) as days_covered
                FROM `{table_ref}`
                """,
            },
            {
                "name": "Data quality metrics",
                "query": f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT _row_hash) as unique_records,
                    COUNT(*) - COUNT(DISTINCT _row_hash) as potential_duplicates,
                    COUNT(value) as non_null_values,
                    ROUND(AVG(value), 2) as avg_value,
                    ROUND(MIN(value), 2) as min_value,
                    ROUND(MAX(value), 2) as max_value
                FROM `{table_ref}`
                """,
            },
        ]

        print(f"\n🔍 Running data quality checks...")

        for check in checks:
            print(f"\n📋 {check['name']}:")

            try:
                result = self.client.query(check["query"]).to_dataframe()

                if len(result) == 1 and len(result.columns) == 1:
                    # Single value result
                    value = result.iloc[0, 0]
                    print(
                        f"   Result: {value:,}"
                        if isinstance(value, (int, float))
                        else f"   Result: {value}"
                    )
                else:
                    # Multi-row or multi-column result
                    for _, row in result.iterrows():
                        row_str = " | ".join(
                            [f"{col}: {val}" for col, val in row.items()]
                        )
                        print(f"   {row_str}")

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

        print(f"\n✅ Quality checks complete!")

    def create_sample_queries(self):
        """Create sample queries for analyzing Teatinos data"""

        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"

        queries = {
            "daily_consumption_trends.sql": f"""
-- Daily consumption trends for Teatinos site
SELECT 
    DATE(datetime) as date,
    _pcr_unit,
    _sensor_type,
    ROUND(AVG(value), 2) as avg_daily_consumption,
    ROUND(MIN(value), 2) as min_consumption,
    ROUND(MAX(value), 2) as max_consumption,
    unit
FROM `{table_ref}`
WHERE _data_type = 'consumption'
    AND datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY DATE(datetime), _pcr_unit, _sensor_type, unit
ORDER BY date DESC, _pcr_unit
""",
            "flow_rate_monitoring.sql": f"""
-- Flow rate monitoring analysis
SELECT 
    DATETIME_TRUNC(datetime, HOUR) as hour,
    _pcr_unit,
    ROUND(AVG(value), 3) as avg_flow_rate,
    ROUND(STDDEV(value), 3) as flow_variance,
    COUNT(*) as measurements
FROM `{table_ref}`
WHERE _data_type = 'consumption-flow'
    AND datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 7 DAY)
GROUP BY hour, _pcr_unit
ORDER BY hour DESC
""",
            "consumption_comparison.sql": f"""
-- Compare consumption between PCR units
WITH daily_consumption AS (
    SELECT 
        DATE(datetime) as date,
        _pcr_unit,
        SUM(value) as total_consumption
    FROM `{table_ref}`
    WHERE _data_type = 'consumption'
        AND datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    GROUP BY DATE(datetime), _pcr_unit
)
SELECT 
    date,
    SUM(CASE WHEN _pcr_unit LIKE '%PCR-4%' THEN total_consumption END) as pcr4_consumption,
    SUM(CASE WHEN _pcr_unit LIKE '%PCR-5%' THEN total_consumption END) as pcr5_consumption,
    SUM(total_consumption) as total_site_consumption
FROM daily_consumption
GROUP BY date
ORDER BY date DESC
""",
            "anomaly_detection.sql": f"""
-- Detect consumption anomalies using statistical thresholds
WITH consumption_stats AS (
    SELECT 
        _pcr_unit,
        _data_type,
        AVG(value) as mean_value,
        STDDEV(value) as stddev_value
    FROM `{table_ref}`
    WHERE _data_type IN ('consumption', 'consumption-flow')
        AND datetime >= DATE_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
    GROUP BY _pcr_unit, _data_type
),
anomalies AS (
    SELECT 
        r.datetime,
        r._pcr_unit,
        r._data_type,
        r.value,
        s.mean_value,
        s.stddev_value,
        ABS(r.value - s.mean_value) / s.stddev_value as z_score
    FROM `{table_ref}` r
    JOIN consumption_stats s 
        ON r._pcr_unit = s._pcr_unit 
        AND r._data_type = s._data_type
    WHERE r.datetime >= DATE_SUB(CURRENT_DATETIME(), INTERVAL 7 DAY)
        AND s.stddev_value > 0
)
SELECT *
FROM anomalies
WHERE z_score > 2.5  -- Values more than 2.5 standard deviations from mean
ORDER BY z_score DESC, datetime DESC
""",
        }

        print(f"\n📝 Creating sample analysis queries...")

        for filename, query in queries.items():
            with open(filename, "w") as f:
                f.write(query.strip())
            print(f"   💾 {filename}")

        print(f"✅ Sample queries created!")


def main():
    """Main function to set up BigQuery for Teatinos data"""

    # File paths
    csv_file = "teatinos_hidroconta_normalized.csv"
    metadata_file = "teatinos_hidroconta_metadata.json"
    schema_file = "teatinos_hidroconta_schema.json"

    # Verify files exist
    for file_path in [csv_file, metadata_file, schema_file]:
        if not os.path.exists(file_path):
            print(f"❌ Required file not found: {file_path}")
            return

    try:
        # Initialize importer
        importer = TeatinoBigQueryImporter()

        print("🚀 Setting up BigQuery for Teatinos infrastructure data...")

        # Create dataset and table
        importer.create_dataset()
        importer.create_table_with_schema(schema_file)

        # Upload data
        success = importer.upload_data(csv_file, metadata_file)

        if success:
            # Run quality checks
            importer.run_data_quality_checks()

            # Create sample queries
            importer.create_sample_queries()

            print(f"\n🎉 Teatinos data successfully imported to BigQuery!")
            print(f"   🗄️ Dataset: teatinos_infrastructure")
            print(f"   📊 Table: sensor_data")
            print(
                f"   🔗 Console: https://console.cloud.google.com/bigquery?project=abbanoa-464816"
            )

        else:
            print(f"❌ Upload failed")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

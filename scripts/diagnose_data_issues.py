#!/usr/bin/env python3
"""
Comprehensive diagnostics script to identify and fix dashboard data issues.
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
import pandas as pd
import traceback

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from google.cloud import bigquery
from google.cloud.exceptions import NotFound, Forbidden
from src.infrastructure.persistence.bigquery_config import (
    BigQueryConfig,
    BigQueryConnection,
)
from src.infrastructure.repositories.sensor_data_repository import SensorDataRepository
from src.infrastructure.di_container import Container


class DataDiagnostics:
    """Comprehensive data diagnostics for the dashboard."""

    def __init__(self):
        self.project_id = "abbanoa-464816"
        self.dataset_id = "water_infrastructure"
        self.location = "EU"
        self.client = None
        self.diagnostics_results = {}

    def run_full_diagnostics(self):
        """Run complete diagnostic suite."""
        print("🔍 Starting comprehensive data diagnostics...")
        print("=" * 60)

        try:
            # Test 1: BigQuery Authentication
            self.test_bigquery_auth()

            # Test 2: Dataset and Table Access
            self.test_dataset_access()

            # Test 3: Data Availability
            self.test_data_availability()

            # Test 4: Node Mappings
            self.test_node_mappings()

            # Test 5: Repository Configuration
            self.test_repository_config()

            # Test 6: Dashboard Dependencies
            self.test_dashboard_dependencies()

            # Print summary
            self.print_summary()

        except Exception as e:
            print(f"❌ Critical error in diagnostics: {e}")
            traceback.print_exc()

    def test_bigquery_auth(self):
        """Test BigQuery authentication and connection."""
        print("\n1. Testing BigQuery Authentication...")

        try:
            # Test different ways to authenticate
            self.client = bigquery.Client(
                project=self.project_id, location=self.location
            )

            # Test basic query
            query = "SELECT 1 as test"
            query_job = self.client.query(query)
            results = list(query_job.result())

            if results and results[0].test == 1:
                print("✅ BigQuery authentication successful")
                self.diagnostics_results["bigquery_auth"] = "SUCCESS"
            else:
                print("❌ BigQuery query failed")
                self.diagnostics_results["bigquery_auth"] = "FAILED"

        except Exception as e:
            print(f"❌ BigQuery authentication failed: {e}")
            self.diagnostics_results["bigquery_auth"] = f"FAILED: {e}"

    def test_dataset_access(self):
        """Test dataset and table access."""
        print("\n2. Testing Dataset Access...")

        if not self.client:
            print("❌ No BigQuery client - skipping dataset tests")
            return

        try:
            # Test dataset access
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            dataset = self.client.get_dataset(dataset_ref)
            print(f"✅ Dataset '{self.dataset_id}' accessible")

            # List all tables
            tables = list(self.client.list_tables(dataset))
            print(f"📊 Found {len(tables)} tables:")

            expected_tables = [
                "sensor_data",
                "v_sensor_readings_normalized",
                "sensor_readings_ml",
                "monitoring_nodes",
            ]

            existing_tables = [table.table_id for table in tables]
            for table_name in existing_tables:
                print(f"  - {table_name}")

            # Check for expected tables
            missing_tables = [t for t in expected_tables if t not in existing_tables]
            if missing_tables:
                print(f"⚠️  Missing expected tables: {missing_tables}")

            self.diagnostics_results["dataset_access"] = "SUCCESS"
            self.diagnostics_results["tables_found"] = existing_tables

        except NotFound:
            print(f"❌ Dataset '{self.dataset_id}' not found")
            self.diagnostics_results["dataset_access"] = "DATASET_NOT_FOUND"
        except Forbidden:
            print(f"❌ Access denied to dataset '{self.dataset_id}'")
            self.diagnostics_results["dataset_access"] = "ACCESS_DENIED"
        except Exception as e:
            print(f"❌ Dataset access error: {e}")
            self.diagnostics_results["dataset_access"] = f"ERROR: {e}"

    def test_data_availability(self):
        """Test data availability in key tables."""
        print("\n3. Testing Data Availability...")

        if not self.client:
            print("❌ No BigQuery client - skipping data tests")
            return

        tables_to_check = [
            "sensor_data",
            "v_sensor_readings_normalized",
            "sensor_readings_ml",
        ]

        data_results = {}

        for table_name in tables_to_check:
            try:
                # Check if table exists and has data
                query = """
                SELECT
                    COUNT(*) as total_rows,
                    MIN(timestamp) as earliest_data,
                    MAX(timestamp) as latest_data,
                    COUNT(DISTINCT node_id) as unique_nodes
                FROM `{self.project_id}.{self.dataset_id}.{table_name}`
                """

                query_job = self.client.query(query)
                results = list(query_job.result())

                if results:
                    row = results[0]
                    data_results[table_name] = {
                        "total_rows": row.total_rows,
                        "earliest_data": row.earliest_data,
                        "latest_data": row.latest_data,
                        "unique_nodes": row.unique_nodes,
                    }

                    print(f"✅ Table '{table_name}':")
                    print(f"    - Total rows: {row.total_rows:,}")
                    print(f"    - Date range: {row.earliest_data} to {row.latest_data}")
                    print(f"    - Unique nodes: {row.unique_nodes}")

                    if row.total_rows == 0:
                        print(f"⚠️  Table '{table_name}' is empty!")

            except Exception as e:
                print(f"❌ Error checking table '{table_name}': {e}")
                data_results[table_name] = f"ERROR: {e}"

        self.diagnostics_results["data_availability"] = data_results

    def test_node_mappings(self):
        """Test node ID mappings and consistency."""
        print("\n4. Testing Node Mappings...")

        if not self.client:
            print("❌ No BigQuery client - skipping node mapping tests")
            return

        try:
            # Test original node mappings
            node_mapping = {
                "00000000-0000-0000-0000-000000000001": "node-santanna",
                "00000000-0000-0000-0000-000000000002": "node-seneca",
                "00000000-0000-0000-0000-000000000003": "node-serbatoio",
            }

            print("📋 Testing original node mappings...")
            for uuid_id, bigquery_id in node_mapping.items():
                query = """
                SELECT COUNT(*) as count
                FROM `{self.project_id}.{self.dataset_id}.v_sensor_readings_normalized`
                WHERE node_id = '{bigquery_id}'
                """

                try:
                    query_job = self.client.query(query)
                    results = list(query_job.result())
                    count = results[0].count if results else 0

                    if count > 0:
                        print(f"✅ Node '{bigquery_id}' has {count:,} readings")
                    else:
                        print(f"⚠️  Node '{bigquery_id}' has no data")

                except Exception as e:
                    print(f"❌ Error checking node '{bigquery_id}': {e}")

            # Test new node mappings if they exist
            try:
                query = """
                SELECT DISTINCT node_id, COUNT(*) as count
                FROM `{}.{}.sensor_readings_ml`
                GROUP BY node_id
                ORDER BY count DESC
                """.format(
                    self.project_id, self.dataset_id
                )

                query_job = self.client.query(query)
                results = list(query_job.result())

                if results:
                    print("\n📋 New nodes found in sensor_readings_ml:")
                    for row in results:
                        print(f"  - {row.node_id}: {row.count:,} readings")

            except Exception as e:
                print(f"⚠️  Could not check new nodes: {e}")

            self.diagnostics_results["node_mappings"] = "TESTED"

        except Exception as e:
            print(f"❌ Node mapping test failed: {e}")
            self.diagnostics_results["node_mappings"] = f"ERROR: {e}"

    def test_repository_config(self):
        """Test repository configuration and data access."""
        print("\n5. Testing Repository Configuration...")

        try:
            # Test DI container configuration
            container = Container()
            container.config.from_dict(
                {
                    "bigquery": {
                        "project_id": self.project_id,
                        "dataset_id": self.dataset_id,
                        "credentials_path": None,
                        "location": self.location,
                    }
                }
            )

            # Test sensor reading repository
            sensor_repo = container.sensor_reading_repository()
            print("✅ Sensor reading repository initialized")

            # Test async data fetch
            async def test_async_fetch():
                try:
                    # Test with a known node ID
                    node_id = UUID("00000000-0000-0000-0000-000000000001")

                    # Use data range that should have data
                    end_time = datetime(2025, 3, 31, 23, 59, 59)
                    start_time = end_time - timedelta(days=1)

                    readings = await sensor_repo.get_by_node_id(
                        node_id=node_id,
                        start_time=start_time,
                        end_time=end_time,
                        limit=10,
                    )

                    print(f"✅ Retrieved {len(readings)} readings from repository")

                    if readings:
                        sample = readings[0]
                        print(
                            f"    Sample: {sample.timestamp}, Flow: {sample.flow_rate}"
                        )

                    return len(readings)

                except Exception as e:
                    print(f"❌ Repository data fetch failed: {e}")
                    return 0

            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            reading_count = loop.run_until_complete(test_async_fetch())

            self.diagnostics_results["repository_config"] = {
                "initialization": "SUCCESS",
                "data_fetch": reading_count,
            }

        except Exception as e:
            print(f"❌ Repository configuration test failed: {e}")
            self.diagnostics_results["repository_config"] = f"ERROR: {e}"

    def test_dashboard_dependencies(self):
        """Test dashboard-specific dependencies and imports."""
        print("\n6. Testing Dashboard Dependencies...")

        try:
            # Test imports
            from src.presentation.streamlit.components.anomaly_tab import AnomalyTab
            from src.application.use_cases.detect_network_anomalies import (
                DetectNetworkAnomaliesUseCase,
            )

            print("✅ Dashboard imports successful")

            # Test use case initialization
            container = Container()
            container.config.from_dict(
                {
                    "bigquery": {
                        "project_id": self.project_id,
                        "dataset_id": self.dataset_id,
                        "credentials_path": None,
                        "location": self.location,
                    }
                }
            )

            use_case = container.detect_network_anomalies_use_case()
            print("✅ Anomaly detection use case initialized")

            # Test anomaly tab initialization
            anomaly_tab = AnomalyTab(use_case)
            print("✅ Anomaly tab initialized")

            self.diagnostics_results["dashboard_dependencies"] = "SUCCESS"

        except Exception as e:
            print(f"❌ Dashboard dependencies test failed: {e}")
            self.diagnostics_results["dashboard_dependencies"] = f"ERROR: {e}"

    def print_summary(self):
        """Print diagnostic summary and recommendations."""
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)

        issues_found = []

        for test_name, result in self.diagnostics_results.items():
            if isinstance(result, str) and ("ERROR" in result or "FAILED" in result):
                issues_found.append(f"❌ {test_name}: {result}")
            elif (
                isinstance(result, dict)
                and "data_fetch" in result
                and result["data_fetch"] == 0
            ):
                issues_found.append(f"⚠️  {test_name}: No data retrieved")

        if issues_found:
            print("\n🚨 ISSUES FOUND:")
            for issue in issues_found:
                print(f"  {issue}")
        else:
            print("\n✅ All diagnostics passed!")

        print("\n💡 RECOMMENDATIONS:")

        if "bigquery_auth" in self.diagnostics_results and "FAILED" in str(
            self.diagnostics_results["bigquery_auth"]
        ):
            print(
                "  1. Check BigQuery authentication - ensure GOOGLE_APPLICATION_CREDENTIALS is set"
            )
            print("  2. Verify project permissions for project 'abbanoa-464816'")

        if "dataset_access" in self.diagnostics_results and "NOT_FOUND" in str(
            self.diagnostics_results["dataset_access"]
        ):
            print("  3. Dataset 'water_infrastructure' not found - check dataset name")

        if any(
            "data_fetch" in str(result) and "0" in str(result)
            for result in self.diagnostics_results.values()
        ):
            print("  4. No data retrieved - check node mappings and time ranges")
            print(
                "  5. Verify data exists in the expected date range (Nov 2024 - Mar 2025)"
            )

        print("\n📋 Full results saved to diagnostics_results.json")

        # Save detailed results
        import json

        with open("diagnostics_results.json", "w") as f:
            json.dump(self.diagnostics_results, f, indent=2, default=str)


def main():
    """Run the diagnostics."""
    diagnostics = DataDiagnostics()
    diagnostics.run_full_diagnostics()


if __name__ == "__main__":
    main()

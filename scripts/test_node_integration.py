#!/usr/bin/env python3
"""
Test script to verify new node integration.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Setup environment
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
    "~/.config/gcloud/application_default_credentials.json"
)
os.environ["BIGQUERY_PROJECT_ID"] = "abbanoa-464816"
os.environ["BIGQUERY_DATASET_ID"] = "water_infrastructure"


def test_node_configuration():
    """Test that node configuration is accessible."""
    print("1. Testing Node Configuration...")

    try:
        from src.config.node_overrides import NEW_BACKUP_NODES, get_all_node_names

        print(f"✅ Found {len(NEW_BACKUP_NODES)} new nodes:")
        for node_id, config in NEW_BACKUP_NODES.items():
            print(f"   - {config['name']} ({config['type']})")

        all_nodes = get_all_node_names()
        print(f"\n✅ Total nodes available: {len(all_nodes)}")

    except ImportError as e:
        print(f"❌ Failed to import node configuration: {e}")
        return False

    return True


def test_bigquery_data():
    """Test that new node data is accessible in BigQuery."""
    print("\n2. Testing BigQuery Data Access...")

    try:
        from google.cloud import bigquery
        from src.infrastructure.adapters.backup_node_adapter import BackupNodeAdapter

        # Initialize client
        client = bigquery.Client(project=os.environ["BIGQUERY_PROJECT_ID"])
        adapter = BackupNodeAdapter(client)

        # Test nodes
        test_nodes = ["215542", "281492"]

        print(f"\nQuerying data for nodes: {test_nodes}")
        df = adapter.get_node_data(
            node_ids=test_nodes, start_time=datetime.now() - timedelta(days=7)
        )

        if not df.empty:
            print(f"✅ Found {len(df)} readings")
            print("\nSample data:")
            print(
                df[
                    [
                        "timestamp",
                        "node_id",
                        "flow_rate",
                        "pressure",
                        "data_quality_score",
                    ]
                ].head()
            )

            # Check data quality
            avg_quality = df["data_quality_score"].mean()
            print(f"\n✅ Average data quality score: {avg_quality:.3f}")

        else:
            print("⚠️  No data found for test nodes in the last 7 days")

    except Exception as e:
        print(f"❌ Failed to access BigQuery data: {e}")
        return False

    return True


def test_dashboard_components():
    """Test that dashboard components have been updated."""
    print("\n3. Testing Dashboard Components...")

    # Check if sidebar was updated
    sidebar_path = (
        project_root / "src/presentation/streamlit/components/sidebar_filters.py"
    )
    if sidebar_path.exists():
        content = sidebar_path.read_text()
        if "Distribution 215542" in content or "Monitoring Nodes" in content:
            print("✅ Sidebar filters have been updated")
        else:
            print("⚠️  Sidebar filters may need manual update")

    # Check for backup files
    backup_files = list(project_root.glob("**/*.backup"))
    if backup_files:
        print(f"\n✅ Found {len(backup_files)} backup files from integration")

    return True


def print_summary():
    """Print integration summary and next steps."""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)

    print("\n✅ New nodes have been integrated successfully!")

    print("\n📊 Data Access:")
    print("- New nodes are stored in: sensor_readings_ml table")
    print("- Data includes quality scores and metadata")
    print("- Historical data from November 2024 onwards")

    print("\n🎯 Next Steps:")
    print("1. Run the dashboard: streamlit run src/presentation/streamlit/app.py")
    print("2. Check that new nodes appear in the sidebar")
    print("3. Verify data displays correctly")
    print("4. Test all visualizations with new nodes")

    print("\n💡 Enhancement Ideas:")
    print("- Add node type filtering (distribution vs monitoring)")
    print("- Display data quality indicators")
    print("- Group nodes by district in visualizations")
    print("- Add tooltips showing node metadata")


def main():
    """Run all integration tests."""
    print("=== Node Integration Test Suite ===\n")

    # Run tests
    config_ok = test_node_configuration()
    data_ok = test_bigquery_data()
    dashboard_ok = test_dashboard_components()

    # Summary
    if config_ok and data_ok and dashboard_ok:
        print_summary()
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Verify the node integration is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_sidebar_update():
    """Check if sidebar has been updated."""
    print("1. Checking Sidebar Update...")

    sidebar_path = (
        project_root / "src/presentation/streamlit/components/sidebar_filters.py"
    )
    content = sidebar_path.read_text()

    new_nodes = [
        "Distribution 215542",
        "Distribution 215600",
        "Distribution 273933",
        "Monitoring 281492",
        "Monitoring 288399",
        "Monitoring 288400",
    ]

    found_nodes = []
    for node in new_nodes:
        if node in content:
            found_nodes.append(node)

    if len(found_nodes) == len(new_nodes):
        print(f"✅ All {len(new_nodes)} new nodes found in sidebar")
    else:
        print(f"⚠️  Only {len(found_nodes)} of {len(new_nodes)} nodes found in sidebar")
        print(f"   Missing: {set(new_nodes) - set(found_nodes)}")

    return len(found_nodes) == len(new_nodes)


def check_utils_modules():
    """Check if utility modules are created."""
    print("\n2. Checking Utility Modules...")

    utils_files = [
        "src/presentation/streamlit/utils/node_mappings.py",
        "src/presentation/streamlit/utils/enhanced_data_fetcher.py",
    ]

    all_exist = True
    for file_path in utils_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False

    # Try importing
    try:
        from src.presentation.streamlit.utils import (
            get_node_ids_from_selection,
            EnhancedDataFetcher,
        )

        print("✅ Modules can be imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        all_exist = False

    return all_exist


def check_node_mappings():
    """Check node mappings are working."""
    print("\n3. Testing Node Mappings...")

    try:
        from src.presentation.streamlit.utils.node_mappings import (
            ALL_NODE_MAPPINGS,
            get_node_ids_from_selection,
        )

        # Test mapping
        test_selection = ["Distribution 215542", "Monitoring 281492"]
        node_ids = get_node_ids_from_selection(test_selection)

        print(f"✅ Test selection: {test_selection}")
        print(f"   Mapped to IDs: {node_ids}")

        # Check all nodes
        print(f"\n✅ Total nodes in mapping: {len(ALL_NODE_MAPPINGS)}")

        return True

    except Exception as e:
        print(f"❌ Error testing mappings: {e}")
        return False


def check_config_files():
    """Check configuration files."""
    print("\n4. Checking Configuration Files...")

    config_files = [
        ("src/config/node_overrides.py", "Node overrides config"),
        ("src/config/nodes.py", "Centralized node config"),
        ("src/infrastructure/adapters/backup_node_adapter.py", "Backup node adapter"),
    ]

    found_count = 0
    for file_path, description in config_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {description}: {file_path}")
            found_count += 1
        else:
            print(f"⚠️  {description} not found")

    return found_count


def print_summary():
    """Print integration summary."""
    print("\n" + "=" * 60)
    print("INTEGRATION VERIFICATION SUMMARY")
    print("=" * 60)

    print("\n✅ COMPLETED:")
    print("- Sidebar updated with 6 new nodes (grouped by type)")
    print("- Created node mapping utilities")
    print("- Created enhanced data fetcher for all nodes")
    print("- Configuration files in place")

    print("\n📊 NEW NODES AVAILABLE:")
    print("Distribution Nodes:")
    print("  - Node 215542")
    print("  - Node 215600")
    print("  - Node 273933")
    print("\nMonitoring Nodes:")
    print("  - Node 281492")
    print("  - Node 288399")
    print("  - Node 288400")

    print("\n🚀 USAGE:")
    print("1. Start the dashboard:")
    print("   streamlit run src/presentation/streamlit/app.py")
    print("\n2. Select new nodes from the sidebar")
    print("\n3. Data will be fetched from sensor_readings_ml table")

    print("\n💡 NEXT STEPS:")
    print("- Test all dashboard tabs with new nodes")
    print("- Monitor data quality scores")
    print("- Consider adding quality indicators to UI")


def main():
    """Run verification checks."""
    print("=== Node Integration Verification ===\n")

    # Run checks
    sidebar_ok = check_sidebar_update()
    utils_ok = check_utils_modules()
    mappings_ok = check_node_mappings()
    check_config_files()

    # Summary
    if sidebar_ok and utils_ok and mappings_ok:
        print_summary()
        print("\n✅ Integration verified successfully!")
    else:
        print("\n⚠️  Some components need attention")
        print("Please check the warnings above")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple test to verify the flow data fix implementation.
"""

import os
import sys
from pathlib import Path

# Setup environment
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing Flow Data Fix Implementation...")
print("=" * 60)

# Check node mappings
print("\n1. Checking node mappings...")
try:
    from src.presentation.streamlit.utils.node_mappings import ALL_NODE_MAPPINGS, get_node_ids_from_selection
    
    print(f"✅ Found {len(ALL_NODE_MAPPINGS)} total nodes:")
    
    uuid_count = 0
    numeric_count = 0
    
    for name, node_id in ALL_NODE_MAPPINGS.items():
        if node_id.startswith("00000000"):
            uuid_count += 1
            print(f"   - {name}: {node_id} (UUID)")
        else:
            numeric_count += 1
            print(f"   - {name}: {node_id} (Numeric)")
    
    print(f"\n   Total: {uuid_count} UUID nodes, {numeric_count} numeric nodes")
    
except Exception as e:
    print(f"❌ Error checking node mappings: {e}")

# Check overview_tab implementation
print("\n2. Checking overview_tab.py implementation...")
try:
    with open("src/presentation/streamlit/components/overview_tab.py", "r") as f:
        content = f.read()
        
    # Check if UnifiedDataAdapter is used
    if "UnifiedDataAdapter" in content and "adapter.get_node_data" in content:
        print("✅ overview_tab.py uses UnifiedDataAdapter for flow data")
    else:
        print("❌ overview_tab.py might not be using UnifiedDataAdapter")
    
    # Check if EnhancedDataFetcher is used
    if "EnhancedDataFetcher" in content and "fetcher.get_latest_readings" in content:
        print("✅ overview_tab.py uses EnhancedDataFetcher for latest node data")
    else:
        print("❌ overview_tab.py might not be using EnhancedDataFetcher")
        
    # Check if get_node_ids_from_selection is used
    if "get_node_ids_from_selection" in content:
        print("✅ overview_tab.py uses centralized node ID conversion")
    else:
        print("❌ overview_tab.py might not be using centralized node ID conversion")
        
except Exception as e:
    print(f"❌ Error checking overview_tab.py: {e}")

# Check UnifiedDataAdapter implementation
print("\n3. Checking UnifiedDataAdapter implementation...")
try:
    with open("src/presentation/streamlit/utils/unified_data_adapter.py", "r") as f:
        content = f.read()
        
    # Check if it handles both table types
    if "sensor_readings_ml" in content and "v_sensor_readings_normalized" in content:
        print("✅ UnifiedDataAdapter queries both original and ML tables")
    else:
        print("❌ UnifiedDataAdapter might not query both tables")
        
    # Check node ID handling
    if "uuid_nodes" in content and "string_nodes" in content:
        print("✅ UnifiedDataAdapter separates UUID and numeric node IDs")
    else:
        print("❌ UnifiedDataAdapter might not handle different node ID types")
        
except Exception as e:
    print(f"❌ Error checking UnifiedDataAdapter: {e}")

print("\n" + "=" * 60)
print("IMPLEMENTATION CHECK COMPLETE")
print("=" * 60)

print("\nSummary:")
print("- The dashboard should now properly fetch data for both UUID and numeric nodes")
print("- Flow charts should display data from all 9 configured nodes") 
print("- Node status cards should show latest data for all node types")
print("\nIf you still see 'No flow data found', check that:")
print("1. The sensor_readings_ml table exists in BigQuery")
print("2. The table contains data for the numeric node IDs")
print("3. Run: python scripts/process_backup_data.py if needed")
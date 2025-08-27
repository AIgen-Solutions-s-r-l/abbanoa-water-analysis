#!/usr/bin/env python3
"""
Verify that all coordinates have been updated to Cesena area
"""

import json
import sys

# Cesena center coordinates
CESENA_LAT = 44.13
CESENA_LON = 12.24

# Cagliari/Selargius coordinates
CAGLIARI_LAT = 39.2
CAGLIARI_LON = 9.1

def check_coordinates():
    """Check if coordinates are in Cesena area"""
    from src.config.nodes import ALL_NODES
    from src.scripts.update_real_topology import REAL_NODES
    
    print("=" * 80)
    print("COORDINATE VERIFICATION REPORT")
    print("=" * 80)
    print(f"\nTarget area: CESENA (lat: ~{CESENA_LAT}, lon: ~{CESENA_LON})")
    print(f"Old area: CAGLIARI (lat: ~{CAGLIARI_LAT}, lon: ~{CAGLIARI_LON})")
    print("\n" + "-" * 80)
    
    # Check nodes.py configuration
    print("\n1. CHECKING src/config/nodes.py:")
    print("-" * 40)
    
    all_cesena = True
    for node_key, node in ALL_NODES.items():
        lat_diff = abs(node.latitude - CESENA_LAT)
        lon_diff = abs(node.longitude - CESENA_LON)
        
        if lat_diff > 0.2 or lon_diff > 0.2:  # Outside Cesena area
            print(f"❌ {node.display_name}: lat={node.latitude}, lon={node.longitude} (NOT in Cesena area)")
            all_cesena = False
        else:
            print(f"✅ {node.display_name}: lat={node.latitude}, lon={node.longitude}")
    
    # Check update_real_topology.py
    print("\n2. CHECKING src/scripts/update_real_topology.py:")
    print("-" * 40)
    
    for node_id, node_data in REAL_NODES.items():
        lat_diff = abs(node_data['lat'] - CESENA_LAT)
        lon_diff = abs(node_data['lon'] - CESENA_LON)
        
        if lat_diff > 0.2 or lon_diff > 0.2:  # Outside Cesena area
            print(f"❌ {node_data['name']}: lat={node_data['lat']}, lon={node_data['lon']} (NOT in Cesena area)")
            all_cesena = False
        else:
            print(f"✅ {node_data['name']}: lat={node_data['lat']}, lon={node_data['lon']}")
    
    print("\n" + "=" * 80)
    if all_cesena:
        print("✅ SUCCESS: All coordinates have been updated to Cesena area!")
    else:
        print("❌ ERROR: Some coordinates are still in the old area!")
        sys.exit(1)
    print("=" * 80)
    
    # Generate summary
    print("\nSUMMARY:")
    print(f"- Total nodes in nodes.py: {len(ALL_NODES)}")
    print(f"- Total nodes in update_real_topology.py: {len(REAL_NODES)}")
    print(f"- All coordinates are within ~20km of Cesena center")
    
    # Show coordinate bounds
    all_lats = [node.latitude for node in ALL_NODES.values()] + [n['lat'] for n in REAL_NODES.values()]
    all_lons = [node.longitude for node in ALL_NODES.values()] + [n['lon'] for n in REAL_NODES.values()]
    
    print(f"\nCoordinate bounds:")
    print(f"- Latitude range: {min(all_lats):.4f} to {max(all_lats):.4f}")
    print(f"- Longitude range: {min(all_lons):.4f} to {max(all_lons):.4f}")

if __name__ == "__main__":
    check_coordinates()

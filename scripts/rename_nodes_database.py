#!/usr/bin/env python3
"""
Rename nodes in the database based on volume analysis results.

This script:
1. Maps CSV columns to actual node IDs
2. Renames nodes based on the volume analysis
3. Updates node types appropriately
"""

import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Optional

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

# Load renaming recommendations
def load_recommendations():
    """Load the renaming recommendations from JSON file."""
    try:
        with open('csv_node_renaming_recommendations.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Recommendations file not found. Run analyze_csv_volumes.py first!")
        return None

async def get_current_nodes(conn):
    """Get current nodes from the database."""
    query = """
        SELECT node_id, node_name, node_type, metadata
        FROM water_infrastructure.nodes
        WHERE is_active = true
        ORDER BY node_id
    """
    
    rows = await conn.fetch(query)
    return [dict(row) for row in rows]

async def map_columns_to_nodes(conn, recommendations):
    """
    Map CSV columns to actual node IDs.
    This is based on the typical pattern where:
    - M3 corresponds to the first node
    - M3.1 corresponds to the second node, etc.
    """
    
    # Get all nodes ordered by ID
    nodes = await get_current_nodes(conn)
    
    print(f"\n📊 Current nodes in database:")
    for node in nodes:
        print(f"  - {node['node_id']}: {node['node_name']} (Type: {node['node_type']})")
    
    # Common mappings based on node naming patterns
    # This assumes nodes follow patterns like NODE_215542, NODE_273933, etc.
    # or simple IDs like 001, 002, 003
    
    column_to_node_map = {}
    
    # Try to map based on order (this is a simple heuristic)
    volume_columns = ['M3', 'M3.1', 'M3.2', 'M3.3']
    
    if len(nodes) >= len(volume_columns):
        # Map by position
        for i, col in enumerate(volume_columns):
            if col in recommendations and i < len(nodes):
                column_to_node_map[col] = nodes[i]['node_id']
    else:
        print("\n⚠️  Warning: Fewer nodes in database than volume columns!")
        print("   Manual mapping may be required.")
    
    # Alternative: Look for specific patterns in node names/IDs
    # Override mappings based on known patterns
    specific_mappings = {
        # Add specific mappings here if known
        # e.g., 'M3.3': '003' if you know M3.3 maps to node_id 003
    }
    
    column_to_node_map.update(specific_mappings)
    
    return column_to_node_map

async def rename_nodes(conn, recommendations, column_to_node_map):
    """Execute the node renaming in the database."""
    
    renamed_count = 0
    
    print("\n🔄 Renaming nodes:")
    
    for col, rec in recommendations.items():
        if col not in column_to_node_map:
            print(f"  ⚠️  No mapping found for {col}")
            continue
        
        node_id = column_to_node_map[col]
        new_name = rec['new_node_name']
        new_type = rec['category']
        
        # Map category to proper node_type
        type_mapping = {
            'tank': 'storage',
            'distribution': 'distribution',
            'monitoring': 'monitoring'
        }
        node_type = type_mapping.get(new_type, new_type)
        
        try:
            # Update the node
            result = await conn.execute("""
                UPDATE water_infrastructure.nodes
                SET node_name = $1,
                    node_type = $2,
                    metadata = jsonb_set(
                        COALESCE(metadata, '{}'::jsonb),
                        '{volume_analysis}',
                        $3::jsonb,
                        true
                    ),
                    updated_at = CURRENT_TIMESTAMP
                WHERE node_id = $4
                RETURNING node_id
            """, 
            new_name, 
            node_type,
            json.dumps({
                'max_volume_m3': rec['max_volume'],
                'total_consumption_m3': rec['total_consumption'],
                'analysis_date': datetime.now().isoformat(),
                'original_column': col
            }),
            node_id
            )
            
            if result:
                print(f"  ✅ {node_id}: Renamed to {new_name} (Type: {node_type})")
                renamed_count += 1
            else:
                print(f"  ❌ {node_id}: Failed to update")
                
        except Exception as e:
            print(f"  ❌ Error updating {node_id}: {e}")
    
    return renamed_count

async def update_node_configurations():
    """Update node configuration files with new names."""
    
    print("\n📄 Generating updated node configuration...")
    
    # Read current recommendations
    recommendations = load_recommendations()
    if not recommendations:
        return
    
    # Generate Python configuration update
    config_content = '''"""
Updated node configuration based on volume analysis.
Generated: {timestamp}
"""

from typing import Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NodeConfig:
    """Configuration for a monitoring node."""
    node_id: str
    display_name: str
    node_type: str
    category: str
    max_volume_m3: float
    
# Node configurations based on volume analysis
VOLUME_BASED_NODES = {{
'''.format(timestamp=datetime.now().isoformat())
    
    for col, rec in recommendations.items():
        config_content += f'''    "{rec['new_node_name']}": NodeConfig(
        node_id="{rec['new_node_name'].lower()}",
        display_name="{rec['new_node_name']}",
        node_type="{rec['category']}",
        category="{rec['category'].title()}",
        max_volume_m3={rec['max_volume']:.0f}
    ),
'''
    
    config_content += '''}\n'''
    
    # Save configuration
    with open('node_config_volume_based.py', 'w') as f:
        f.write(config_content)
    
    print("  ✅ Created node_config_volume_based.py")

async def main():
    """Main execution function."""
    print("🔧 Node Renaming Tool")
    print("=" * 50)
    
    # Load recommendations
    recommendations = load_recommendations()
    if not recommendations:
        return
    
    # Connect to database
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\n💡 Make sure the database is running:")
        print("   docker-compose up -d postgres")
        return
    
    try:
        # Map columns to nodes
        column_to_node_map = await map_columns_to_nodes(conn, recommendations)
        
        if not column_to_node_map:
            print("\n❌ Unable to map columns to nodes!")
            return
        
        print("\n📋 Column to Node Mapping:")
        for col, node_id in column_to_node_map.items():
            if col in recommendations:
                rec = recommendations[col]
                print(f"  {col} → Node ID: {node_id} → New name: {rec['new_node_name']}")
        
        # Confirm before proceeding
        print("\n⚠️  This will rename nodes in the database!")
        response = input("Proceed with renaming? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Renaming cancelled")
            return
        
        # Rename nodes
        renamed_count = await rename_nodes(conn, recommendations, column_to_node_map)
        
        print(f"\n✅ Successfully renamed {renamed_count} nodes")
        
        # Verify the changes
        print("\n📊 Updated nodes:")
        updated_nodes = await get_current_nodes(conn)
        for node in updated_nodes:
            print(f"  - {node['node_id']}: {node['node_name']} (Type: {node['node_type']})")
        
    finally:
        await conn.close()
        print("\n🔌 Database connection closed")
    
    # Update configuration files
    await update_node_configurations()
    
    print("\n✨ Node renaming complete!")

if __name__ == "__main__":
    asyncio.run(main())


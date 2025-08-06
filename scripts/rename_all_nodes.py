#!/usr/bin/env python3
"""
Rename ALL nodes in the database with a systematic naming convention.
"""

import asyncio
import asyncpg
import json
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

# Node type prefixes
NODE_TYPE_PREFIXES = {
    'storage': 'TANK',
    'distribution': 'NODE',
    'monitoring': 'MONITOR',
    'distribution_center': 'DISTCENTER',
    'interconnection': 'INTERCON',
    'zone_meter': 'ZONE',
    'sensor': 'SENSOR',
    'pump': 'PUMP',
    'valve': 'VALVE'
}

async def get_all_nodes(conn):
    """Get all active nodes from the database."""
    query = """
        SELECT node_id, node_name, node_type 
        FROM water_infrastructure.nodes 
        WHERE is_active = true
        ORDER BY node_type, node_name
    """
    
    rows = await conn.fetch(query)
    return [dict(row) for row in rows]

async def create_renaming_plan(nodes):
    """Create a systematic renaming plan for all nodes."""
    renaming_plan = {}
    type_counters = {}
    
    # Group nodes by type
    nodes_by_type = {}
    for node in nodes:
        node_type = node['node_type']
        if node_type not in nodes_by_type:
            nodes_by_type[node_type] = []
        nodes_by_type[node_type].append(node)
    
    # Create new names for each type
    for node_type, type_nodes in nodes_by_type.items():
        prefix = NODE_TYPE_PREFIXES.get(node_type, 'NODE')
        counter = 1
        
        for node in sorted(type_nodes, key=lambda x: x['node_name']):
            # Check if already renamed (skip TANK01, NODE01, MONITOR01, MONITOR02)
            if node['node_name'] in ['TANK01', 'NODE01', 'MONITOR01', 'MONITOR02']:
                renaming_plan[node['node_id']] = {
                    'current_name': node['node_name'],
                    'new_name': node['node_name'],  # Keep existing name
                    'node_type': node['node_type'],
                    'action': 'keep'
                }
            else:
                new_name = f"{prefix}{counter:02d}"
                renaming_plan[node['node_id']] = {
                    'current_name': node['node_name'],
                    'new_name': new_name,
                    'node_type': node['node_type'],
                    'action': 'rename'
                }
                counter += 1
    
    return renaming_plan

async def apply_renaming(conn, renaming_plan):
    """Apply the renaming plan to the database."""
    renamed_count = 0
    
    for node_id, plan in renaming_plan.items():
        if plan['action'] == 'rename':
            try:
                await conn.execute("""
                    UPDATE water_infrastructure.nodes
                    SET node_name = $1,
                        metadata = jsonb_set(
                            COALESCE(metadata, '{}'::jsonb),
                            '{renaming_info}',
                            $2::jsonb,
                            true
                        ),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE node_id = $3
                """, 
                plan['new_name'],
                json.dumps({
                    'original_name': plan['current_name'],
                    'renamed_date': datetime.now().isoformat(),
                    'naming_convention': 'systematic_v2'
                }),
                node_id
                )
                renamed_count += 1
                print(f"  ✅ {plan['current_name']:20} → {plan['new_name']:15} (Type: {plan['node_type']})")
            except Exception as e:
                print(f"  ❌ Error renaming {node_id}: {e}")
        else:
            print(f"  ⏭️  {plan['current_name']:20} → {plan['new_name']:15} (Already renamed)")
    
    return renamed_count

async def main():
    """Main execution function."""
    print("🔧 Comprehensive Node Renaming Tool")
    print("=" * 60)
    
    # Connect to database
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Connected to database\n")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    try:
        # Get all nodes
        nodes = await get_all_nodes(conn)
        print(f"📊 Found {len(nodes)} active nodes\n")
        
        # Display current state
        print("Current nodes by type:")
        nodes_by_type = {}
        for node in nodes:
            if node['node_type'] not in nodes_by_type:
                nodes_by_type[node['node_type']] = 0
            nodes_by_type[node['node_type']] += 1
        
        for node_type, count in sorted(nodes_by_type.items()):
            print(f"  - {node_type:20}: {count} nodes")
        
        # Create renaming plan
        print("\n📋 Creating renaming plan...")
        renaming_plan = await create_renaming_plan(nodes)
        
        # Count actions
        rename_count = sum(1 for p in renaming_plan.values() if p['action'] == 'rename')
        keep_count = sum(1 for p in renaming_plan.values() if p['action'] == 'keep')
        
        print(f"\nRenaming summary:")
        print(f"  - Nodes to rename: {rename_count}")
        print(f"  - Nodes to keep: {keep_count}")
        
        # Save renaming plan
        plan_file = 'all_nodes_renaming_plan.json'
        with open(plan_file, 'w') as f:
            json.dump(renaming_plan, f, indent=2)
        print(f"\n💾 Renaming plan saved to: {plan_file}")
        
        # Display renaming plan
        print("\n🔄 Renaming Plan:")
        print("-" * 60)
        
        # Group by type for display
        for node_type in sorted(nodes_by_type.keys()):
            type_plans = [(nid, p) for nid, p in renaming_plan.items() if p['node_type'] == node_type]
            if type_plans:
                print(f"\n{node_type.upper()}:")
                for node_id, plan in sorted(type_plans, key=lambda x: x[1]['new_name']):
                    action_symbol = "→" if plan['action'] == 'rename' else "="
                    print(f"  {plan['current_name']:25} {action_symbol} {plan['new_name']:15}")
        
        # Confirm before proceeding
        print("\n⚠️  This will rename all nodes in the database!")
        response = input("Proceed with renaming? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Renaming cancelled")
            return
        
        # Apply renaming
        print("\n🔄 Applying renaming...")
        renamed_count = await apply_renaming(conn, renaming_plan)
        
        print(f"\n✅ Successfully renamed {renamed_count} nodes")
        
        # Verify final state
        print("\n📊 Final node names:")
        final_nodes = await get_all_nodes(conn)
        for node in sorted(final_nodes, key=lambda x: x['node_name']):
            print(f"  {node['node_id']:15} → {node['node_name']:15} (Type: {node['node_type']})")
        
    finally:
        await conn.close()
        print("\n🔌 Database connection closed")
    
    print("\n✨ Comprehensive node renaming complete!")

if __name__ == "__main__":
    asyncio.run(main())

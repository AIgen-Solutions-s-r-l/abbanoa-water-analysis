#!/usr/bin/env python3
"""
Script to anonymize all node names in the database.
Replaces real location names with generic functional names.
"""

import asyncpg
import asyncio
import os
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'database': os.getenv('POSTGRES_DB', 'abbanoa_processing'),
    'user': os.getenv('POSTGRES_USER', 'abbanoa_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'abbanoa_secure_pass')
}

# Anonymization mapping based on node types
ANONYMIZATION_MAPPING = {
    # Distribution centers
    'CENTRO_EST': 'DIST01',
    'CENTRO_NORD': 'DIST02', 
    'CENTRO_OVEST': 'DIST03',
    'CENTRO_SUD': 'DIST04',
    
    # Interconnections
    'FIORI': 'INTERCON01',
    'Q_GALLUS': 'INTERCON02',
    'Q_MATTEOTTI': 'INTERCON03',
    'Q_MONSERRATO': 'INTERCON04',
    'Q_NENNI_SUD': 'INTERCON05',
    'Q_SANTANNA': 'INTERCON06',
    'Q_SARDEGNA': 'INTERCON07',
    'Q_TRIESTE': 'INTERCON08',
    
    # Zone meters
    'LIBERTA': 'ZONE01',
    'STADIO': 'ZONE02'
}

async def anonymize_node_names():
    """Anonymize all node names in the database."""
    print("🔒 Starting Node Names Anonymization")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Get current nodes
        print("📋 Current node names:")
        current_nodes = await conn.fetch("""
            SELECT node_id, node_name, node_type 
            FROM water_infrastructure.nodes 
            WHERE is_active = true 
            ORDER BY node_name
        """)
        
        for node in current_nodes:
            print(f"   {node['node_id']}: {node['node_name']} ({node['node_type']})")
        
        print(f"\n🔄 Anonymizing {len(current_nodes)} nodes...")
        
        # Update each node with anonymized name
        for node in current_nodes:
            node_id = node['node_id']
            new_name = ANONYMIZATION_MAPPING.get(node_id)
            
            if new_name:
                await conn.execute("""
                    UPDATE water_infrastructure.nodes 
                    SET node_name = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE node_id = $2
                """, new_name, node_id)
                
                print(f"   ✅ {node_id}: {node['node_name']} → {new_name}")
            else:
                print(f"   ⚠️  {node_id}: No mapping found for {node['node_name']}")
        
        # Verify the changes
        print("\n📋 Updated node names:")
        updated_nodes = await conn.fetch("""
            SELECT node_id, node_name, node_type 
            FROM water_infrastructure.nodes 
            WHERE is_active = true 
            ORDER BY node_name
        """)
        
        for node in updated_nodes:
            print(f"   {node['node_id']}: {node['node_name']} ({node['node_type']})")
        
        await conn.close()
        
        print("\n✅ Node names anonymization completed successfully!")
        print(f"📊 Total nodes updated: {len(current_nodes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during anonymization: {e}")
        return False

async def main():
    """Main function."""
    success = await anonymize_node_names()
    
    if success:
        print("\n🎉 All node names have been anonymized!")
        print("📝 Next steps:")
        print("   1. Restart the API services to pick up changes")
        print("   2. Test the Infrastructure Map")
        print("   3. Verify no real location names are visible")
    else:
        print("\n❌ Anonymization failed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())

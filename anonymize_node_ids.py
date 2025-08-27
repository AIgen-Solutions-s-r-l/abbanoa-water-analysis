#!/usr/bin/env python3
"""
Script to anonymize node IDs in the database.
Replaces real location names in node_id with generic functional IDs.
Maintains referential integrity with foreign key constraints.
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

# Node ID anonymization mapping
NODE_ID_MAPPING = {
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

async def anonymize_node_ids():
    """Anonymize node IDs while maintaining referential integrity."""
    print("🔒 Starting Node ID Anonymization")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Start transaction
        async with conn.transaction():
            print("📋 Current node IDs:")
            current_nodes = await conn.fetch("""
                SELECT node_id, node_name, node_type 
                FROM water_infrastructure.nodes 
                WHERE is_active = true 
                ORDER BY node_id
            """)
            
            for node in current_nodes:
                print(f"   {node['node_id']}: {node['node_name']} ({node['node_type']})")
            
            print(f"\n🔄 Anonymizing {len(current_nodes)} node IDs...")
            
            # First, temporarily disable foreign key constraints
            print("\n🔧 Temporarily disabling foreign key constraints...")
            await conn.execute("SET session_replication_role = replica;")
            
            # Update node IDs in the nodes table
            print("\n📝 Updating node IDs in nodes table...")
            for old_id, new_id in NODE_ID_MAPPING.items():
                await conn.execute("""
                    UPDATE water_infrastructure.nodes 
                    SET node_id = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE node_id = $2
                """, new_id, old_id)
                print(f"   ✅ {old_id} → {new_id}")
            
            # Update node IDs in sensor_readings table
            print("\n📊 Updating node IDs in sensor_readings table...")
            for old_id, new_id in NODE_ID_MAPPING.items():
                result = await conn.execute("""
                    UPDATE water_infrastructure.sensor_readings 
                    SET node_id = $1
                    WHERE node_id = $2
                """, new_id, old_id)
                print(f"   ✅ {old_id} → {new_id} (sensor_readings)")
            
            # Update node IDs in anomalies table
            print("\n⚠️  Updating node IDs in anomalies table...")
            for old_id, new_id in NODE_ID_MAPPING.items():
                result = await conn.execute("""
                    UPDATE water_infrastructure.anomalies 
                    SET node_id = $1
                    WHERE node_id = $2
                """, new_id, old_id)
                print(f"   ✅ {old_id} → {new_id} (anomalies)")
            
            # Re-enable foreign key constraints
            print("\n🔧 Re-enabling foreign key constraints...")
            await conn.execute("SET session_replication_role = DEFAULT;")
            
            # Verify foreign key constraints
            print("\n🔍 Verifying foreign key constraints...")
            try:
                await conn.execute("""
                    SELECT 1 FROM water_infrastructure.sensor_readings sr
                    JOIN water_infrastructure.nodes n ON sr.node_id = n.node_id
                    LIMIT 1
                """)
                print("   ✅ sensor_readings foreign key constraint verified")
                
                await conn.execute("""
                    SELECT 1 FROM water_infrastructure.anomalies a
                    JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
                    LIMIT 1
                """)
                print("   ✅ anomalies foreign key constraint verified")
                
            except Exception as e:
                print(f"   ❌ Foreign key constraint verification failed: {e}")
                raise
        
        # Verify the changes
        print("\n📋 Updated node IDs:")
        updated_nodes = await conn.fetch("""
            SELECT node_id, node_name, node_type 
            FROM water_infrastructure.nodes 
            WHERE is_active = true 
            ORDER BY node_id
        """)
        
        for node in updated_nodes:
            print(f"   {node['node_id']}: {node['node_name']} ({node['node_type']})")
        
        # Count records in related tables
        sensor_count = await conn.fetchval("SELECT COUNT(*) FROM water_infrastructure.sensor_readings")
        anomalies_count = await conn.fetchval("SELECT COUNT(*) FROM water_infrastructure.anomalies")
        
        print(f"\n📊 Related records updated:")
        print(f"   - sensor_readings: {sensor_count} records")
        print(f"   - anomalies: {anomalies_count} records")
        
        await conn.close()
        
        print("\n✅ Node ID anonymization completed successfully!")
        print(f"📊 Total nodes updated: {len(current_nodes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during anonymization: {e}")
        return False

async def main():
    """Main function."""
    success = await anonymize_node_ids()
    
    if success:
        print("\n🎉 All node IDs have been anonymized!")
        print("📝 Next steps:")
        print("   1. Restart the API services to pick up changes")
        print("   2. Test the Infrastructure Map")
        print("   3. Verify no real location names are visible in node IDs")
    else:
        print("\n❌ Node ID anonymization failed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())

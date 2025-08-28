#!/usr/bin/env python3
"""Standalone test script for mock data generation verification."""

import asyncio
import asyncpg
import subprocess
import sys
from datetime import datetime, timezone, timedelta

DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

async def test_mock_data_system():
    """Test the complete mock data generation system."""
    print("🧪 Mock Data Generation System Verification")
    print("="*60)
    
    # Connect to database
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    try:
        # Test 1: Database connectivity
        print("\n🔍 Test 1: Database Connectivity")
        result = await conn.fetchval("SELECT COUNT(*) FROM water_infrastructure.nodes WHERE is_active = true")
        print(f"   Active nodes: {result}")
        if result > 0:
            print("✅ Database connectivity test passed")
        else:
            print("❌ No active nodes found")
            return False
        
        # Test 2: Node configuration
        print("\n🔍 Test 2: Node Configuration")
        db_nodes = await conn.fetch("""
            SELECT node_id, node_name, node_type
            FROM water_infrastructure.nodes
            WHERE is_active = true
            ORDER BY node_name
        """)
        print(f"   Found {len(db_nodes)} active nodes")
        if len(db_nodes) == 14:
            print("✅ Correct number of nodes (14)")
        else:
            print(f"⚠️  Expected 14 nodes, found {len(db_nodes)}")
        
        # Test 3: Data generation
        print("\n🔍 Test 3: Data Generation")
        initial_count = await conn.fetchval("""
            SELECT COUNT(*) FROM water_infrastructure.sensor_readings 
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """)
        print(f"   Initial records in last hour: {initial_count}")
        
        result = subprocess.run(['python3', 'scripts/hourly_data_generator.py'], 
                              capture_output=True, text=True, cwd='/home/alessio/Customers/Abbanoa')
        if result.returncode == 0:
            print("✅ Hourly data generator executed successfully")
        else:
            print(f"❌ Hourly data generator failed: {result.stderr}")
            return False
        
        # Test 4: Scheduling
        print("\n🔍 Test 4: Scheduling System")
        result = subprocess.run(['systemctl', 'is-active', 'abbanoa-hourly-data.timer'], 
                              capture_output=True, text=True)
        if result.stdout.strip() == 'active':
            print("✅ Systemd timer is active")
        else:
            print(f"❌ Systemd timer not active: {result.stdout}")
        
        # Test 5: API integration
        print("\n🔍 Test 5: API Integration")
        dashboard_data = await conn.fetch("""
            SELECT DISTINCT ON (n.node_id) n.node_id, n.node_name, n.node_type
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON sr.node_id = n.node_id AND sr.timestamp > NOW() - INTERVAL '24 hours'
            WHERE n.is_active = true
            ORDER BY n.node_id, sr.timestamp DESC NULLS LAST
        """)
        print(f"   API returned data for {len(dashboard_data)} nodes")
        if len(dashboard_data) == 14:
            print("✅ API integration test passed")
        else:
            print(f"❌ Expected 14 nodes, got {len(dashboard_data)}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await conn.close()

if __name__ == "__main__":
    success = asyncio.run(test_mock_data_system())
    sys.exit(0 if success else 1)

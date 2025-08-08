#!/usr/bin/env python3
"""
Test script for the hourly data generator
Runs the generator once and shows the results
"""

import asyncio
import asyncpg
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the hourly generator
from hourly_data_generator import generate_hourly_data, DB_CONFIG

async def test_generator():
    """Test the hourly data generator"""
    print("🧪 Testing Hourly Data Generator")
    print("=" * 50)
    
    # Get current time
    now = datetime.now(timezone.utc)
    print(f"Current time: {now}")
    print()
    
    # Check current data before generation
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Get record count before
        before_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= NOW() - INTERVAL '2 hours'
        """)
        print(f"Records in last 2 hours (before): {before_count}")
        
        # Get latest timestamp for each node
        print("\nLatest timestamps per node (before):")
        latest_before = await conn.fetch("""
            SELECT DISTINCT ON (node_id)
                node_id,
                timestamp,
                flow_rate
            FROM water_infrastructure.sensor_readings
            ORDER BY node_id, timestamp DESC
            LIMIT 5;
        """)
        for row in latest_before:
            print(f"  {row['node_id']:15} - {row['timestamp']} (flow: {row['flow_rate']})")
        
        print("\n" + "-" * 50)
        print("Running hourly data generator...")
        print("-" * 50 + "\n")
        
        # Run the generator
        await generate_hourly_data()
        
        print("\n" + "-" * 50)
        print("Post-generation verification:")
        print("-" * 50)
        
        # Get record count after
        after_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= NOW() - INTERVAL '2 hours'
        """)
        print(f"\nRecords in last 2 hours (after): {after_count}")
        print(f"New records inserted: {after_count - before_count}")
        
        # Get latest timestamp for each node after
        print("\nLatest timestamps per node (after):")
        latest_after = await conn.fetch("""
            SELECT DISTINCT ON (node_id)
                node_id,
                timestamp,
                flow_rate,
                temperature,
                pressure,
                is_interpolated
            FROM water_infrastructure.sensor_readings
            ORDER BY node_id, timestamp DESC
            LIMIT 5;
        """)
        for row in latest_after:
            print(f"  {row['node_id']:15} - {row['timestamp']} "
                  f"(flow: {row['flow_rate']}, temp: {row['temperature']}, "
                  f"pressure: {row['pressure']}, synthetic: {row['is_interpolated']})")
        
        # Show newly inserted records
        print("\nNewly inserted records (last hour):")
        new_records = await conn.fetch("""
            SELECT 
                timestamp,
                node_id,
                flow_rate,
                temperature,
                pressure,
                total_flow
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            AND is_interpolated = true
            ORDER BY timestamp DESC, node_id
            LIMIT 10;
        """)
        
        if new_records:
            for row in new_records:
                flow = f"{row['flow_rate']:6.1f}" if row['flow_rate'] is not None else "   N/A"
                temp = f"{row['temperature']:4.1f}" if row['temperature'] is not None else " N/A"
                press = f"{row['pressure']:3.1f}" if row['pressure'] is not None else "N/A"
                total = f"{row['total_flow']:7.1f}" if row['total_flow'] is not None else "     N/A"
                print(f"  {row['timestamp']} - {row['node_id']:15} - "
                      f"Flow: {flow}, Temp: {temp}, Press: {press}, Total: {total}")
        else:
            print("  No new synthetic records found in the last hour")
        
        # Check data distribution
        print("\nData distribution check (records per hour, last 24h):")
        distribution = await conn.fetch("""
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as record_count,
                COUNT(DISTINCT node_id) as unique_nodes
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 10;
        """)
        
        for row in distribution:
            print(f"  {row['hour']} - {row['record_count']:3} records, {row['unique_nodes']:2} nodes")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    print("Abbanoa Hourly Data Generator Test")
    print("==================================\n")
    
    # Create logs directory if needed
    os.makedirs('/home/alessio/Customers/Abbanoa/logs', exist_ok=True)
    
    # Run test
    asyncio.run(test_generator())

#!/usr/bin/env python3
"""
Simulate what the hourly generator would insert for future timestamps
This is a demonstration script showing what data would be generated
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta, timezone
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hourly_data_generator import (
    DB_CONFIG, 
    load_data_patterns, 
    generate_sensor_reading,
    get_node_specific_multipliers
)

async def simulate_future_generation():
    """Simulate future data generation without actually inserting"""
    print("🔮 Simulating Future Data Generation")
    print("=" * 60)
    
    # Load patterns
    patterns = load_data_patterns()
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Get active nodes
        active_nodes = await conn.fetch("""
            SELECT node_id, node_type, node_name
            FROM water_infrastructure.nodes
            WHERE is_active = true
            ORDER BY node_id
            LIMIT 5;  -- Just show first 5 nodes for demo
        """)
        
        # Simulate next 3 hours of data
        base_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        future_time = base_time + timedelta(hours=1)  # Next hour
        
        print(f"Current time: {base_time}")
        print(f"Simulating data for: {future_time} onwards\n")
        
        # Generate 3 hours worth (6 half-hour slots)
        time_slots = []
        for i in range(6):
            time_slots.append(future_time + timedelta(minutes=30*i))
        
        print("Time slots that would be generated:")
        for ts in time_slots:
            print(f"  - {ts}")
        
        print("\n" + "-" * 60)
        print("Sample data that would be generated:")
        print("-" * 60 + "\n")
        
        # Show sample data for first 3 nodes and first 2 time slots
        for node in active_nodes[:3]:
            node_id = node['node_id']
            node_type = node['node_type']
            
            print(f"\n📊 Node: {node_id} ({node_type})")
            print("  " + "-" * 50)
            
            for ts in time_slots[:2]:  # Just show first 2 slots
                reading = generate_sensor_reading(
                    timestamp=ts,
                    node_id=node_id,
                    node_type=node_type,
                    patterns=patterns,
                    last_values=None
                )
                
                print(f"  {ts}:")
                print(f"    Temperature: {reading['temperature']}°C")
                print(f"    Flow Rate:   {reading['flow_rate']} L/s")
                print(f"    Pressure:    {reading['pressure']} bar")
                print(f"    Total Flow:  {reading['total_flow']} m³")
                print(f"    Quality:     {reading['quality_score']}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("📈 Summary of what would happen:")
        print("=" * 60)
        print(f"✓ Would generate data for {len(active_nodes)} nodes")
        print(f"✓ Would create {len(active_nodes) * 2} records per hour")
        print(f"✓ Each record marked as synthetic (is_interpolated=true)")
        print(f"✓ Data follows historical patterns with realistic variations")
        print(f"✓ Node-specific characteristics applied based on type")
        
        # Show when this would actually run
        print("\n⏰ Automatic Execution Schedule:")
        print("  - Runs every hour at :15 minutes past the hour")
        print("  - Next scheduled run would generate data for:")
        next_run = base_time.replace(minute=15)
        if next_run <= datetime.now(timezone.utc):
            next_run += timedelta(hours=1)
        print(f"    {next_run} → generates data for {base_time}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    print("Abbanoa Hourly Data Generator - Future Simulation")
    print("=" * 60 + "\n")
    asyncio.run(simulate_future_generation())

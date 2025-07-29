#!/usr/bin/env python3
"""
Insert historical readings for the last 48 hours for all nodes
"""
import asyncpg
import asyncio
import logging
from datetime import datetime, timedelta
import random
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

async def insert_historical_readings():
    """Insert 48 hours of historical readings for all nodes"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Get all active nodes
        nodes = await conn.fetch("""
            SELECT node_id, node_name, node_type
            FROM water_infrastructure.nodes
            WHERE is_active = true
            ORDER BY node_id
        """)
        
        logger.info(f"Found {len(nodes)} active nodes")
        
        # Get current readings for reference
        current_readings = {}
        for node in nodes:
            reading = await conn.fetchrow("""
                SELECT flow_rate, pressure, temperature
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1
                ORDER BY timestamp DESC
                LIMIT 1
            """, node['node_id'])
            
            if reading:
                current_readings[node['node_id']] = {
                    'flow_rate': float(reading['flow_rate']),
                    'pressure': float(reading['pressure']),
                    'temperature': float(reading['temperature'])
                }
            else:
                # Default values based on node type
                if node['node_type'] == 'distribution_center':
                    flow = 25.0 + random.uniform(-5, 5)
                elif node['node_type'] == 'zone_meter':
                    flow = 10.0 + random.uniform(-2, 2)
                else:
                    flow = 0.0
                
                current_readings[node['node_id']] = {
                    'flow_rate': flow,
                    'pressure': 3.5 + random.uniform(-0.5, 0.5),
                    'temperature': 18.0
                }
        
        # Generate historical data for the last 48 hours
        now = datetime.now()
        total_inserted = 0
        
        for node in nodes:
            node_id = node['node_id']
            base_values = current_readings[node_id]
            
            logger.info(f"Generating data for {node_id} ({node['node_name']})")
            
            # Create hourly readings for the last 48 hours
            for hours_ago in range(48, 0, -1):
                timestamp = now - timedelta(hours=hours_ago)
                hour_of_day = timestamp.hour
                
                # Daily pattern multiplier (higher during day, lower at night)
                if 6 <= hour_of_day <= 22:
                    daily_factor = 1.0 + 0.2 * math.sin((hour_of_day - 6) * math.pi / 16)
                else:
                    daily_factor = 0.7 + 0.1 * random.random()
                
                # Add some random variation
                random_factor = 0.95 + random.random() * 0.1
                
                # Calculate values
                flow_rate = base_values['flow_rate'] * daily_factor * random_factor
                pressure = base_values['pressure'] * (0.98 + random.random() * 0.04)
                temperature = 18.0 + 2 * math.sin((hour_of_day - 6) * math.pi / 12) + random.uniform(-0.5, 0.5)
                
                # Insert reading
                try:
                    await conn.execute("""
                        INSERT INTO water_infrastructure.sensor_readings
                        (node_id, timestamp, flow_rate, pressure, temperature)
                        VALUES ($1, $2, $3, $4, $5)
                    """, node_id, timestamp, flow_rate, pressure, temperature)
                except asyncpg.exceptions.UniqueViolationError:
                    # Skip if already exists
                    pass
                
                total_inserted += 1
        
        logger.info(f"✅ Inserted {total_inserted} historical readings")
        
        # Verify the data
        for node in nodes[:3]:  # Check first 3 nodes
            count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1
                AND timestamp > NOW() - INTERVAL '48 hours'
            """, node['node_id'])
            
            logger.info(f"  {node['node_id']}: {count} readings in last 48h")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(insert_historical_readings()) 
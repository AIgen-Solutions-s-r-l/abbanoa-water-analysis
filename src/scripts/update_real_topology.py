#!/usr/bin/env python3
"""
Update nodes with real Abbanoa topology based on actual network diagram
"""
import asyncpg
import asyncio
import logging
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real topology nodes with approximate coordinates based on the map
REAL_NODES = {
    # Main distribution centers
    'CENTRO_EST': {
        'name': 'CENTRO EST',
        'lat': 44.1355, 'lon': 12.2510,
        'type': 'distribution_center',
        'current_flow': 11.50
    },
    'CENTRO_NORD': {
        'name': 'CENTRO NORD', 
        'lat': 44.1400, 'lon': 12.2430,
        'type': 'distribution_center',
        'current_flow': 31.67
    },
    'CENTRO_SUD': {
        'name': 'CENTRO SUD',
        'lat': 44.1310, 'lon': 12.2450,
        'type': 'distribution_center', 
        'current_flow': 33.33
    },
    'CENTRO_OVEST': {
        'name': 'CENTRO OVEST',
        'lat': 44.1340, 'lon': 12.2350,
        'type': 'distribution_center',
        'current_flow': -19.46  # Negative indicates reverse flow
    },
    'LIBERTA': {
        'name': 'LIBERTÀ',
        'lat': 44.1280, 'lon': 12.2390,
        'type': 'zone_meter',
        'current_flow': 12.82
    },
    'STADIO': {
        'name': 'STADIO',
        'lat': 44.1310, 'lon': 12.2520,
        'type': 'zone_meter',
        'current_flow': 6.30
    },
    # Connection points to other districts
    'FIORI': {
        'name': 'FIORI',
        'lat': 44.1420, 'lon': 12.2390,
        'type': 'interconnection',
        'current_flow': 0
    },
    'Q_SANTANNA': {
        'name': 'Q.SANT\'ANNA',
        'lat': 44.1380, 'lon': 12.2350,
        'type': 'interconnection',
        'current_flow': 0
    },
    'Q_MONSERRATO': {
        'name': 'Q.MONSERRATO', 
        'lat': 44.1280, 'lon': 12.2340,
        'type': 'interconnection',
        'current_flow': 0
    },
    'Q_SARDEGNA': {
        'name': 'Q.SARDEGNA',
        'lat': 44.1390, 'lon': 12.2490,
        'type': 'interconnection', 
        'current_flow': 0
    },
    'Q_GALLUS': {
        'name': 'Q.GALLUS',
        'lat': 44.1307, 'lon': 12.2380,  # Using actual SCADA coordinates
        'type': 'interconnection',
        'current_flow': 0
    },
    'Q_MATTEOTTI': {
        'name': 'Q.MATTEOTTI',
        'lat': 44.1390, 'lon': 12.2470,  # Using actual SCADA coordinates
        'type': 'interconnection',
        'current_flow': 0
    },
    'Q_TRIESTE': {
        'name': 'Q.TRIESTE',
        'lat': 44.1361, 'lon': 12.2520,  # Using actual SCADA coordinates
        'type': 'interconnection',
        'current_flow': 0
    },
    'Q_NENNI_SUD': {
        'name': 'Q.NENNI SUD',
        'lat': 44.1270, 'lon': 12.2420,
        'type': 'interconnection',
        'current_flow': 0
    }
}

# Real pipe connections based on the topology diagram
REAL_PIPES = [
    # From arrival points to distribution centers
    ('Q_SARDEGNA', 'CENTRO_NORD'),
    ('Q_MATTEOTTI', 'CENTRO_EST'),
    ('Q_GALLUS', 'CENTRO_EST'),
    ('Q_GALLUS', 'CENTRO_SUD'),
    ('FIORI', 'CENTRO_NORD'),
    ('Q_SANTANNA', 'CENTRO_OVEST'),
    ('Q_MONSERRATO', 'CENTRO_OVEST'),
    
    # Between distribution centers
    ('CENTRO_NORD', 'CENTRO_EST'),
    ('CENTRO_NORD', 'CENTRO_OVEST'),
    ('CENTRO_EST', 'CENTRO_SUD'),
    ('CENTRO_OVEST', 'CENTRO_SUD'),
    
    # To zone meters
    ('CENTRO_OVEST', 'LIBERTA'),
    ('CENTRO_SUD', 'STADIO'),
    ('Q_TRIESTE', 'STADIO'),
    ('Q_NENNI_SUD', 'LIBERTA'),
]

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

async def update_topology():
    """Update nodes and pipes with real Abbanoa topology"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        logger.info("🔄 Updating to real Abbanoa topology...")
        
        # Clear existing data in correct order due to foreign keys
        await conn.execute("DELETE FROM water_infrastructure.anomalies")
        await conn.execute("DELETE FROM water_infrastructure.sensor_readings")
        await conn.execute("DELETE FROM water_infrastructure.pipe_connections")
        await conn.execute("DELETE FROM water_infrastructure.nodes")
        
        # Insert real nodes
        for node_id, node_data in REAL_NODES.items():
            await conn.execute("""
                INSERT INTO water_infrastructure.nodes 
                (node_id, node_name, location_name, latitude, longitude, 
                 node_type, is_active, installation_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, node_id, node_data['name'], 'Abbanoa', 
                node_data['lat'], node_data['lon'],
                node_data['type'], True, date(2010, 1, 1))
            
            # Insert current reading
            if node_data['current_flow'] != 0:
                await conn.execute("""
                    INSERT INTO water_infrastructure.sensor_readings
                    (node_id, timestamp, flow_rate, pressure, temperature)
                    VALUES ($1, NOW(), $2, $3, $4)
                """, node_id, abs(node_data['current_flow']), 3.5, 18.0)
            
            logger.info(f"✓ Added node: {node_data['name']} ({node_id})")
        
        # Insert pipes
        pipe_count = 0
        for from_node, to_node in REAL_PIPES:
            pipe_id = f"PIPE_{from_node}_{to_node}"
            
            # Get node coordinates
            from_coords = REAL_NODES[from_node]
            to_coords = REAL_NODES[to_node]
            
            # Calculate approximate distance
            lat_diff = abs(from_coords['lat'] - to_coords['lat'])
            lon_diff = abs(from_coords['lon'] - to_coords['lon'])
            distance = int(((lat_diff**2 + lon_diff**2)**0.5) * 111000)  # Rough conversion to meters
            
            await conn.execute("""
                INSERT INTO water_infrastructure.pipe_connections
                (from_node_id, to_node_id, pipe_length_m, pipe_diameter_mm, pipe_material)
                VALUES ($1, $2, $3, $4, $5)
            """, from_node, to_node, distance, 300, 'Steel')
            
            pipe_count += 1
        
        logger.info(f"✓ Created {pipe_count} pipe connections")
        
        # Verify results
        node_count = await conn.fetchval("SELECT COUNT(*) FROM water_infrastructure.nodes")
        logger.info(f"\n✅ Successfully updated topology: {node_count} nodes, {pipe_count} pipes")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_topology()) 
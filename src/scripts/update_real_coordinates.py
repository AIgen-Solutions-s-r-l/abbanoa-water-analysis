#!/usr/bin/env python3
"""
Update nodes with real SCADA coordinates from Selargius
"""
import asyncpg
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real coordinates from SCADA system
REAL_COORDINATES = {
    'NODO VIA GALLUS': {'lat': 39.2507717, 'lon': 9.1519532, 'scada_id': 'ND_PC_00009'},
    'NODO VIA MATTEOTTI': {'lat': 39.258977, 'lon': 9.1631273, 'scada_id': 'ND_PC_00006'},
    'NODO VIA NENNI': {'lat': 39.2596188, 'lon': 9.1621939, 'scada_id': 'ND_PC_00007'},
    'NODO VIA SARDEGNA': {'lat': 39.2577936, 'lon': 9.1653232, 'scada_id': 'ND_PC_00008'},
    'NODO VIA TRIESTE': {'lat': 39.2561181, 'lon': 9.1701813, 'scada_id': 'ND_PC_00005'},
}

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

async def update_coordinates():
    """Update nodes with real SCADA coordinates"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # First, let's see what nodes we have
        nodes = await conn.fetch("""
            SELECT node_id, node_name, location_name, latitude, longitude
            FROM water_infrastructure.nodes
            ORDER BY node_id
        """)
        
        logger.info(f"Found {len(nodes)} nodes in database")
        
        # Update specific nodes with real coordinates if we can match them
        updated_count = 0
        
        # Try to match by partial name
        for scada_name, coords in REAL_COORDINATES.items():
            # Extract the street name (e.g., "GALLUS" from "NODO VIA GALLUS")
            street = scada_name.replace('NODO VIA ', '').strip()
            
            # Try to find a matching node
            for node in nodes:
                node_name = node['node_name'] or ''
                if street.lower() in node_name.lower() or node['node_id'] == coords.get('scada_id'):
                    # Update this node with real coordinates
                    await conn.execute("""
                        UPDATE water_infrastructure.nodes
                        SET latitude = $1, 
                            longitude = $2,
                            location_name = 'Selargius',
                            node_name = $3
                        WHERE node_id = $4
                    """, coords['lat'], coords['lon'], scada_name, node['node_id'])
                    
                    logger.info(f"✓ Updated {node['node_id']} with {scada_name} coordinates: {coords['lat']}, {coords['lon']}")
                    updated_count += 1
                    break
        
        # For remaining nodes, distribute them around the Selargius area
        remaining_nodes = await conn.fetch("""
            SELECT node_id, node_name
            FROM water_infrastructure.nodes
            WHERE node_id NOT IN (
                SELECT node_id FROM water_infrastructure.nodes 
                WHERE node_name IN ($1, $2, $3, $4, $5)
            )
            ORDER BY node_id
        """, *REAL_COORDINATES.keys())
        
        # Use the center of the real coordinates as base
        center_lat = sum(c['lat'] for c in REAL_COORDINATES.values()) / len(REAL_COORDINATES)
        center_lon = sum(c['lon'] for c in REAL_COORDINATES.values()) / len(REAL_COORDINATES)
        
        logger.info(f"\nCenter of Selargius nodes: {center_lat:.6f}, {center_lon:.6f}")
        
        # Update remaining nodes to be distributed around the center
        import math
        for i, node in enumerate(remaining_nodes):
            # Create a small offset for each node
            angle = (2 * math.pi * i) / len(remaining_nodes)
            distance = 0.003 + (i % 2) * 0.002  # 300-500m radius
            
            new_lat = center_lat + distance * math.cos(angle)
            new_lon = center_lon + distance * math.sin(angle)
            
            await conn.execute("""
                UPDATE water_infrastructure.nodes
                SET latitude = $1, 
                    longitude = $2,
                    location_name = 'Selargius'
                WHERE node_id = $3
            """, new_lat, new_lon, node['node_id'])
            
            logger.info(f"✓ Updated {node['node_id']} near center: {new_lat:.6f}, {new_lon:.6f}")
            updated_count += 1
        
        # Create pipe connections between nearby nodes
        logger.info("\n📡 Creating pipe connections...")
        
        # Get all nodes with coordinates
        all_nodes = await conn.fetch("""
            SELECT node_id, latitude, longitude
            FROM water_infrastructure.nodes
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY node_id
        """)
        
        # Clear existing pipes
        await conn.execute("DELETE FROM water_infrastructure.pipe_connections")
        
        # Create connections between nearby nodes (within ~1km)
        pipe_count = 0
        for i, node1 in enumerate(all_nodes):
            for j, node2 in enumerate(all_nodes[i+1:], i+1):
                # Calculate distance (rough approximation)
                lat_diff = abs(float(node1['latitude']) - float(node2['latitude']))
                lon_diff = abs(float(node1['longitude']) - float(node2['longitude']))
                distance = math.sqrt(lat_diff**2 + lon_diff**2)
                
                # Connect nodes within ~1km (0.01 degrees ≈ 1km)
                if distance < 0.012:
                    pipe_id = f"PIPE_{node1['node_id']}_{node2['node_id']}"
                    
                    await conn.execute("""
                        INSERT INTO water_infrastructure.pipe_connections 
                        (pipe_id, from_node_id, to_node_id, length_m, diameter_mm, material, installation_year)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (pipe_id) DO NOTHING
                    """, pipe_id, node1['node_id'], node2['node_id'], 
                        int(distance * 111000),  # Convert to meters
                        200 + (pipe_count % 3) * 100,  # 200-400mm diameter
                        'Steel' if pipe_count % 2 == 0 else 'PVC',
                        2010 + (pipe_count % 10))
                    
                    pipe_count += 1
        
        logger.info(f"✓ Created {pipe_count} pipe connections")
        
        # Verify final results
        logger.info("\n📊 Final node distribution:")
        result = await conn.fetch("""
            SELECT location_name, COUNT(*) as count,
                   AVG(latitude)::numeric(10,6) as avg_lat,
                   AVG(longitude)::numeric(10,6) as avg_lon
            FROM water_infrastructure.nodes
            WHERE latitude IS NOT NULL
            GROUP BY location_name
            ORDER BY count DESC
        """)
        
        for row in result:
            logger.info(f"  {row['location_name']:20} - {row['count']} nodes (center: {row['avg_lat']}, {row['avg_lon']})")
        
        logger.info(f"\n✅ Successfully updated {updated_count} nodes with real/realistic coordinates")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_coordinates()) 
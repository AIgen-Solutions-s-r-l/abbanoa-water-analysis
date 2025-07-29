#!/usr/bin/env python3
"""
Add realistic geographical coordinates to water infrastructure nodes in Sardinia
"""
import asyncpg
import asyncio
import random
from typing import List, Tuple

# Sardinian regions with realistic coordinate ranges
SARDINIA_REGIONS = {
    'Cagliari': {
        'center': (39.2238, 9.1217),
        'radius': 0.15,  # ~15km radius
        'nodes': ['DIST_001', 'NODE_287156', 'NODE_288400']
    },
    'Sassari': {
        'center': (40.7259, 8.5606),
        'radius': 0.12,
        'nodes': ['NODE_215542', 'NODE_281492']
    },
    'Nuoro': {
        'center': (40.3211, 9.3307),
        'radius': 0.10,
        'nodes': ['NODE_288399', 'SERBATOIO_001']
    },
    'Oristano': {
        'center': (39.9032, 8.5869),
        'radius': 0.08,
        'nodes': ['ZONA_IND_002', 'ZONA_RES_003']
    },
    'Quartu Sant\'Elena': {
        'center': (39.2321, 9.1841),
        'radius': 0.05,
        'nodes': []  # Will assign remaining nodes
    }
}

def generate_coordinates_around(center: Tuple[float, float], radius: float) -> Tuple[float, float]:
    """Generate random coordinates around a center point within a radius"""
    lat, lon = center
    # Generate random offset
    angle = random.uniform(0, 2 * 3.14159)
    distance = random.uniform(0, radius)
    
    # Apply offset
    new_lat = lat + (distance * random.uniform(0.8, 1.2))
    new_lon = lon + (distance * random.uniform(0.8, 1.2) * (1 if random.random() > 0.5 else -1))
    
    return round(new_lat, 6), round(new_lon, 6)

async def update_node_coordinates():
    """Update node coordinates in the database"""
    # Database connection
    conn = await asyncpg.connect(
        host='localhost',
        port=5434,
        database='abbanoa_processing',
        user='abbanoa_user',
        password='abbanoa_secure_pass'
    )
    
    try:
        # Get all nodes
        nodes = await conn.fetch("""
            SELECT node_id, node_name, location_name 
            FROM water_infrastructure.nodes
            WHERE is_active = true
        """)
        
        print(f"📍 Found {len(nodes)} active nodes to update")
        
        # Create a mapping of nodes to regions
        node_assignments = {}
        unassigned_nodes = []
        
        for node in nodes:
            node_id = node['node_id']
            assigned = False
            
            # Check if node is pre-assigned to a region
            for region, data in SARDINIA_REGIONS.items():
                if node_id in data['nodes']:
                    node_assignments[node_id] = region
                    assigned = True
                    break
            
            if not assigned:
                unassigned_nodes.append(node_id)
        
        # Assign unassigned nodes to Quartu Sant'Elena and other regions
        for i, node_id in enumerate(unassigned_nodes):
            if i < len(unassigned_nodes) // 2:
                node_assignments[node_id] = 'Quartu Sant\'Elena'
            else:
                # Distribute among other regions
                regions = list(SARDINIA_REGIONS.keys())
                node_assignments[node_id] = regions[i % len(regions)]
        
        # Update coordinates for each node
        updated_count = 0
        for node in nodes:
            node_id = node['node_id']
            region = node_assignments.get(node_id, 'Cagliari')
            
            # Generate coordinates
            center = SARDINIA_REGIONS[region]['center']
            radius = SARDINIA_REGIONS[region]['radius']
            lat, lon = generate_coordinates_around(center, radius)
            
            # Update database
            await conn.execute("""
                UPDATE water_infrastructure.nodes
                SET latitude = $1, 
                    longitude = $2,
                    location_name = $3,
                    updated_at = CURRENT_TIMESTAMP
                WHERE node_id = $4
            """, lat, lon, region, node_id)
            
            updated_count += 1
            print(f"  ✓ {node['node_name']} → {region} ({lat}, {lon})")
        
        print(f"\n✅ Successfully updated {updated_count} nodes with coordinates")
        
        # Verify the update
        verify = await conn.fetch("""
            SELECT location_name, COUNT(*) as count,
                   AVG(latitude) as avg_lat, AVG(longitude) as avg_lon
            FROM water_infrastructure.nodes
            WHERE latitude IS NOT NULL
            GROUP BY location_name
            ORDER BY location_name
        """)
        
        print("\n📊 Distribution by region:")
        for row in verify:
            print(f"  - {row['location_name']}: {row['count']} nodes")
            print(f"    Center: ({row['avg_lat']:.4f}, {row['avg_lon']:.4f})")
        
    finally:
        await conn.close()

async def add_pipe_connections():
    """Add connections between nodes to represent pipes"""
    conn = await asyncpg.connect(
        host='localhost',
        port=5434,
        database='abbanoa_processing',
        user='abbanoa_user',
        password='abbanoa_secure_pass'
    )
    
    try:
        # Create pipe connections table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS water_infrastructure.pipe_connections (
                id SERIAL PRIMARY KEY,
                from_node_id VARCHAR(50) REFERENCES water_infrastructure.nodes(node_id),
                to_node_id VARCHAR(50) REFERENCES water_infrastructure.nodes(node_id),
                pipe_diameter_mm INTEGER,
                pipe_material VARCHAR(50),
                pipe_length_m DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_node_id, to_node_id)
            )
        """)
        
        # Get nodes by location
        nodes_by_location = {}
        nodes = await conn.fetch("""
            SELECT node_id, location_name, latitude, longitude
            FROM water_infrastructure.nodes
            WHERE latitude IS NOT NULL
        """)
        
        for node in nodes:
            loc = node['location_name']
            if loc not in nodes_by_location:
                nodes_by_location[loc] = []
            nodes_by_location[loc].append(node)
        
        # Create connections within each location
        connection_count = 0
        for location, location_nodes in nodes_by_location.items():
            # Connect nodes in a network pattern
            for i in range(len(location_nodes) - 1):
                from_node = location_nodes[i]
                to_node = location_nodes[i + 1]
                
                # Calculate approximate distance
                lat_diff = float(abs(from_node['latitude'] - to_node['latitude']))
                lon_diff = float(abs(from_node['longitude'] - to_node['longitude']))
                distance_km = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km conversion
                
                pipe_diameter = random.choice([200, 300, 400, 500, 600])
                pipe_material = random.choice(['Steel', 'PVC', 'HDPE', 'Cast Iron'])
                
                try:
                    await conn.execute("""
                        INSERT INTO water_infrastructure.pipe_connections
                        (from_node_id, to_node_id, pipe_diameter_mm, pipe_material, pipe_length_m)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (from_node_id, to_node_id) DO NOTHING
                    """, from_node['node_id'], to_node['node_id'], 
                        pipe_diameter, pipe_material, distance_km * 1000)
                    connection_count += 1
                except Exception as e:
                    print(f"  ⚠️  Error connecting {from_node['node_id']} to {to_node['node_id']}: {e}")
        
        print(f"\n🔗 Created {connection_count} pipe connections")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🗺️ Sardinian Water Infrastructure Coordinate Generator")
    print("=" * 50)
    
    asyncio.run(update_node_coordinates())
    asyncio.run(add_pipe_connections())
    
    print("\n✨ Coordinates and connections added successfully!")
    print("   Your nodes are now ready for the interactive map!") 
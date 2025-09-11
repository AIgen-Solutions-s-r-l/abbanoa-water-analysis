"""Network topology endpoints for infrastructure hierarchy visualization."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import asyncpg

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/network",
    tags=["network-topology"]
)


async def get_db_connection():
    """Get database connection from app state."""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from src.presentation.api.app_postgres import pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    return pool


@router.get("/topology")
async def get_network_topology(
    include_metrics: bool = False,
    pool: asyncpg.Pool = Depends(get_db_connection)
) -> Dict[str, Any]:
    """
    Get the complete network topology with nodes and connections.
    
    Returns hierarchical structure of water infrastructure network.
    """
    try:
        async with pool.acquire() as conn:
            # Get all nodes with their types and locations
            nodes_query = """
            SELECT 
                node_id,
                node_name,
                node_type,
                latitude,
                longitude,
                location_name,
                is_active,
                metadata
            FROM water_infrastructure.nodes
            WHERE is_active = true
            ORDER BY 
                CASE node_type 
                    WHEN 'source' THEN 1
                    WHEN 'reservoir' THEN 2
                    WHEN 'hub' THEN 3
                    WHEN 'junction' THEN 4
                    WHEN 'district' THEN 5
                    ELSE 6
                END,
                node_id
            """
            nodes = await conn.fetch(nodes_query)
            
            # Get all network connections
            connections_query = """
            SELECT 
                nc.source_node_id,
                nc.target_node_id,
                nc.connection_type,
                nc.flow_direction,
                nc.diameter_mm,
                nc.length_m,
                nc.material,
                nc.status
            FROM water_infrastructure.network_connections nc
            WHERE nc.status = 'active'
            """
            connections = await conn.fetch(connections_query)
            
            # Get metrics if requested
            metrics = {}
            if include_metrics:
                metrics_query = """
                SELECT 
                    node_id,
                    AVG(flow_rate) as avg_flow,
                    AVG(pressure) as avg_pressure,
                    MAX(timestamp) as last_reading
                FROM water_infrastructure.sensor_readings
                WHERE timestamp > NOW() - INTERVAL '1 hour'
                GROUP BY node_id
                """
                metrics_data = await conn.fetch(metrics_query)
                metrics = {m['node_id']: {
                    'avg_flow': float(m['avg_flow']) if m['avg_flow'] else 0,
                    'avg_pressure': float(m['avg_pressure']) if m['avg_pressure'] else 0,
                    'last_reading': m['last_reading'].isoformat() if m['last_reading'] else None
                } for m in metrics_data}
            
            # Format nodes by type for hierarchy
            nodes_by_type = {}
            for node in nodes:
                node_type = node['node_type']
                if node_type not in nodes_by_type:
                    nodes_by_type[node_type] = []
                
                node_data = {
                    'id': node['node_id'],
                    'name': node['node_name'],
                    'type': node_type,
                    'location': {
                        'lat': float(node['latitude']) if node['latitude'] else None,
                        'lng': float(node['longitude']) if node['longitude'] else None,
                        'name': node['location_name']
                    },
                    'active': node['is_active'],
                    'metadata': dict(node['metadata']) if node['metadata'] else {}
                }
                
                # Add metrics if available
                if node['node_id'] in metrics:
                    node_data['metrics'] = metrics[node['node_id']]
                
                nodes_by_type[node_type].append(node_data)
            
            # Format connections
            formatted_connections = []
            for conn in connections:
                formatted_connections.append({
                    'source': conn['source_node_id'],
                    'target': conn['target_node_id'],
                    'type': conn['connection_type'],
                    'direction': conn['flow_direction'],
                    'properties': {
                        'diameter_mm': conn['diameter_mm'],
                        'length_m': float(conn['length_m']) if conn['length_m'] else None,
                        'material': conn['material'],
                        'status': conn['status']
                    }
                })
            
            return {
                'topology': {
                    'nodes': nodes_by_type,
                    'connections': formatted_connections,
                    'summary': {
                        'total_nodes': len(nodes),
                        'total_connections': len(connections),
                        'node_types': list(nodes_by_type.keys()),
                        'active_nodes': sum(1 for n in nodes if n['is_active'])
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error fetching network topology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching network topology: {str(e)}")


@router.get("/topology/hierarchy")
async def get_network_hierarchy(
    pool: asyncpg.Pool = Depends(get_db_connection)
) -> Dict[str, Any]:
    """
    Get network topology in hierarchical tree structure.
    
    Returns tree structure showing flow from sources to end districts.
    """
    try:
        async with pool.acquire() as conn:
            # Get all nodes
            nodes_query = """
            SELECT node_id, node_name, node_type, latitude, longitude
            FROM water_infrastructure.nodes
            WHERE is_active = true
            """
            nodes = await conn.fetch(nodes_query)
            nodes_dict = {n['node_id']: dict(n) for n in nodes}
            
            # Get all connections
            connections_query = """
            SELECT source_node_id, target_node_id, connection_type, flow_direction
            FROM water_infrastructure.network_connections
            WHERE status = 'active'
            """
            connections = await conn.fetch(connections_query)
            
            # Build adjacency list
            graph = {}
            reverse_graph = {}
            for conn in connections:
                source = conn['source_node_id']
                target = conn['target_node_id']
                
                if source not in graph:
                    graph[source] = []
                graph[source].append(target)
                
                if target not in reverse_graph:
                    reverse_graph[target] = []
                reverse_graph[target].append(source)
                
                # Handle bidirectional connections
                if conn['flow_direction'] == 'bidirectional':
                    if target not in graph:
                        graph[target] = []
                    graph[target].append(source)
                    
                    if source not in reverse_graph:
                        reverse_graph[source] = []
                    reverse_graph[source].append(target)
            
            # Find root nodes (sources with no incoming connections)
            root_nodes = []
            for node_id, node_data in nodes_dict.items():
                if node_data['node_type'] == 'source' and node_id not in reverse_graph:
                    root_nodes.append(node_id)
                elif node_data['node_type'] == 'source' and all(
                    nodes_dict.get(parent, {}).get('node_type') != 'source' 
                    for parent in reverse_graph.get(node_id, [])
                ):
                    root_nodes.append(node_id)
            
            # If no pure sources found, use nodes with type 'source'
            if not root_nodes:
                root_nodes = [n['node_id'] for n in nodes if n['node_type'] == 'source']
            
            # Build hierarchy tree
            def build_tree(node_id, visited=None):
                if visited is None:
                    visited = set()
                
                if node_id in visited:
                    return None
                
                visited.add(node_id)
                node_data = nodes_dict.get(node_id, {})
                
                tree_node = {
                    'id': node_id,
                    'name': node_data.get('node_name', node_id),
                    'type': node_data.get('node_type', 'unknown'),
                    'location': {
                        'lat': float(node_data['latitude']) if node_data.get('latitude') else None,
                        'lng': float(node_data['longitude']) if node_data.get('longitude') else None
                    },
                    'children': []
                }
                
                # Add children
                for child_id in graph.get(node_id, []):
                    child_tree = build_tree(child_id, visited.copy())
                    if child_tree:
                        tree_node['children'].append(child_tree)
                
                return tree_node
            
            # Build hierarchy from each root
            hierarchy = []
            for root in root_nodes:
                tree = build_tree(root)
                if tree:
                    hierarchy.append(tree)
            
            return {
                'hierarchy': hierarchy,
                'statistics': {
                    'total_nodes': len(nodes),
                    'root_nodes': len(root_nodes),
                    'max_depth': calculate_max_depth(hierarchy)
                },
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error building network hierarchy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error building network hierarchy: {str(e)}")


def calculate_max_depth(hierarchy: List[Dict], depth: int = 0) -> int:
    """Calculate maximum depth of hierarchy tree."""
    if not hierarchy:
        return depth
    
    max_child_depth = depth
    for node in hierarchy:
        if 'children' in node and node['children']:
            child_depth = calculate_max_depth(node['children'], depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
    
    return max_child_depth


@router.get("/topology/flow-path/{node_id}")
async def get_flow_path(
    node_id: str,
    pool: asyncpg.Pool = Depends(get_db_connection)
) -> Dict[str, Any]:
    """
    Get the flow path from sources to a specific node.
    
    Returns all possible paths water can take to reach the specified node.
    """
    try:
        async with pool.acquire() as conn:
            # Verify node exists
            node = await conn.fetchrow(
                "SELECT * FROM water_infrastructure.nodes WHERE node_id = $1",
                node_id
            )
            if not node:
                raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
            
            # Get all connections
            connections_query = """
            SELECT source_node_id, target_node_id, flow_direction
            FROM water_infrastructure.network_connections
            WHERE status = 'active'
            """
            connections = await conn.fetch(connections_query)
            
            # Build reverse graph (from target to source)
            reverse_graph = {}
            for conn in connections:
                target = conn['target_node_id']
                source = conn['source_node_id']
                
                if target not in reverse_graph:
                    reverse_graph[target] = []
                reverse_graph[target].append(source)
                
                # Handle bidirectional
                if conn['flow_direction'] == 'bidirectional':
                    if source not in reverse_graph:
                        reverse_graph[source] = []
                    reverse_graph[source].append(target)
            
            # Find all paths from sources to the target node
            def find_paths(current, visited=None):
                if visited is None:
                    visited = set()
                
                if current in visited:
                    return []
                
                visited.add(current)
                
                # Check if this is a source node
                node_data = await conn.fetchrow(
                    "SELECT node_type FROM water_infrastructure.nodes WHERE node_id = $1",
                    current
                )
                if node_data and node_data['node_type'] == 'source':
                    return [[current]]
                
                # Find paths through parents
                paths = []
                for parent in reverse_graph.get(current, []):
                    parent_paths = find_paths(parent, visited.copy())
                    for path in parent_paths:
                        paths.append(path + [current])
                
                return paths
            
            paths = find_paths(node_id)
            
            # Get node details for each path
            detailed_paths = []
            for path in paths:
                path_details = []
                for node_in_path in path:
                    node_info = await conn.fetchrow(
                        "SELECT node_id, node_name, node_type FROM water_infrastructure.nodes WHERE node_id = $1",
                        node_in_path
                    )
                    if node_info:
                        path_details.append({
                            'id': node_info['node_id'],
                            'name': node_info['node_name'],
                            'type': node_info['node_type']
                        })
                detailed_paths.append(path_details)
            
            return {
                'target_node': {
                    'id': node['node_id'],
                    'name': node['node_name'],
                    'type': node['node_type']
                },
                'flow_paths': detailed_paths,
                'path_count': len(detailed_paths),
                'timestamp': datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding flow paths: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding flow paths: {str(e)}")
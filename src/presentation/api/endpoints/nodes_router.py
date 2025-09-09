"""Nodes API endpoints."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import asyncpg
import os
import logging

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/v1", tags=["nodes"])
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'abbanoa_processing'),
    'user': os.getenv('POSTGRES_USER', 'abbanoa_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'abbanoa_secure_pass')
}


async def get_db_connection():
    """Get database connection."""
    return await asyncpg.connect(**DB_CONFIG)


@router.get("/nodes")
async def get_nodes(
    status: Optional[str] = Query(None, description="Filter by status"),
    node_type: Optional[str] = Query(None, description="Filter by node type")
) -> Dict[str, Any]:
    """Get list of network nodes with their details."""
    try:
        conn = await get_db_connection()
        
        # Build the query with filters
        query = """
            SELECT 
                n.node_id,
                n.node_name,
                n.node_type,
                n.location_lat,
                n.location_lng,
                n.status,
                n.capacity,
                n.current_flow,
                n.last_reading,
                n.created_at,
                n.updated_at
            FROM water_infrastructure.nodes n
            WHERE 1=1
        """
        
        params = []
        param_count = 0
        
        if status is not None:
            param_count += 1
            query += f" AND n.status = ${param_count}"
            params.append(str(status))
            
        if node_type is not None:
            param_count += 1
            query += f" AND n.node_type = ${param_count}"
            params.append(str(node_type))
            
        query += " ORDER BY n.node_name"
        
        nodes_data = await conn.fetch(query, *params)
        
        # Transform nodes data
        nodes = []
        total_capacity = 0
        total_current_flow = 0
        status_counts = {}
        
        for row in nodes_data:
            node = {
                "node_id": row['node_id'],
                "node_name": row['node_name'],
                "node_type": row['node_type'],
                "location": {
                    "lat": float(row['location_lat']) if row['location_lat'] else None,
                    "lng": float(row['location_lng']) if row['location_lng'] else None
                },
                "status": row['status'],
                "capacity": float(row['capacity']) if row['capacity'] else 0.0,
                "current_flow": float(row['current_flow']) if row['current_flow'] else 0.0,
                "last_reading": row['last_reading'].isoformat() if row['last_reading'] else None,
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
            }
            nodes.append(node)
            
            # Calculate summary statistics
            total_capacity += node["capacity"]
            total_current_flow += node["current_flow"]
            
            # Count by status
            node_status = node["status"]
            if node_status in status_counts:
                status_counts[node_status] += 1
            else:
                status_counts[node_status] = 1
        
        await conn.close()
        
        # Build summary
        summary = {
            "total_nodes": len(nodes),
            "active_nodes": status_counts.get('active', 0),
            "maintenance_nodes": status_counts.get('maintenance', 0),
            "offline_nodes": status_counts.get('offline', 0),
            "total_capacity": total_capacity,
            "total_current_flow": total_current_flow,
            "capacity_utilization": round((total_current_flow / total_capacity * 100), 2) if total_capacity > 0 else 0.0,
            "status_breakdown": status_counts
        }
        
        return {
            "nodes": nodes,
            "summary": summary,
            "metadata": {
                "query_timestamp": datetime.now(timezone.utc).isoformat(),
                "filters_applied": {
                    "status": status,
                    "node_type": node_type
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}")
async def get_node_details(node_id: str) -> Dict[str, Any]:
    """Get detailed information for a specific node."""
    try:
        conn = await get_db_connection()
        
        # Get node details
        node_query = """
            SELECT 
                n.node_id,
                n.node_name,
                n.node_type,
                n.location_lat,
                n.location_lng,
                n.status,
                n.capacity,
                n.current_flow,
                n.last_reading,
                n.created_at,
                n.updated_at,
                n.description,
                n.maintenance_schedule,
                n.installation_date
            FROM water_infrastructure.nodes n
            WHERE n.node_id = $1
        """
        
        node_result = await conn.fetchrow(node_query, node_id)
        
        if not node_result:
            await conn.close()
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        
        # Get recent sensor readings for this node
        readings_query = """
            SELECT 
                timestamp,
                pressure,
                flow_rate,
                temperature,
                quality_score
            FROM water_infrastructure.sensor_readings
            WHERE node_id = $1
            ORDER BY timestamp DESC
            LIMIT 24
        """
        
        readings_data = await conn.fetch(readings_query, node_id)
        
        await conn.close()
        
        # Build node details
        node = {
            "node_id": node_result['node_id'],
            "node_name": node_result['node_name'],
            "node_type": node_result['node_type'],
            "location": {
                "lat": float(node_result['location_lat']) if node_result['location_lat'] else None,
                "lng": float(node_result['location_lng']) if node_result['location_lng'] else None
            },
            "status": node_result['status'],
            "capacity": float(node_result['capacity']) if node_result['capacity'] else 0.0,
            "current_flow": float(node_result['current_flow']) if node_result['current_flow'] else 0.0,
            "last_reading": node_result['last_reading'].isoformat() if node_result['last_reading'] else None,
            "description": node_result['description'],
            "maintenance_schedule": node_result['maintenance_schedule'],
            "installation_date": node_result['installation_date'].isoformat() if node_result['installation_date'] else None,
            "created_at": node_result['created_at'].isoformat() if node_result['created_at'] else None,
            "updated_at": node_result['updated_at'].isoformat() if node_result['updated_at'] else None
        }
        
        # Process recent readings
        recent_readings = []
        for reading in readings_data:
            recent_readings.append({
                "timestamp": reading['timestamp'].isoformat(),
                "pressure": float(reading['pressure']) if reading['pressure'] else None,
                "flow_rate": float(reading['flow_rate']) if reading['flow_rate'] else None,
                "temperature": float(reading['temperature']) if reading['temperature'] else None,
                "quality_score": float(reading['quality_score']) if reading['quality_score'] else None
            })
        
        return {
            "node": node,
            "recent_readings": recent_readings,
            "metadata": {
                "query_timestamp": datetime.now(timezone.utc).isoformat(),
                "readings_count": len(recent_readings)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching node details for {node_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
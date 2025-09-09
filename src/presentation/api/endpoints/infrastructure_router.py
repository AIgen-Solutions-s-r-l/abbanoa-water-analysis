"""Infrastructure data API endpoints for map and network visualization."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import asyncpg
import os
import logging

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/infrastructure", tags=["infrastructure"])

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


@router.get("/map-data")
async def get_infrastructure_map_data() -> Dict[str, Any]:
    """Get infrastructure data for map visualization."""
    try:
        conn = await get_db_connection()
        
        # Get nodes with latest readings
        nodes_query = """
            SELECT DISTINCT ON (n.node_id)
                n.node_id,
                n.node_name,
                n.node_type,
                n.latitude,
                n.longitude,
                n.is_active,
                COALESCE(sr.flow_rate, 0.0) as flow_rate,
                COALESCE(sr.pressure, 0.0) as pressure,
                sr.timestamp as last_reading,
                EXISTS(
                    SELECT 1 FROM water_infrastructure.anomalies a 
                    WHERE a.node_id = n.node_id 
                    AND a.timestamp > NOW() - INTERVAL '24 hours'
                    AND a.resolved_at IS NULL
                ) as has_anomaly
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON sr.node_id = n.node_id
            WHERE n.is_active = true
            ORDER BY n.node_id, sr.timestamp DESC NULLS LAST
        """
        
        nodes_data = await conn.fetch(nodes_query)
        
        # Transform nodes data
        nodes = []
        total_flow = 0.0
        total_pressure = 0.0
        active_nodes = 0
        
        for row in nodes_data:
            flow_rate = float(row['flow_rate']) if row['flow_rate'] else 0.0
            pressure = float(row['pressure']) if row['pressure'] else 0.0
            
            node = {
                "id": row['node_id'],
                "name": row['node_name'],
                "type": row['node_type'] or "distribution",
                "latitude": float(row['latitude']) if row['latitude'] else 40.9179,
                "longitude": float(row['longitude']) if row['longitude'] else 9.4944,
                "status": "active" if row['is_active'] else "inactive",
                "flow_rate": flow_rate,
                "pressure": pressure,
                "has_anomaly": row['has_anomaly'],
                "last_reading": row['last_reading'].isoformat() if row['last_reading'] else None
            }
            nodes.append(node)
            
            if flow_rate > 0 or pressure > 0:
                active_nodes += 1
                total_flow += flow_rate
                total_pressure += pressure
        
        # Calculate network metrics
        avg_pressure = total_pressure / active_nodes if active_nodes > 0 else 0.0
        network_health = min(95.0, (avg_pressure / 3.0) * 100) if avg_pressure > 0 else 0.0
        
        # Get active alerts count
        alerts_query = """
            SELECT COUNT(*) as alert_count
            FROM water_infrastructure.anomalies
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            AND resolved_at IS NULL
        """
        alerts_result = await conn.fetchrow(alerts_query)
        active_alerts = alerts_result['alert_count'] if alerts_result else 0
        
        # Get pressure zones if available
        zones_query = """
            SELECT 
                zone_id,
                zone_name,
                COUNT(DISTINCT node_id) as node_count,
                AVG(efficiency) as avg_efficiency
            FROM water_infrastructure.pressure_zones
            WHERE is_active = true
            GROUP BY zone_id, zone_name
        """
        
        zones = []
        try:
            zones_data = await conn.fetch(zones_query)
            for row in zones_data:
                zones.append({
                    "id": row['zone_id'],
                    "name": row['zone_name'],
                    "node_count": row['node_count'],
                    "efficiency": float(row['avg_efficiency']) if row['avg_efficiency'] else 95.0
                })
        except Exception as e:
            # Table might not exist yet
            logger.warning(f"Could not fetch pressure zones: {e}")
            zones = [
                {
                    "id": "default_zone",
                    "name": "Main Network",
                    "node_count": len(nodes),
                    "efficiency": network_health
                }
            ]
        
        await conn.close()
        
        return {
            "network_health": network_health,
            "total_flow": total_flow,
            "avg_pressure": avg_pressure,
            "active_alerts": active_alerts,
            "nodes": nodes,
            "pipes": [],  # To be implemented when pipe data is available
            "zones": zones,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching infrastructure data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}")
async def get_node_details(node_id: str) -> Dict[str, Any]:
    """Get detailed information for a specific node."""
    try:
        conn = await get_db_connection()
        
        # Get node details with latest readings
        node_query = """
            SELECT 
                n.node_id,
                n.node_name,
                n.node_type,
                n.latitude,
                n.longitude,
                n.is_active,
                n.description,
                sr.flow_rate,
                sr.pressure,
                sr.temperature,
                sr.quality_score,
                sr.timestamp as last_reading
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON sr.node_id = n.node_id
            WHERE n.node_id = $1
            ORDER BY sr.timestamp DESC
            LIMIT 1
        """
        
        node_data = await conn.fetchrow(node_query, node_id)
        
        if not node_data:
            await conn.close()
            raise HTTPException(status_code=404, detail="Node not found")
        
        # Get recent anomalies
        anomalies_query = """
            SELECT 
                anomaly_id,
                anomaly_type,
                severity,
                description,
                timestamp,
                resolved_at
            FROM water_infrastructure.anomalies
            WHERE node_id = $1
            AND timestamp > NOW() - INTERVAL '7 days'
            ORDER BY timestamp DESC
            LIMIT 10
        """
        
        anomalies_data = await conn.fetch(anomalies_query, node_id)
        
        anomalies = []
        for row in anomalies_data:
            anomalies.append({
                "id": row['anomaly_id'],
                "type": row['anomaly_type'],
                "severity": row['severity'],
                "description": row['description'],
                "timestamp": row['timestamp'].isoformat(),
                "resolved": row['resolved_at'] is not None
            })
        
        await conn.close()
        
        return {
            "id": node_data['node_id'],
            "name": node_data['node_name'],
            "type": node_data['node_type'] or "distribution",
            "location": {
                "latitude": float(node_data['latitude']) if node_data['latitude'] else 40.9179,
                "longitude": float(node_data['longitude']) if node_data['longitude'] else 9.4944
            },
            "status": "active" if node_data['is_active'] else "inactive",
            "description": node_data['description'],
            "current_readings": {
                "flow_rate": float(node_data['flow_rate']) if node_data['flow_rate'] else 0.0,
                "pressure": float(node_data['pressure']) if node_data['pressure'] else 0.0,
                "temperature": float(node_data['temperature']) if node_data['temperature'] else None,
                "quality_score": float(node_data['quality_score']) if node_data['quality_score'] else None,
                "timestamp": node_data['last_reading'].isoformat() if node_data['last_reading'] else None
            },
            "recent_anomalies": anomalies
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching node details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-summary")
async def get_network_summary() -> Dict[str, Any]:
    """Get network summary statistics."""
    try:
        conn = await get_db_connection()
        
        # Get network statistics
        stats_query = """
            SELECT 
                COUNT(DISTINCT n.node_id) as total_nodes,
                COUNT(DISTINCT CASE WHEN n.is_active THEN n.node_id END) as active_nodes,
                COUNT(DISTINCT sr.node_id) as nodes_with_readings,
                AVG(sr.flow_rate) as avg_flow_rate,
                AVG(sr.pressure) as avg_pressure,
                MIN(sr.timestamp) as oldest_reading,
                MAX(sr.timestamp) as latest_reading
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON sr.node_id = n.node_id
                AND sr.timestamp > NOW() - INTERVAL '24 hours'
        """
        
        stats = await conn.fetchrow(stats_query)
        
        # Get anomaly statistics
        anomaly_query = """
            SELECT 
                COUNT(*) as total_anomalies,
                COUNT(CASE WHEN resolved_at IS NULL THEN 1 END) as active_anomalies,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_anomalies
            FROM water_infrastructure.anomalies
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """
        
        anomaly_stats = await conn.fetchrow(anomaly_query)
        
        await conn.close()
        
        return {
            "network": {
                "total_nodes": stats['total_nodes'] or 0,
                "active_nodes": stats['active_nodes'] or 0,
                "nodes_with_readings": stats['nodes_with_readings'] or 0,
                "avg_flow_rate": float(stats['avg_flow_rate']) if stats['avg_flow_rate'] else 0.0,
                "avg_pressure": float(stats['avg_pressure']) if stats['avg_pressure'] else 0.0,
                "data_range": {
                    "oldest": stats['oldest_reading'].isoformat() if stats['oldest_reading'] else None,
                    "latest": stats['latest_reading'].isoformat() if stats['latest_reading'] else None
                }
            },
            "anomalies": {
                "total_24h": anomaly_stats['total_anomalies'] or 0,
                "active": anomaly_stats['active_anomalies'] or 0,
                "critical": anomaly_stats['critical_anomalies'] or 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching network summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
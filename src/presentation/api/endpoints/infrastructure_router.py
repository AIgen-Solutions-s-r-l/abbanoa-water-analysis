"""Infrastructure data API endpoints for map and network visualization."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import asyncpg
import os
import logging
import random

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
    try:
        return await asyncpg.connect(**DB_CONFIG)
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        return None


def get_mock_infrastructure_data() -> Dict[str, Any]:
    """Generate mock infrastructure data for testing."""
    # Fixed real-world coordinates for water infrastructure nodes
    # Based on actual Sardinian water network topology
    
    FIXED_NODE_COORDINATES = {
        # SELARGIUS nodes - distributed across the municipality
        "SEL_001": {"lat": 39.2599, "lon": 9.1628, "name": "SELARGIUS_1", "type": "source"},
        "SEL_002": {"lat": 39.2612, "lon": 9.1645, "name": "SELARGIUS_2", "type": "distribution"},
        "SEL_003": {"lat": 39.2585, "lon": 9.1612, "name": "SELARGIUS_3", "type": "junction"},
        "SEL_004": {"lat": 39.2603, "lon": 9.1598, "name": "SELARGIUS_4", "type": "junction"},
        "SEL_005": {"lat": 39.2621, "lon": 9.1655, "name": "SELARGIUS_5", "type": "distribution"},
        "SEL_006": {"lat": 39.2577, "lon": 9.1635, "name": "SELARGIUS_6", "type": "storage"},
        
        # QUARTUCCIU nodes - distributed across the municipality
        "QUA_001": {"lat": 39.2474, "lon": 9.1844, "name": "QUARTUCCIU_1", "type": "source"},
        "QUA_002": {"lat": 39.2488, "lon": 9.1862, "name": "QUARTUCCIU_2", "type": "distribution"},
        "QUA_003": {"lat": 39.2461, "lon": 9.1828, "name": "QUARTUCCIU_3", "type": "junction"},
        "QUA_004": {"lat": 39.2495, "lon": 9.1855, "name": "QUARTUCCIU_4", "type": "distribution"},
        "QUA_005": {"lat": 39.2468, "lon": 9.1875, "name": "QUARTUCCIU_5", "type": "storage"},
        
        # CAGLIARI main distribution nodes
        "DIST_001": {"lat": 39.2238, "lon": 9.1217, "name": "Cagliari DIST_001", "type": "distribution"},
        "NODE_287156": {"lat": 39.2251, "lon": 9.1198, "name": "Cagliari NODE_287156", "type": "junction"},
        "NODE_288400": {"lat": 39.2225, "lon": 9.1234, "name": "Cagliari NODE_288400", "type": "junction"},
        "SERBATOIO_001": {"lat": 39.2264, "lon": 9.1185, "name": "Cagliari SERBATOIO_001", "type": "storage"},
    }
    
    nodes = []
    
    # Create nodes with fixed coordinates
    for node_id, node_data in FIXED_NODE_COORDINATES.items():
        # Generate varying operational data (flow and pressure change, positions don't)
        flow_rate = random.uniform(15, 60) if node_id.startswith("SEL") else \
                   random.uniform(12, 55) if node_id.startswith("QUA") else \
                   random.uniform(20, 80)
        
        pressure = random.uniform(3.0, 5.0) if node_id.startswith("SEL") else \
                  random.uniform(2.8, 4.8) if node_id.startswith("QUA") else \
                  random.uniform(3.5, 5.5)
        
        node = {
            "id": node_id,
            "name": node_data["name"],
            "type": node_data["type"],
            "latitude": node_data["lat"],
            "longitude": node_data["lon"],
            "status": "active",
            "flow_rate": flow_rate,
            "pressure": pressure,
            "has_anomaly": random.random() < 0.10,
            "last_reading": datetime.now(timezone.utc).isoformat()
        }
        nodes.append(node)
    
    # Calculate metrics
    total_flow = sum(n['flow_rate'] for n in nodes)
    avg_pressure = sum(n['pressure'] for n in nodes) / len(nodes)
    network_health = min(95.0, (avg_pressure / 3.0) * 100)
    active_alerts = sum(1 for n in nodes if n['has_anomaly'])
    
    # Fixed pipe connections based on real network topology
    FIXED_PIPE_CONNECTIONS = [
        # Selargius internal network
        {"from": "SEL_001", "to": "SEL_002", "diameter": 300, "material": "PVC"},
        {"from": "SEL_002", "to": "SEL_003", "diameter": 250, "material": "HDPE"},
        {"from": "SEL_003", "to": "SEL_004", "diameter": 250, "material": "PVC"},
        {"from": "SEL_004", "to": "SEL_005", "diameter": 300, "material": "HDPE"},
        {"from": "SEL_005", "to": "SEL_006", "diameter": 350, "material": "PVC"},
        
        # Quartucciu internal network
        {"from": "QUA_001", "to": "QUA_002", "diameter": 280, "material": "PVC"},
        {"from": "QUA_002", "to": "QUA_003", "diameter": 250, "material": "Steel"},
        {"from": "QUA_003", "to": "QUA_004", "diameter": 280, "material": "PVC"},
        {"from": "QUA_004", "to": "QUA_005", "diameter": 320, "material": "HDPE"},
        
        # Cagliari main network
        {"from": "DIST_001", "to": "NODE_287156", "diameter": 500, "material": "Steel"},
        {"from": "NODE_287156", "to": "NODE_288400", "diameter": 450, "material": "Cast Iron"},
        {"from": "NODE_288400", "to": "SERBATOIO_001", "diameter": 500, "material": "Steel"},
        
        # Inter-network connections
        {"from": "DIST_001", "to": "SEL_001", "diameter": 400, "material": "Steel"},
        {"from": "NODE_288400", "to": "QUA_001", "diameter": 380, "material": "Steel"},
    ]
    
    pipes = []
    nodes_dict = {n['id']: n for n in nodes}
    
    for i, connection in enumerate(FIXED_PIPE_CONNECTIONS):
        from_node = nodes_dict.get(connection["from"])
        to_node = nodes_dict.get(connection["to"])
        
        if from_node and to_node:
            # Generate varying flow rate (only this changes, not the connections)
            flow_rate = random.uniform(15, 50)
            
            pipes.append({
                "pipe_id": f"PIPE_{i:03d}",
                "from_node_id": from_node['id'],
                "to_node_id": to_node['id'],
                "from_lat": from_node['latitude'],
                "from_lon": from_node['longitude'],
                "to_lat": to_node['latitude'],
                "to_lon": to_node['longitude'],
                "diameter_mm": connection["diameter"],
                "material": connection["material"],
                "flow_rate": flow_rate
            })
    
    return {
        "network_health": network_health,
        "total_flow": total_flow,
        "avg_pressure": avg_pressure,
        "active_alerts": active_alerts,
        "nodes": nodes,
        "pipes": pipes,
        "zones": [
            {
                "id": "zone_central",
                "name": "Central District",
                "node_count": 5,
                "efficiency": 92.5
            },
            {
                "id": "zone_north",
                "name": "North District",
                "node_count": 5,
                "efficiency": 88.3
            },
            {
                "id": "zone_south",
                "name": "South District",
                "node_count": 5,
                "efficiency": 94.1
            }
        ],
        "last_updated": datetime.now(timezone.utc).isoformat()
    }


@router.get("/map-data")
async def get_infrastructure_map_data() -> Dict[str, Any]:
    """Get infrastructure data for map visualization."""
    conn = None
    try:
        conn = await get_db_connection()
        
        # If no database connection, return error
        if conn is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Unable to fetch infrastructure data."
            )
        
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
        
        if conn:
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching infrastructure data: {e}")
        # Return error instead of mock data
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch infrastructure data: {str(e)}"
        )
    finally:
        if conn:
            try:
                await conn.close()
            except:
                pass


@router.get("/nodes/{node_id}")
async def get_node_details(node_id: str) -> Dict[str, Any]:
    """Get detailed information for a specific node."""
    conn = None
    try:
        conn = await get_db_connection()
        
        # If no database connection, return error
        if conn is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Unable to fetch node details."
            )
        
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
            if conn:
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
        
        if conn:
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
        
        # If no database connection, return error
        if conn is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Unable to fetch network summary."
            )
        
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
        
        if conn:
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
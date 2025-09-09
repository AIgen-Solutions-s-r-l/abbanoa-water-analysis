"""Dashboard summary API endpoints."""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import asyncpg
import os

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["dashboard"])

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


@router.get("/dashboard/summary")
async def get_dashboard_summary() -> Dict[str, Any]:
    """Get summary data for dashboard display with latest available real data."""
    try:
        conn = await get_db_connection()
        
        # Get the latest data timestamp from our historical data
        latest_time_query = """
            SELECT MAX(timestamp) as latest_timestamp
            FROM water_infrastructure.sensor_readings
        """
        latest_time_result = await conn.fetchrow(latest_time_query)
        latest_timestamp = latest_time_result['latest_timestamp'] if latest_time_result else None
        
        # Get all active nodes with their latest readings (from historical data)
        nodes_query = """
            SELECT DISTINCT ON (n.node_id)
                n.node_id,
                n.node_name,
                n.node_type,
                COALESCE(sr.flow_rate, 0.0) as flow_rate,
                COALESCE(sr.pressure, 0.0) as pressure,
                COALESCE(sr.temperature, 0.0) as temperature,
                sr.timestamp as last_reading,
                COALESCE(sr.quality_score, 0.95) as quality_score
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
        nodes_with_data = 0
        
        for row in nodes_data:
            flow_rate = float(row['flow_rate']) if row['flow_rate'] else 0.0
            pressure = float(row['pressure']) if row['pressure'] else 0.0
            
            nodes.append({
                "node_id": row['node_id'],
                "node_name": row['node_name'],
                "flow_rate": flow_rate,
                "pressure": pressure,
                "temperature": float(row['temperature']) if row['temperature'] else 0.0,
                "anomaly_count": 0,  # We'll calculate real anomalies later
                "quality_score": float(row['quality_score']),
                "last_reading": row['last_reading'].isoformat() if row['last_reading'] else None
            })
            
            if flow_rate > 0 or pressure > 0:
                nodes_with_data += 1
                total_flow += flow_rate
                total_pressure += pressure
            
            if row['node_id'] in ['VIA_SANT_ANNA', 'VIA_SENECA', 'SERBATOIO_SELARGIUS', 'SERBATOIO_CUCCURU_LINU']:
                active_nodes += 1
        
        # Calculate network metrics based on real data
        avg_pressure = total_pressure / nodes_with_data if nodes_with_data > 0 else 0.0
        
        # Calculate total consumption from the latest 24h window of historical data
        consumption_query = """
            SELECT 
                SUM(flow_rate * 1800) as total_liters,  -- flow_rate in L/s * 30 minutes (1800 seconds)
                AVG(flow_rate) as avg_flow_rate,
                AVG(pressure) as avg_pressure,
                COUNT(DISTINCT node_id) as active_connections
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= $1
            AND timestamp <= $2
        """
        
        if latest_timestamp:
            # Calculate 24 hours before latest timestamp
            start_timestamp = latest_timestamp - timedelta(hours=24)
            consumption_result = await conn.fetchrow(consumption_query, start_timestamp, latest_timestamp)
            total_consumption = float(consumption_result['total_liters']) if consumption_result['total_liters'] else 0.0
            avg_flow_24h = float(consumption_result['avg_flow_rate']) if consumption_result['avg_flow_rate'] else 0.0
            avg_pressure_24h = float(consumption_result['avg_pressure']) if consumption_result['avg_pressure'] else 0.0
            active_connections = consumption_result['active_connections'] if consumption_result['active_connections'] else 0
        else:
            total_consumption = 0.0
            avg_flow_24h = 0.0
            avg_pressure_24h = 0.0
            active_connections = 0
        
        # Calculate system health based on pressure and flow metrics
        # Normal pressure range: 2.5 - 4.5 bar
        # Normal flow range: varies but we'll use averages
        pressure_health = min(100, (avg_pressure_24h / 3.5) * 100) if avg_pressure_24h > 0 else 0
        flow_health = min(100, 95) if avg_flow_24h > 0 else 0  # Simplified
        system_health = (pressure_health + flow_health) / 2
        
        # Get anomaly statistics (detect anomalies based on thresholds)
        anomaly_query = """
            SELECT 
                COUNT(CASE WHEN pressure < 2.0 OR pressure > 5.0 THEN 1 END) as pressure_anomalies,
                COUNT(CASE WHEN flow_rate < 0 OR flow_rate > 200 THEN 1 END) as flow_anomalies,
                COUNT(CASE WHEN temperature < 5 OR temperature > 30 THEN 1 END) as temp_anomalies
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= $1
            AND timestamp <= $2
        """
        
        if latest_timestamp:
            anomaly_result = await conn.fetchrow(anomaly_query, start_timestamp, latest_timestamp)
            total_anomalies = (
                (anomaly_result['pressure_anomalies'] or 0) +
                (anomaly_result['flow_anomalies'] or 0) +
                (anomaly_result['temp_anomalies'] or 0)
            )
        else:
            total_anomalies = 0
        
        await conn.close()
        
        # Return comprehensive dashboard data
        return {
            "nodes": nodes,
            "network": {
                "active_nodes": active_nodes,
                "total_flow_lps": total_flow,  # Latest total flow in L/s
                "average_pressure_bar": avg_pressure_24h,  # 24h average pressure
                "total_volume_m3": total_consumption / 1000,  # Convert liters to m³
                "anomaly_count": total_anomalies,
                "efficiency_percentage": system_health,
                "alert_count": total_anomalies,  # Use anomalies as alerts
                "energy_consumption_kwh": total_flow * 0.5,  # Estimate based on flow
                "water_quality_index": 95.0,  # Default quality
                "active_connections": active_connections
            },
            "recent_anomalies": total_anomalies,
            "total_consumption": total_consumption,  # Total consumption in liters
            "system_health": system_health,
            "last_updated": latest_timestamp.isoformat() if latest_timestamp else datetime.now(timezone.utc).isoformat(),
            "data_timestamp": latest_timestamp.isoformat() if latest_timestamp else None,
            "data_note": "Showing latest available historical data from September 2025"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
"""Dashboard summary API endpoints."""

from datetime import datetime, timezone
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
    'password': os.getenv('POSTGRES_PASSWORD', 'abbanoa_dev_pass')
}


async def get_db_connection():
    """Get database connection."""
    return await asyncpg.connect(**DB_CONFIG)


@router.get("/dashboard/summary")
async def get_dashboard_summary() -> Dict[str, Any]:
    """Get summary data for dashboard display."""
    try:
        conn = await get_db_connection()
        
        # Get all active nodes with their latest readings
        nodes_query = """
            SELECT DISTINCT ON (n.node_id)
                n.node_id,
                n.node_name,
                n.node_type,
                COALESCE(sr.flow_rate, 0.0) as flow_rate,
                COALESCE(sr.pressure, 0.0) as pressure,
                0 as anomaly_count,
                COALESCE(sr.quality_score, 0.95) as quality_score
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON sr.node_id = n.node_id
                AND sr.timestamp > NOW() - INTERVAL '24 hours'
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
            
            nodes.append({
                "node_id": row['node_id'],
                "node_name": row['node_name'],
                "flow_rate": flow_rate,
                "pressure": pressure,
                "anomaly_count": row['anomaly_count'],
                "quality_score": float(row['quality_score'])
            })
            
            if flow_rate > 0 or pressure > 0:
                active_nodes += 1
                total_flow += flow_rate
                total_pressure += pressure
        
        # Calculate network metrics
        avg_pressure = total_pressure / active_nodes if active_nodes > 0 else 0.0
        
        # Get recent anomalies count
        anomalies_query = """
            SELECT COUNT(*) as anomaly_count
            FROM water_infrastructure.anomalies
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            AND resolved_at IS NULL
        """
        anomalies_result = await conn.fetchrow(anomalies_query)
        recent_anomalies = anomalies_result['anomaly_count'] if anomalies_result else 0
        
        await conn.close()
        
        return {
            "nodes": nodes,
            "network": {
                "active_nodes": active_nodes,
                "total_flow": total_flow,
                "avg_pressure": avg_pressure,
                "total_volume_m3": total_flow * 24,  # Estimate daily volume
                "anomaly_count": recent_anomalies
            },
            "recent_anomalies": recent_anomalies,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
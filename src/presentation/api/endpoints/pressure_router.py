"""Pressure zones API endpoints."""

from datetime import datetime, timezone
from typing import Dict, Any, List
import asyncpg
import os

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["pressure"])

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


@router.get("/pressure/zones")
async def get_pressure_zones() -> Dict[str, List[Dict[str, Any]]]:
    """Get pressure zones summary data using real database tables."""
    # Check if we should use mock data
    use_mock = os.getenv('USE_MOCK_API', 'false').lower() == 'true'
    
    if use_mock:
        # Return mock data for testing
        return {
            "zones": [
                {
                    "zone": "Z01",
                    "zoneName": "Zona Centro", 
                    "minPressure": 3.2,
                    "avgPressure": 4.5,
                    "maxPressure": 5.8,
                    "nodeCount": 15,
                    "nodesWithData": 14,
                    "efficiency": 96.5,
                    "status": "optimal"
                },
                {
                    "zone": "Z02",
                    "zoneName": "Zona Nord",
                    "minPressure": 2.8,
                    "avgPressure": 3.9,
                    "maxPressure": 5.2,
                    "nodeCount": 12,
                    "nodesWithData": 12,
                    "efficiency": 94.2,
                    "status": "normal"
                },
                {
                    "zone": "Z03",
                    "zoneName": "Zona Sud",
                    "minPressure": 2.1,
                    "avgPressure": 2.7,
                    "maxPressure": 3.5,
                    "nodeCount": 10,
                    "nodesWithData": 9,
                    "efficiency": 88.5,
                    "status": "warning"
                },
                {
                    "zone": "Z04",
                    "zoneName": "Zona Est",
                    "minPressure": 4.0,
                    "avgPressure": 4.8,
                    "maxPressure": 5.5,
                    "nodeCount": 18,
                    "nodesWithData": 18,
                    "efficiency": 97.2,
                    "status": "optimal"
                },
                {
                    "zone": "Z05",
                    "zoneName": "Zona Ovest",
                    "minPressure": 3.5,
                    "avgPressure": 4.2,
                    "maxPressure": 4.9,
                    "nodeCount": 14,
                    "nodesWithData": 13,
                    "efficiency": 95.8,
                    "status": "normal"
                }
            ]
        }
    
    conn = None
    try:
        conn = await get_db_connection()
        
        # Query to get pressure zones data from existing tables
        # Join pressure_zones with sensor_readings to get actual pressure data
        # Use the most recent 24 hours of data available (not NOW())
        query = """
            WITH latest_data AS (
                SELECT MAX(timestamp) as max_time 
                FROM water_infrastructure.sensor_readings
            ),
            zone_pressure_stats AS (
                SELECT 
                    pz.zone_id,
                    pz.zone_name,
                    COUNT(DISTINCT pz.node_id) as total_node_count,
                    COUNT(DISTINCT sr.node_id) as nodes_with_data,
                    COALESCE(MIN(sr.pressure), 0) as min_pressure,
                    COALESCE(AVG(sr.pressure), 0) as avg_pressure,
                    COALESCE(MAX(sr.pressure), 0) as max_pressure,
                    COALESCE(pz.efficiency, 95.0) as efficiency
                FROM water_infrastructure.pressure_zones pz
                CROSS JOIN latest_data ld
                LEFT JOIN water_infrastructure.sensor_readings sr 
                    ON pz.node_id = sr.node_id
                    AND sr.timestamp >= ld.max_time - INTERVAL '24 hours'
                    AND sr.timestamp <= ld.max_time
                WHERE pz.is_active = true
                GROUP BY pz.zone_id, pz.zone_name, pz.efficiency
            )
            SELECT 
                zone_id as zone,
                zone_name,
                min_pressure,
                avg_pressure,
                max_pressure,
                total_node_count as node_count,
                nodes_with_data,
                efficiency,
                CASE 
                    WHEN avg_pressure < 2.5 THEN 'critical'
                    WHEN avg_pressure < 3.0 THEN 'warning'
                    WHEN avg_pressure >= 4.0 AND avg_pressure <= 5.0 AND efficiency >= 95 THEN 'optimal'
                    WHEN avg_pressure > 6.0 THEN 'warning'  -- Pressione troppo alta
                    ELSE 'normal'
                END as status
            FROM zone_pressure_stats
            ORDER BY zone_id
        """
        
        rows = await conn.fetch(query)
        
        zones = []
        for row in rows:
            zones.append({
                "zone": row["zone"],
                "zoneName": row["zone_name"], 
                "minPressure": float(row["min_pressure"]) if row["min_pressure"] is not None else 0.0,
                "avgPressure": float(row["avg_pressure"]) if row["avg_pressure"] is not None else 0.0,
                "maxPressure": float(row["max_pressure"]) if row["max_pressure"] is not None else 0.0,
                "nodeCount": int(row["node_count"]) if row["node_count"] is not None else 0,
                "nodesWithData": int(row["nodes_with_data"]) if row["nodes_with_data"] is not None else 0,
                "efficiency": float(row["efficiency"]) if row["efficiency"] is not None else 95.0,
                "status": row["status"] if row["status"] is not None else "unknown"
            })
        
        return {"zones": zones}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()
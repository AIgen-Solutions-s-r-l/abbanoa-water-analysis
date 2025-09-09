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
    'password': os.getenv('POSTGRES_PASSWORD', 'abbanoa_dev_pass')
}


async def get_db_connection():
    """Get database connection."""
    return await asyncpg.connect(**DB_CONFIG)


@router.get("/pressure/zones")
async def get_pressure_zones() -> Dict[str, List[Dict[str, Any]]]:
    """Get pressure zones summary data."""
    # Production implementation: fetch from database
    conn = None
    try:
        conn = await get_db_connection()
        
        # Query to get pressure zones data
        # This assumes a table structure with zone information and pressure readings
        query = """
            WITH zone_stats AS (
                SELECT 
                    zone_id as zone,
                    zone_name as zone_name,
                    MIN(pressure) as min_pressure,
                    AVG(pressure) as avg_pressure,
                    MAX(pressure) as max_pressure,
                    COUNT(DISTINCT node_id) as node_count
                FROM pressure_readings
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY zone_id, zone_name
            )
            SELECT 
                zone,
                zone_name,
                min_pressure,
                avg_pressure,
                max_pressure,
                node_count,
                CASE 
                    WHEN avg_pressure < 2.5 THEN 'critical'
                    WHEN avg_pressure < 2.8 THEN 'warning'
                    ELSE 'normal'
                END as status
            FROM zone_stats
            ORDER BY zone
        """
        
        rows = await conn.fetch(query)
        
        zones = []
        for row in rows:
            zones.append({
                "zone": row["zone"],
                "zoneName": row["zone_name"],
                "minPressure": float(row["min_pressure"]),
                "avgPressure": float(row["avg_pressure"]),
                "maxPressure": float(row["max_pressure"]),
                "nodeCount": row["node_count"],
                "status": row["status"]
            })
        
        return {"zones": zones}
        
    except Exception as e:
        # If database connection fails, return mock data in development
        if os.getenv("ENV", "development") == "development":
            return {
                "zones": [
                    {
                        "zone": "DEFAULT_ZONE",
                        "zoneName": "Default Zone",
                        "minPressure": 2.5,
                        "avgPressure": 3.0,
                        "maxPressure": 3.5,
                        "nodeCount": 1,
                        "status": "normal"
                    }
                ]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()
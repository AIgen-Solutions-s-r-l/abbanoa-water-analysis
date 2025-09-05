"""Anomaly detection API endpoints."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import asyncpg
import os

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/v1", tags=["anomalies"])

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


@router.get("/anomalies")
async def get_anomalies(
    hours: int = Query(24, description="Hours to look back"),
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    severity: Optional[str] = Query(None, description="Filter by severity")
) -> List[Dict[str, Any]]:
    """Get recent anomalies."""
    # CI-friendly branch: allow mocked response when requested
    if os.getenv("USE_MOCK_API", "").lower() == "true":
        return [
            {
                "id": 1,
                "node_id": "VIA_DANTE_1",
                "node_name": "Via Dante Principale",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "anomaly_type": "pressure_low",
                "severity": "warning",
                "measurement_type": "pressure",
                "actual_value": 2.3,
                "expected_range": [2.8, 3.5],
                "deviation_percentage": 17.8,
                "description": "Pressure below threshold",
                "resolved_at": None,
            }
        ]

    try:
        conn = await get_db_connection()
        
        # Build the query with filters
        query = """
            SELECT 
                a.anomaly_id as id,
                a.node_id,
                n.node_name,
                a.timestamp,
                a.anomaly_type,
                a.severity,
                a.measurement_type,
                a.actual_value,
                a.expected_min,
                a.expected_max,
                a.deviation_percentage,
                COALESCE(a.metadata->>'description', a.anomaly_type || ' anomaly detected') as description,
                a.resolved_at
            FROM water_infrastructure.anomalies a
            JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
            WHERE a.timestamp > NOW() - INTERVAL '1 hour' * $1
        """
        
        params = [hours]
        param_count = 1
        
        if node_id is not None:
            param_count += 1
            query += f" AND a.node_id = ${param_count}"
            params.append(str(node_id))
            
        if severity is not None:
            param_count += 1
            query += f" AND a.severity = ${param_count}"
            params.append(str(severity))
            
        query += " ORDER BY a.timestamp DESC"
        
        anomalies_data = await conn.fetch(query, *params)
        
        # Transform anomalies data
        anomalies = []
        for row in anomalies_data:
            anomalies.append({
                "id": row['id'],
                "node_id": row['node_id'],
                "node_name": row['node_name'],
                "timestamp": row['timestamp'].isoformat(),
                "anomaly_type": row['anomaly_type'],
                "severity": row['severity'],
                "measurement_type": row['measurement_type'],
                "actual_value": float(row['actual_value']) if row['actual_value'] else None,
                "expected_range": [float(row['expected_min']) if row['expected_min'] else 0, 
                                 float(row['expected_max']) if row['expected_max'] else 0],
                "deviation_percentage": float(row['deviation_percentage']) if row['deviation_percentage'] else 0.0,
                "description": row['description'],
                "resolved_at": row['resolved_at'].isoformat() if row['resolved_at'] else None
            })
        
        await conn.close()
        
        # If no real anomalies found, return empty list instead of mock data
        return anomalies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
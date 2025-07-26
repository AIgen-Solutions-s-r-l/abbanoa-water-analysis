"""Anomaly detection API endpoints."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/v1", tags=["anomalies"])


@router.get("/anomalies")
async def get_anomalies(
    hours: int = Query(24, description="Hours to look back"),
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    severity: Optional[str] = Query(None, description="Filter by severity")
) -> List[Dict[str, Any]]:
    """Get recent anomalies."""
    try:
        # For now, return mock data - this should be connected to actual data source
        mock_anomalies = [
            {
                "id": "anomaly_001",
                "node_id": "node-serbatoio",
                "node_name": "Serbatoio Node",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "anomaly_type": "pressure_drop",
                "severity": "warning",
                "measurement_type": "pressure",
                "actual_value": 1.8,
                "expected_range": [2.0, 3.0],
                "deviation_percentage": 10.0,
                "description": "Pressure below expected range",
                "resolved_at": None
            }
        ]
        
        # Apply filters
        if node_id:
            mock_anomalies = [a for a in mock_anomalies if a["node_id"] == node_id]
        if severity:
            mock_anomalies = [a for a in mock_anomalies if a["severity"] == severity]
            
        return mock_anomalies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
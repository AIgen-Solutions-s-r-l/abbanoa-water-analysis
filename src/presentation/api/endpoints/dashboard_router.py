"""Dashboard summary API endpoints."""

from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard/summary")
async def get_dashboard_summary() -> Dict[str, Any]:
    """Get summary data for dashboard display."""
    try:
        # For now, return mock data - this should be connected to actual data source
        return {
            "nodes": [
                {
                    "node_id": "node-serbatoio",
                    "node_name": "Serbatoio Node",
                    "flow_rate": 150.0,
                    "pressure": 2.5,
                    "anomaly_count": 0,
                    "quality_score": 0.95
                },
                {
                    "node_id": "node-seneca",
                    "node_name": "Seneca Node", 
                    "flow_rate": 200.0,
                    "pressure": 2.8,
                    "anomaly_count": 0,
                    "quality_score": 0.92
                },
                {
                    "node_id": "node-santanna",
                    "node_name": "Sant'Anna Node",
                    "flow_rate": 180.0,
                    "pressure": 2.6,
                    "anomaly_count": 1,
                    "quality_score": 0.88
                }
            ],
            "network": {
                "active_nodes": 3,
                "total_flow": 530.0,
                "avg_pressure": 2.63,
                "total_volume_m3": 1000.0,
                "anomaly_count": 1
            },
            "recent_anomalies": 1,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
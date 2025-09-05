"""Pressure zones and nodes endpoints used by the frontend proxy.

These endpoints provide a thin API over the existing Postgres data when
available; if the database is not reachable, they return simulated data so the
frontend can still render gracefully.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["pressure", "nodes"]) 


async def _fetch_nodes_from_db(pool) -> List[Dict[str, Any]]:
    query = (
        """
        SELECT node_id,
               MAX(pressure) as pressure,
               MAX(flow_rate) as flow_rate,
               MAX(timestamp) as last_seen
        FROM sensor_readings
        GROUP BY node_id
        ORDER BY node_id
        """
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    nodes: List[Dict[str, Any]] = []
    for row in rows:
        nodes.append(
            {
                "node_id": row["node_id"],
                "pressure": float(row["pressure"]) if row["pressure"] is not None else None,
                "flow_rate": float(row["flow_rate"]) if row["flow_rate"] is not None else None,
                "last_seen": row["last_seen"].isoformat() if row["last_seen"] else None,
            }
        )
    return nodes


def _mock_nodes() -> List[Dict[str, Any]]:
    now_iso = datetime.now(timezone.utc).isoformat()
    return [
        {"node_id": "VIA_DANTE_1", "pressure": 3.2, "flow_rate": 4.3, "last_seen": now_iso},
        {"node_id": "VIA_ROMA_1", "pressure": 2.7, "flow_rate": 2.4, "last_seen": now_iso},
        {"node_id": "PIAZZA_ITALIA_1", "pressure": 3.5, "flow_rate": 3.9, "last_seen": now_iso},
        {"node_id": "SERBATOIO_SELARGIUS", "pressure": 4.2, "flow_rate": 8.7, "last_seen": now_iso},
    ]


@router.get("/nodes")
async def get_nodes() -> List[Dict[str, Any]]:
    """Return nodes with basic metrics for frontend enrichment."""
    try:
        # Access pool via app state if available (mounted by app_postgres)
        pool = router.app.state.pool if hasattr(router.app.state, "pool") else None
        if pool:
            return await _fetch_nodes_from_db(pool)
        return _mock_nodes()
    except Exception as exc:  # pragma: no cover - defensive fallback
        # On error, still provide mock data so UI stays functional
        return _mock_nodes()


def _mock_zones() -> Dict[str, Any]:
    # Simple static zones aligned with frontend expectations
    return {
        "zones": [
            {
                "zone": "ZONE_001",
                "zoneName": "Central Business District",
                "minPressure": 2.8,
                "avgPressure": 3.2,
                "maxPressure": 3.8,
                "nodeCount": 15,
                "status": "optimal",
            },
            {
                "zone": "ZONE_002",
                "zoneName": "Residential North",
                "minPressure": 2.1,
                "avgPressure": 2.8,
                "maxPressure": 3.2,
                "nodeCount": 23,
                "status": "warning",
            },
            {
                "zone": "ZONE_003",
                "zoneName": "Industrial District",
                "minPressure": 3.0,
                "avgPressure": 3.5,
                "maxPressure": 4.0,
                "nodeCount": 8,
                "status": "optimal",
            },
        ]
    }


@router.get("/pressure/zones")
async def get_pressure_zones() -> Dict[str, Any]:
    """Return pressure zones aggregated view.

    If a database connection pool is available, this could be extended to compute
    real aggregates; for now, return static data that matches the frontend
    contract to avoid 404s and unblock the dashboard.
    """
    try:
        # Placeholder for potential future DB-based aggregation
        return _mock_zones()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



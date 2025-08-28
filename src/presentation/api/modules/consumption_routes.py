"""Consumption routes module."""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import asyncpg
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/consumption", tags=["consumption"])


class ConsumptionData(BaseModel):
    """Consumption data model."""
    timestamp: datetime
    value: float
    node_id: str
    unit: str = "m³/h"


class ConsumptionResponse(BaseModel):
    """Consumption response model."""
    data: List[ConsumptionData]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


@router.get("/", response_model=ConsumptionResponse)
async def get_consumption_data(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    node_id: Optional[str] = Query(None, description="Node ID"),
    interval: str = Query("hourly", description="Data interval")
):
    """Get consumption data."""
    try:
        pool = router.app.state.pool
        
        # Default date range if not provided
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=7)
        if not end_date:
            end_date = datetime.now(timezone.utc)
        
        # Build query
        query = """
            SELECT timestamp, value, node_id, unit
            FROM sensor_readings
            WHERE timestamp BETWEEN $1 AND $2
        """
        params = [start_date, end_date]
        
        if node_id:
            query += " AND node_id = $3"
            params.append(node_id)
        
        query += " ORDER BY timestamp"
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        
        # Transform data
        data = [
            ConsumptionData(
                timestamp=row['timestamp'],
                value=float(row['value']),
                node_id=row['node_id'],
                unit=row['unit']
            )
            for row in rows
        ]
        
        # Calculate summary
        if data:
            values = [d.value for d in data]
            summary = {
                "total_readings": len(data),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "total_consumption": sum(values)
            }
        else:
            summary = {
                "total_readings": 0,
                "average": 0,
                "min": 0,
                "max": 0,
                "total_consumption": 0
            }
        
        metadata = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "interval": interval,
            "node_id": node_id,
            "data_points": len(data)
        }
        
        return ConsumptionResponse(
            data=data,
            summary=summary,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error fetching consumption data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/nodes")
async def get_consumption_nodes():
    """Get list of consumption nodes."""
    try:
        pool = router.app.state.pool
        
        query = """
            SELECT DISTINCT node_id, 
                   MIN(timestamp) as first_reading,
                   MAX(timestamp) as last_reading,
                   COUNT(*) as total_readings
            FROM sensor_readings
            GROUP BY node_id
            ORDER BY node_id
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        nodes = [
            {
                "node_id": row['node_id'],
                "first_reading": row['first_reading'].isoformat() if row['first_reading'] else None,
                "last_reading": row['last_reading'].isoformat() if row['last_reading'] else None,
                "total_readings": row['total_readings']
            }
            for row in rows
        ]
        
        return {"nodes": nodes}
        
    except Exception as e:
        logger.error(f"Error fetching consumption nodes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

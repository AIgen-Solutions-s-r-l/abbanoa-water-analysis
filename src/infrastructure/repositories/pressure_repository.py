
import asyncpg
from typing import Optional, List
from src.schemas.pressure import PressureZone, PressureZoneResponse, TimeRange, PressureSummary
from datetime import datetime, timedelta, timezone

class PressureRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_pressure_zones(self, start_time: Optional[str], end_time: Optional[str]) -> PressureZoneResponse:
        if not self.pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = datetime.now(timezone.utc)
            
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = end_dt - timedelta(days=30)
        
        async with self.pool.acquire() as conn:
            query = """
            SELECT 
                n.node_id,
                n.node_name,
                ROUND(MIN(sr.pressure)::numeric, 1) as min_pressure,
                ROUND(AVG(sr.pressure)::numeric, 1) as avg_pressure,
                ROUND(MAX(sr.pressure)::numeric, 1) as max_pressure,
                COUNT(sr.pressure) as reading_count,
                CASE 
                    WHEN AVG(sr.pressure) >= 3.0 THEN 'optimal'
                    WHEN AVG(sr.pressure) >= 2.5 THEN 'warning'
                    ELSE 'critical'
                END as status
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON n.node_id = sr.node_id 
                AND sr.timestamp >= $1 
                AND sr.timestamp <= $2
                AND sr.pressure IS NOT NULL
            WHERE n.is_active = true
            GROUP BY n.node_id, n.node_name
            HAVING COUNT(sr.pressure) > 0
            ORDER BY n.node_id
            """
            
            rows = await conn.fetch(query, start_dt, end_dt)
            
            zones = []
            for row in rows:
                zones.append(PressureZone(
                    zone=f"Node {row['node_id']}",
                    zoneName=row['node_name'] or f"Node {row['node_id']}",
                    minPressure=float(row['min_pressure']) if row['min_pressure'] else 0.0,
                    avgPressure=float(row['avg_pressure']) if row['avg_pressure'] else 0.0,
                    maxPressure=float(row['max_pressure']) if row['max_pressure'] else 0.0,
                    nodeCount=1,
                    readingCount=int(row['reading_count']),
                    status=row['status']
                ))
            
            summary = PressureSummary(
                totalZones=len(zones),
                optimalZones=len([z for z in zones if z.status == 'optimal']),
                warningZones=len([z for z in zones if z.status == 'warning']),
                criticalZones=len([z for z in zones if z.status == 'critical'])
            )

            return PressureZoneResponse(
                zones=zones,
                timeRange=TimeRange(start=start_dt.isoformat(), end=end_dt.isoformat()),
                summary=summary
            )


import asyncpg
from typing import List, Optional
from src.schemas.reading import Reading
from datetime import datetime, timedelta

class ReadingRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_node_readings(self, node_id: str, start_time: Optional[str], end_time: Optional[str], max_points: int) -> List[Reading]:
        async with self.pool.acquire() as conn:
            # Default to last 24 hours if no time range provided
            if not start_time or not end_time:
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(hours=24)
            else:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")
            
            # Calculate time range in days
            time_range_days = (end_dt - start_dt).total_seconds() / (24 * 3600)
            
            # Choose aggregation strategy based on time range
            if time_range_days <= 1:
                # Raw data for <= 1 day (limit to max_points most recent)
                query = """
                    SELECT timestamp, flow_rate, pressure, temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
                
            elif time_range_days <= 7:
                # Hourly averages for 1-7 days
                query = """
                    SELECT 
                        date_trunc('hour', timestamp) as timestamp,
                        AVG(flow_rate) as flow_rate,
                        AVG(pressure) as pressure,
                        AVG(temperature) as temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                        AND (flow_rate IS NOT NULL OR pressure IS NOT NULL OR temperature IS NOT NULL)
                    GROUP BY date_trunc('hour', timestamp)
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
                
            elif time_range_days <= 31:
                # Daily averages for 7-31 days
                query = """
                    SELECT 
                        date_trunc('day', timestamp) as timestamp,
                        AVG(flow_rate) as flow_rate,
                        AVG(pressure) as pressure,
                        AVG(temperature) as temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                        AND (flow_rate IS NOT NULL OR pressure IS NOT NULL OR temperature IS NOT NULL)
                    GROUP BY date_trunc('day', timestamp)
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
                
            else:
                # Weekly averages for > 30 days (much cleaner visualization for long ranges)
                query = """
                    SELECT 
                        date_trunc('week', timestamp) as timestamp,
                        AVG(flow_rate) as flow_rate,
                        AVG(pressure) as pressure,
                        AVG(temperature) as temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                        AND (flow_rate IS NOT NULL OR pressure IS NOT NULL OR temperature IS NOT NULL)
                    GROUP BY date_trunc('week', timestamp)
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
            
            rows = await conn.fetch(query, *params)
            
            readings = []
            for row in rows:
                readings.append(Reading(
                    timestamp=row["timestamp"].isoformat(),
                    flow_rate=float(row["flow_rate"]) if row["flow_rate"] else None,
                    pressure=float(row["pressure"]) if row["pressure"] else None,
                    temperature=float(row["temperature"]) if row["temperature"] else None,
                ))
            
            return readings

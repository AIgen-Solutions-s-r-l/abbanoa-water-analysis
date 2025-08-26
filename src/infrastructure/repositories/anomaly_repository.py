

import asyncpg
from typing import List
from src.schemas.anomaly import Anomaly
from datetime import datetime, timedelta

class AnomalyRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_anomalies(self) -> List[Anomaly]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    a.anomaly_id,
                    a.node_id,
                    n.node_name,
                    a.timestamp,
                    a.anomaly_type,
                    a.severity,
                    a.measurement_type,
                    a.actual_value,
                    a.expected_value,
                    a.deviation_percentage,
                    a.detection_method,
                    a.resolved_at
                FROM water_infrastructure.anomalies a
                JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
                WHERE a.timestamp > NOW() - INTERVAL '7 days'
                ORDER BY a.timestamp DESC
                LIMIT 100
            """)
            
            anomalies = []
            for row in rows:
                description = f"{row['anomaly_type'].replace('_', ' ').title()} detected"
                if row['measurement_type']:
                    description += f" in {row['measurement_type']}"
                
                expected_val = float(row["expected_value"]) if row["expected_value"] else 0
                expected_range = [expected_val * 0.9, expected_val * 1.1]
                
                anomalies.append(Anomaly(
                    id=f"anomaly_{row['anomaly_id']}",
                    node_id=row["node_id"],
                    node_name=row["node_name"],
                    timestamp=row["timestamp"].isoformat() if row["timestamp"] else None,
                    anomaly_type=row["anomaly_type"],
                    severity=row["severity"],
                    measurement_type=row["measurement_type"],
                    actual_value=float(row["actual_value"]) if row["actual_value"] else None,
                    expected_range=expected_range,
                    deviation_percentage=float(row["deviation_percentage"]) if row["deviation_percentage"] else None,
                    description=description,
                    resolved_at=row["resolved_at"].isoformat() if row["resolved_at"] else None
                ))
            
            if not anomalies:
                anomalies = [Anomaly(
                    id="anomaly_mock_001",
                    node_id="node-001",
                    node_name="Selargius Monitoring Station",
                    timestamp=(datetime.now() - timedelta(hours=1)).isoformat(),
                    anomaly_type="pressure_drop",
                    severity="warning",
                    measurement_type="pressure",
                    actual_value=1.8,
                    expected_range=[2.0, 3.0],
                    deviation_percentage=10.0,
                    description="Pressure below expected range",
                    resolved_at=None
                )]
            
            return anomalies

"""Repository for accessing sensor_data table in BigQuery."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from google.cloud import bigquery

from src.application.interfaces.repositories import ISensorReadingRepository
from src.domain.entities.sensor_reading import SensorReading
from src.infrastructure.persistence.bigquery_config import BigQueryConnection


class SensorDataRepository(ISensorReadingRepository):
    """Repository implementation for sensor_data table."""
    
    def __init__(self, connection: BigQueryConnection) -> None:
        self.connection = connection
        self.dataset_id = connection.config.dataset_id
        self.project_id = connection.config.project_id
    
    async def create(self, sensor_reading: SensorReading) -> SensorReading:
        """Create is not implemented for read-only sensor_data table."""
        raise NotImplementedError("sensor_data table is read-only")
    
    async def get_by_id(self, reading_id: UUID) -> Optional[SensorReading]:
        """Get by ID is not implemented for sensor_data table."""
        raise NotImplementedError("sensor_data table doesn't have UUID IDs")
    
    async def get_by_node_id(
        self,
        node_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[SensorReading]:
        """Get sensor readings from the normalized view."""
        query = f"""
        SELECT 
            timestamp,
            node_id,
            node_name,
            temperature,
            flow_rate,
            pressure,
            volume
        FROM `{self.project_id}.{self.dataset_id}.v_sensor_readings_normalized`
        WHERE 1=1
        """
        
        params = []
        
        # Map UUID to node_id string used in BigQuery
        node_mapping = {
            '00000000-0000-0000-0000-000000000001': 'node-santanna',
            '00000000-0000-0000-0000-000000000002': 'node-seneca', 
            '00000000-0000-0000-0000-000000000003': 'node-serbatoio'
        }
        
        if str(node_id) in node_mapping:
            query += " AND node_id = @node_id"
            params.append(bigquery.ScalarQueryParameter("node_id", "STRING", node_mapping[str(node_id)]))
        
        if start_time:
            query += " AND timestamp >= @start_time"
            params.append(bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time))
        
        if end_time:
            query += " AND timestamp <= @end_time"
            params.append(bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time))
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        # Execute query
        job_config = bigquery.QueryJobConfig()
        job_config.query_parameters = params
        
        query_job = self.connection.client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Convert to SensorReading entities
        readings = []
        
        # Reverse mapping from node_id string to UUID
        uuid_mapping = {
            'node-santanna': UUID('00000000-0000-0000-0000-000000000001'),
            'node-seneca': UUID('00000000-0000-0000-0000-000000000002'),
            'node-serbatoio': UUID('00000000-0000-0000-0000-000000000003')
        }
        
        for row in results:
            # Map node_id back to UUID
            actual_node_id = uuid_mapping.get(row.node_id, UUID('00000000-0000-0000-0000-000000000001'))
            
            # Create a minimal SensorReading
            reading = SensorReading(
                node_id=actual_node_id,
                sensor_type='multi',
                timestamp=row.timestamp,
                temperature=row.temperature,
                flow_rate=row.flow_rate,  
                pressure=row.pressure,
                volume=row.volume
            )
            readings.append(reading)
        
        return readings
    
    async def get_latest_by_node(self, node_id: UUID) -> Optional[SensorReading]:
        """Get the latest reading for a node."""
        readings = await self.get_by_node_id(node_id, limit=1)
        return readings[0] if readings else None
    
    async def get_anomalous_readings(
        self,
        start_time: datetime,
        end_time: datetime,
        node_ids: Optional[List[UUID]] = None
    ) -> List[SensorReading]:
        """Get anomalous readings (simplified - just extreme values)."""
        query = f"""
        SELECT 
            timestamp,
            node_id,
            node_name,
            temperature,
            flow_rate,
            pressure,
            volume
        FROM `{self.project_id}.{self.dataset_id}.v_sensor_readings_normalized`
        WHERE timestamp BETWEEN @start_time AND @end_time
        AND (
            flow_rate > 200 OR flow_rate < 0 OR
            pressure > 6 OR pressure < 2 OR
            temperature > 40 OR temperature < 0
        )
        """
        
        params = [
            bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
            bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time)
        ]
        
        # Execute query
        job_config = bigquery.QueryJobConfig()
        job_config.query_parameters = params
        
        query_job = self.connection.client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Convert to SensorReading entities
        readings = []
        
        # Reverse mapping from node_id string to UUID
        uuid_mapping = {
            'node-santanna': UUID('00000000-0000-0000-0000-000000000001'),
            'node-seneca': UUID('00000000-0000-0000-0000-000000000002'),
            'node-serbatoio': UUID('00000000-0000-0000-0000-000000000003')
        }
        
        for row in results:
            # Map node_id back to UUID
            actual_node_id = uuid_mapping.get(row.node_id, UUID('00000000-0000-0000-0000-000000000001'))
            
            reading = SensorReading(
                node_id=actual_node_id,
                sensor_type='multi',
                timestamp=row.timestamp,
                temperature=row.temperature,
                flow_rate=row.flow_rate,
                pressure=row.pressure,
                volume=row.volume
            )
            readings.append(reading)
        
        return readings
    
    async def delete(self, reading_id: UUID) -> bool:
        """Delete is not implemented for read-only sensor_data table."""
        raise NotImplementedError("sensor_data table is read-only")
    
    async def update(self, sensor_reading: SensorReading) -> SensorReading:
        """Update is not implemented for read-only sensor_data table."""
        raise NotImplementedError("sensor_data table is read-only")
    
    async def add(self, reading: SensorReading) -> None:
        """Add is not implemented for read-only sensor_data table."""
        raise NotImplementedError("sensor_data table is read-only")
    
    async def delete_by_id(self, reading_id: UUID) -> None:
        """Delete by ID is not implemented for read-only sensor_data table."""
        raise NotImplementedError("sensor_data table is read-only")
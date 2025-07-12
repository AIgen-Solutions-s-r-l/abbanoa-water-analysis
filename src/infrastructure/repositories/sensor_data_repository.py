"""Repository for accessing sensor_data table in BigQuery."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from google.cloud import bigquery

from src.application.interfaces.repositories import ISensorReadingRepository
from src.domain.entities.sensor_reading import SensorReading
from src.domain.value_objects.measurements import (
    FlowRate,
    Pressure,
    Temperature,
    Volume,
)
from src.domain.value_objects.sensor_type import SensorType
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

    def _create_sensor_reading_from_row(self, row) -> SensorReading:
        """Create a SensorReading entity from a BigQuery row."""
        # Reverse mapping from numeric node_id back to UUID
        uuid_mapping = {
            "281492": UUID("00000000-0000-0000-0000-000000000001"),
            "211514": UUID("00000000-0000-0000-0000-000000000002"),
            "288400": UUID("00000000-0000-0000-0000-000000000003"),
            "288399": UUID("00000000-0000-0000-0000-000000000004"),
            "215542": UUID("00000000-0000-0000-0000-000000000005"),
            "273933": UUID("00000000-0000-0000-0000-000000000006"),
            "215600": UUID("00000000-0000-0000-0000-000000000007"),
            "287156": UUID("00000000-0000-0000-0000-000000000008"),
        }

        # Map node_id back to UUID
        actual_node_id = uuid_mapping.get(
            str(row.node_id), UUID("00000000-0000-0000-0000-000000000001")
        )

        # Create value objects from raw values, handling None values
        # Use try-catch to handle values that might be outside normal ranges
        temperature = None
        if row.temperature is not None:
            try:
                temperature = Temperature(value=float(row.temperature), unit="celsius")
            except ValueError:
                # Skip invalid temperature readings
                pass

        flow_rate = None
        if row.flow_rate is not None:
            try:
                flow_rate = FlowRate(
                    value=float(row.flow_rate), unit="liters_per_second"
                )
            except ValueError:
                # Skip invalid flow rate readings
                pass

        pressure = None
        if row.pressure is not None:
            try:
                # Create custom pressure value object that handles higher ranges
                pressure_value = float(row.pressure)
                if (
                    pressure_value >= 0 and pressure_value <= 100
                ):  # Expand range to handle real data
                    pressure = CustomPressure(value=pressure_value, unit="bar")
            except ValueError:
                # Skip invalid pressure readings
                pass

        volume = None
        if row.volume is not None:
            try:
                volume = Volume(value=float(row.volume), unit="liters")
            except ValueError:
                # Skip invalid volume readings
                pass

        # At least one measurement must be valid
        if not any([temperature, flow_rate, pressure, volume]):
            raise ValueError("No valid measurements found")

        # Create the sensor reading
        return SensorReading(
            node_id=actual_node_id,
            sensor_type=SensorType.MULTI_PARAMETER,
            timestamp=row.timestamp,
            temperature=temperature,
            flow_rate=flow_rate,
            pressure=pressure,
            volume=volume,
        )

    async def get_by_node_id(
        self,
        node_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[SensorReading]:
        """Get sensor readings from the ML sensor readings table."""
        query = f"""
        SELECT
            timestamp,
            node_id,
            node_name,
            temperature,
            flow_rate,
            pressure,
            volume
        FROM `{self.project_id}.{self.dataset_id}.sensor_readings_ml`
        WHERE 1=1
        """

        params = []

        # Map UUID to actual numeric node_id used in BigQuery
        # Updated mappings based on actual data in the database
        node_mapping = {
            "00000000-0000-0000-0000-000000000001": "281492",  # Primary node with most data
            "00000000-0000-0000-0000-000000000002": "211514",  # Secondary node
            "00000000-0000-0000-0000-000000000003": "288400",  # Third node
            "00000000-0000-0000-0000-000000000004": "288399",  # Fourth node
            "00000000-0000-0000-0000-000000000005": "215542",  # Fifth node
            "00000000-0000-0000-0000-000000000006": "273933",  # Sixth node
            "00000000-0000-0000-0000-000000000007": "215600",  # Seventh node
            "00000000-0000-0000-0000-000000000008": "287156",  # Eighth node
        }

        if str(node_id) in node_mapping:
            query += " AND node_id = @node_id"
            params.append(
                bigquery.ScalarQueryParameter(
                    "node_id", "STRING", node_mapping[str(node_id)]
                )
            )

        if start_time:
            query += " AND timestamp >= @start_time"
            params.append(
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time)
            )

        if end_time:
            query += " AND timestamp <= @end_time"
            params.append(
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time)
            )

        # Only include high-quality data
        query += " AND data_quality_score > 0.7"

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
        for row in results:
            try:
                reading = self._create_sensor_reading_from_row(row)
                readings.append(reading)
            except Exception as e:
                # Skip invalid readings but log the error
                print(f"Warning: Skipping invalid reading: {e}")
                continue

        return readings

    async def get_latest_by_node(self, node_id: UUID) -> Optional[SensorReading]:
        """Get the latest reading for a node."""
        readings = await self.get_by_node_id(node_id, limit=1)
        return readings[0] if readings else None

    async def get_anomalous_readings(
        self,
        start_time: datetime,
        end_time: datetime,
        node_ids: Optional[List[UUID]] = None,
    ) -> List[SensorReading]:
        """Get anomalous readings using statistical analysis."""
        query = f"""
        WITH stats AS (
            SELECT
                node_id,
                AVG(flow_rate) as avg_flow,
                STDDEV(flow_rate) as std_flow,
                AVG(pressure) as avg_pressure,
                STDDEV(pressure) as std_pressure,
                AVG(temperature) as avg_temperature,
                STDDEV(temperature) as std_temperature
            FROM `{self.project_id}.{self.dataset_id}.sensor_readings_ml`
            WHERE timestamp BETWEEN @start_time AND @end_time
            AND data_quality_score > 0.7
            AND flow_rate IS NOT NULL
            AND pressure IS NOT NULL
            AND temperature IS NOT NULL
            GROUP BY node_id
        )
        SELECT
            r.timestamp,
            r.node_id,
            r.node_name,
            r.temperature,
            r.flow_rate,
            r.pressure,
            r.volume,
            ABS(r.flow_rate - s.avg_flow) / NULLIF(s.std_flow, 0) as flow_z_score,
            ABS(r.pressure - s.avg_pressure) / NULLIF(s.std_pressure, 0) as pressure_z_score,
            ABS(r.temperature - s.avg_temperature) / NULLIF(s.std_temperature, 0) as temp_z_score
        FROM `{self.project_id}.{self.dataset_id}.sensor_readings_ml` r
        JOIN stats s ON r.node_id = s.node_id
        WHERE r.timestamp BETWEEN @start_time AND @end_time
        AND r.data_quality_score > 0.7
        AND r.flow_rate IS NOT NULL
        AND r.pressure IS NOT NULL
        AND r.temperature IS NOT NULL
        AND (
            ABS(r.flow_rate - s.avg_flow) / NULLIF(s.std_flow, 0) > 2.5 OR
            ABS(r.pressure - s.avg_pressure) / NULLIF(s.std_pressure, 0) > 2.5 OR
            ABS(r.temperature - s.avg_temperature) / NULLIF(s.std_temperature, 0) > 2.5
        )
        ORDER BY r.timestamp DESC
        """

        params = [
            bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
            bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
        ]

        # Execute query
        job_config = bigquery.QueryJobConfig()
        job_config.query_parameters = params

        query_job = self.connection.client.query(query, job_config=job_config)
        results = query_job.result()

        # Convert to SensorReading entities
        readings = []
        for row in results:
            try:
                reading = self._create_sensor_reading_from_row(row)
                readings.append(reading)
            except Exception as e:
                # Skip invalid readings but log the error
                print(f"Warning: Skipping invalid anomaly reading: {e}")
                continue

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


class CustomPressure(Pressure):
    """Custom pressure value object that handles higher pressure ranges."""

    def _validate(self) -> None:
        """Validate pressure value with extended range."""
        if self.value < 0:
            raise ValueError(f"Pressure cannot be negative: {self.value}")

        # Extended maximum reasonable pressure (100 bar) to handle real data
        if self.value > 100:
            raise ValueError(f"Pressure {self.value} exceeds maximum reasonable value")

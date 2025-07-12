"""BigQuery implementation of sensor reading repository."""

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


class BigQuerySensorReadingRepository(ISensorReadingRepository):
    """BigQuery implementation of sensor reading repository."""

    TABLE_NAME = "sensor_readings"

    def __init__(self, connection: BigQueryConnection) -> None:
        self.connection = connection
        self._ensure_table_exists()

    def _ensure_table_exists(self) -> None:
        """Ensure the sensor readings table exists."""
        if not self.connection.table_exists(self.TABLE_NAME):
            schema = [
                bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("node_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("sensor_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("temperature", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("flow_rate", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("pressure", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("volume", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            ]

            table_ref = f"{self.connection.config.dataset_ref}.{self.TABLE_NAME}"
            table = bigquery.Table(table_ref, schema=schema)
            self.connection.client.create_table(table)

    async def add(self, reading: SensorReading) -> None:
        """Add a new sensor reading."""
        row = self._entity_to_row(reading)

        table_ref = f"{self.connection.config.dataset_ref}.{self.TABLE_NAME}"
        errors = self.connection.client.insert_rows_json(table_ref, [row])

        if errors:
            raise Exception(f"Failed to insert sensor reading: {errors}")

    async def get_by_id(self, reading_id: UUID) -> Optional[SensorReading]:
        """Get a sensor reading by ID."""
        query = """
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE id = @reading_id
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("reading_id", "STRING", str(reading_id))
            ]
        )

        query_job = self.connection.client.query(query, job_config=job_config)
        results = list(query_job.result())

        if not results:
            return None

        return self._row_to_entity(results[0])

    async def get_by_node_id(
        self,
        node_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[SensorReading]:
        """Get sensor readings for a specific node."""
        query = """
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE node_id = @node_id
        """

        query_parameters = [
            bigquery.ScalarQueryParameter("node_id", "STRING", str(node_id))
        ]

        if start_time:
            query += " AND timestamp >= @start_time"
            query_parameters.append(
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time)
            )

        if end_time:
            query += " AND timestamp <= @end_time"
            query_parameters.append(
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time)
            )

        query += " ORDER BY timestamp DESC"

        if limit:
            query += f" LIMIT {limit}"

        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query_job = self.connection.client.query(query, job_config=job_config)

        readings = []
        for row in query_job.result():
            reading = self._row_to_entity(row)
            if reading:
                readings.append(reading)

        return readings

    async def get_latest_by_node(self, node_id: UUID) -> Optional[SensorReading]:
        """Get the latest sensor reading for a node."""
        readings = await self.get_by_node_id(node_id, limit=1)
        return readings[0] if readings else None

    async def delete_by_id(self, reading_id: UUID) -> None:
        """Delete a sensor reading by ID."""
        query = """
        DELETE FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE id = @reading_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("reading_id", "STRING", str(reading_id))
            ]
        )

        query_job = self.connection.client.query(query, job_config=job_config)
        query_job.result()  # Wait for query to complete

    def _entity_to_row(self, reading: SensorReading) -> dict:
        """Convert entity to BigQuery row."""
        row = {
            "id": str(reading.id),
            "node_id": str(reading.node_id),
            "sensor_type": reading.sensor_type.value,
            "timestamp": reading.timestamp.isoformat(),
            "created_at": reading.created_at.isoformat(),
            "updated_at": reading.updated_at.isoformat(),
        }

        if reading.temperature:
            row["temperature"] = reading.temperature.value
        if reading.flow_rate:
            row["flow_rate"] = reading.flow_rate.value
        if reading.pressure:
            row["pressure"] = reading.pressure.value
        if reading.volume:
            row["volume"] = reading.volume.value

        return row

    def _row_to_entity(self, row: bigquery.Row) -> Optional[SensorReading]:
        """Convert BigQuery row to entity."""
        try:
            # Create value objects
            temperature = Temperature(row.temperature) if row.temperature else None
            flow_rate = FlowRate(row.flow_rate) if row.flow_rate else None
            pressure = Pressure(row.pressure) if row.pressure else None
            volume = Volume(row.volume) if row.volume else None

            # Create entity
            reading = SensorReading(
                id=UUID(row.id),
                node_id=UUID(row.node_id),
                sensor_type=SensorType.from_string(row.sensor_type),
                timestamp=row.timestamp,
                temperature=temperature,
                flow_rate=flow_rate,
                pressure=pressure,
                volume=volume,
            )

            # Set timestamps
            reading._created_at = row.created_at
            reading._updated_at = row.updated_at

            return reading
        except Exception as e:
            # Log error and return None
            print(f"Error converting row to entity: {e}")
            return None

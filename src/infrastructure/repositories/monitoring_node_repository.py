"""BigQuery implementation of monitoring node repository."""

from typing import List, Optional
from uuid import UUID

from google.cloud import bigquery

from src.application.interfaces.repositories import IMonitoringNodeRepository
from src.domain.entities.monitoring_node import MonitoringNode
from src.domain.value_objects.location import Coordinates, NodeLocation
from src.domain.value_objects.node_status import NodeStatus
from src.infrastructure.persistence.bigquery_config import BigQueryConnection


class BigQueryMonitoringNodeRepository(IMonitoringNodeRepository):
    """BigQuery implementation of monitoring node repository."""

    TABLE_NAME = "monitoring_nodes"

    def __init__(self, connection: BigQueryConnection) -> None:
        self.connection = connection
        self._ensure_table_exists()

    def _ensure_table_exists(self) -> None:
        """Ensure the monitoring nodes table exists."""
        if not self.connection.table_exists(self.TABLE_NAME):
            schema = [
                bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("node_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("location_site_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("location_area", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("location_pcr_unit", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("location_address", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("location_latitude", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("location_longitude", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            ]

            table_ref = f"{self.connection.config.dataset_ref}.{self.TABLE_NAME}"
            table = bigquery.Table(table_ref, schema=schema)
            self.connection.client.create_table(table)

    async def add(self, node: MonitoringNode) -> None:
        """Add a new monitoring node."""
        row = self._entity_to_row(node)

        table_ref = f"{self.connection.config.dataset_ref}.{self.TABLE_NAME}"
        errors = self.connection.client.insert_rows_json(table_ref, [row])

        if errors:
            raise Exception(f"Failed to insert monitoring node: {errors}")

    async def get_by_id(self, node_id: UUID) -> Optional[MonitoringNode]:
        """Get a monitoring node by ID."""
        query = f"""
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE id = @node_id
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("node_id", "STRING", str(node_id))
            ]
        )

        query_job = self.connection.client.query(query, job_config=job_config)
        results = list(query_job.result())

        if not results:
            return None

        return self._row_to_entity(results[0])

    async def get_by_name(self, name: str) -> Optional[MonitoringNode]:
        """Get a monitoring node by name."""
        query = f"""
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE name = @name
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", name)]
        )

        query_job = self.connection.client.query(query, job_config=job_config)
        results = list(query_job.result())

        if not results:
            return None

        return self._row_to_entity(results[0])

    async def get_all(
        self,
        active_only: bool = False,
        node_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[MonitoringNode]:
        """Get all monitoring nodes with optional filters."""
        query = f"""
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE 1=1
        """

        query_parameters = []

        if active_only:
            query += " AND status = @status"
            query_parameters.append(
                bigquery.ScalarQueryParameter(
                    "status", "STRING", NodeStatus.ACTIVE.value
                )
            )

        if node_type:
            query += " AND node_type = @node_type"
            query_parameters.append(
                bigquery.ScalarQueryParameter("node_type", "STRING", node_type)
            )

        if location:
            query += (
                " AND (location_area = @location OR location_site_name = @location)"
            )
            query_parameters.append(
                bigquery.ScalarQueryParameter("location", "STRING", location)
            )

        query += " ORDER BY name"

        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query_job = self.connection.client.query(query, job_config=job_config)

        nodes = []
        for row in query_job.result():
            node = self._row_to_entity(row)
            if node:
                nodes.append(node)

        return nodes

    async def update(self, node: MonitoringNode) -> None:
        """Update an existing monitoring node."""
        query = f"""
        UPDATE `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        SET 
            name = @name,
            node_type = @node_type,
            status = @status,
            description = @description,
            location_site_name = @location_site_name,
            location_area = @location_area,
            location_pcr_unit = @location_pcr_unit,
            location_address = @location_address,
            location_latitude = @location_latitude,
            location_longitude = @location_longitude,
            updated_at = @updated_at
        WHERE id = @id
        """

        row = self._entity_to_row(node)

        query_parameters = [
            bigquery.ScalarQueryParameter(
                key,
                (
                    "STRING"
                    if isinstance(value, str)
                    else "FLOAT64"
                    if isinstance(value, float)
                    else "TIMESTAMP"
                ),
                value,
            )
            for key, value in row.items()
            if value is not None
        ]

        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query_job = self.connection.client.query(query, job_config=job_config)
        query_job.result()

    async def delete_by_id(self, node_id: UUID) -> None:
        """Delete a monitoring node by ID."""
        query = f"""
        DELETE FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE id = @node_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("node_id", "STRING", str(node_id))
            ]
        )

        query_job = self.connection.client.query(query, job_config=job_config)
        query_job.result()

    def _entity_to_row(self, node: MonitoringNode) -> dict:
        """Convert entity to BigQuery row."""
        row = {
            "id": str(node.id),
            "name": node.name,
            "node_type": node.node_type,
            "status": node.status.value,
            "description": node.description,
            "location_site_name": node.location.site_name,
            "location_area": node.location.area,
            "location_pcr_unit": node.location.pcr_unit,
            "location_address": node.location.address,
            "created_at": node.created_at.isoformat(),
            "updated_at": node.updated_at.isoformat(),
        }

        if node.location.coordinates:
            row["location_latitude"] = node.location.coordinates.latitude
            row["location_longitude"] = node.location.coordinates.longitude

        return row

    def _row_to_entity(self, row: bigquery.Row) -> Optional[MonitoringNode]:
        """Convert BigQuery row to entity."""
        try:
            # Create location
            coordinates = None
            if row.location_latitude and row.location_longitude:
                coordinates = Coordinates(
                    latitude=row.location_latitude, longitude=row.location_longitude
                )

            location = NodeLocation(
                site_name=row.location_site_name,
                area=row.location_area,
                pcr_unit=row.location_pcr_unit,
                address=row.location_address,
                coordinates=coordinates,
            )

            # Create entity
            node = MonitoringNode(
                id=UUID(row.id),
                name=row.name,
                location=location,
                node_type=row.node_type,
                status=NodeStatus.from_string(row.status),
                description=row.description,
            )

            # Set timestamps
            node._created_at = row.created_at
            node._updated_at = row.updated_at

            return node
        except Exception as e:
            # Log error and return None
            print(f"Error converting row to entity: {e}")
            return None

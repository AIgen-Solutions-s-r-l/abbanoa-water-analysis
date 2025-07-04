"""BigQuery implementation of water network repository."""

import json
from typing import List, Optional
from uuid import UUID

from google.cloud import bigquery

from src.application.interfaces.repositories import IWaterNetworkRepository
from src.domain.entities.water_network import WaterNetwork
from src.infrastructure.persistence.bigquery_config import BigQueryConnection


class BigQueryWaterNetworkRepository(IWaterNetworkRepository):
    """BigQuery implementation of water network repository."""
    
    TABLE_NAME = "water_networks"
    
    def __init__(self, connection: BigQueryConnection) -> None:
        self.connection = connection
        self._ensure_table_exists()
    
    def _ensure_table_exists(self) -> None:
        """Ensure the water networks table exists."""
        if not self.connection.table_exists(self.TABLE_NAME):
            schema = [
                bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("region", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("node_ids", "STRING", mode="REPEATED"),
                bigquery.SchemaField("connections", "STRING", mode="NULLABLE"),  # JSON string
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            table_ref = f"{self.connection.config.dataset_ref}.{self.TABLE_NAME}"
            table = bigquery.Table(table_ref, schema=schema)
            self.connection.client.create_table(table)
    
    async def add(self, network: WaterNetwork) -> None:
        """Add a new water network."""
        row = self._entity_to_row(network)
        
        table_ref = f"{self.connection.config.dataset_ref}.{self.TABLE_NAME}"
        errors = self.connection.client.insert_rows_json(table_ref, [row])
        
        if errors:
            raise Exception(f"Failed to insert water network: {errors}")
    
    async def get_by_id(self, network_id: UUID) -> Optional[WaterNetwork]:
        """Get a water network by ID."""
        query = f"""
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE id = @network_id
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("network_id", "STRING", str(network_id))
            ]
        )
        
        query_job = self.connection.client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if not results:
            return None
        
        return self._row_to_entity(results[0])
    
    async def get_by_name(self, name: str) -> Optional[WaterNetwork]:
        """Get a water network by name."""
        query = f"""
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE name = @name
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("name", "STRING", name)
            ]
        )
        
        query_job = self.connection.client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if not results:
            return None
        
        return self._row_to_entity(results[0])
    
    async def get_by_region(self, region: str) -> List[WaterNetwork]:
        """Get all water networks in a region."""
        query = f"""
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE region = @region
        ORDER BY name
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("region", "STRING", region)
            ]
        )
        
        query_job = self.connection.client.query(query, job_config=job_config)
        
        networks = []
        for row in query_job.result():
            network = self._row_to_entity(row)
            if network:
                networks.append(network)
        
        return networks
    
    async def get_all(self) -> List[WaterNetwork]:
        """Get all water networks."""
        query = f"""
        SELECT * FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        ORDER BY region, name
        """
        
        query_job = self.connection.client.query(query)
        
        networks = []
        for row in query_job.result():
            network = self._row_to_entity(row)
            if network:
                networks.append(network)
        
        return networks
    
    async def update(self, network: WaterNetwork) -> None:
        """Update an existing water network."""
        query = f"""
        UPDATE `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        SET 
            name = @name,
            region = @region,
            description = @description,
            node_ids = @node_ids,
            connections = @connections,
            updated_at = @updated_at
        WHERE id = @id
        """
        
        row = self._entity_to_row(network)
        
        # Convert parameters
        query_parameters = [
            bigquery.ScalarQueryParameter("id", "STRING", row["id"]),
            bigquery.ScalarQueryParameter("name", "STRING", row["name"]),
            bigquery.ScalarQueryParameter("region", "STRING", row["region"]),
            bigquery.ScalarQueryParameter("description", "STRING", row.get("description")),
            bigquery.ArrayQueryParameter("node_ids", "STRING", row["node_ids"]),
            bigquery.ScalarQueryParameter("connections", "STRING", row["connections"]),
            bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", row["updated_at"]),
        ]
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query_job = self.connection.client.query(query, job_config=job_config)
        query_job.result()
    
    async def delete_by_id(self, network_id: UUID) -> None:
        """Delete a water network by ID."""
        query = f"""
        DELETE FROM `{self.connection.config.dataset_ref}.{self.TABLE_NAME}`
        WHERE id = @network_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("network_id", "STRING", str(network_id))
            ]
        )
        
        query_job = self.connection.client.query(query, job_config=job_config)
        query_job.result()
    
    def _entity_to_row(self, network: WaterNetwork) -> dict:
        """Convert entity to BigQuery row."""
        # Convert connections to JSON
        connections_list = [
            {"from": str(from_id), "to": str(to_id)}
            for from_id, to_id in network._connections
        ]
        
        return {
            "id": str(network.id),
            "name": network.name,
            "region": network.region,
            "description": network.description,
            "node_ids": [str(node_id) for node_id in network._nodes.keys()],
            "connections": json.dumps(connections_list),
            "created_at": network.created_at.isoformat(),
            "updated_at": network.updated_at.isoformat(),
        }
    
    def _row_to_entity(self, row: bigquery.Row) -> Optional[WaterNetwork]:
        """Convert BigQuery row to entity."""
        try:
            # Create entity
            network = WaterNetwork(
                id=UUID(row.id),
                name=row.name,
                region=row.region,
                description=row.description
            )
            
            # Note: We don't load nodes here - they should be loaded separately
            # and added to the network as needed
            
            # Parse connections
            if row.connections:
                connections_list = json.loads(row.connections)
                for conn in connections_list:
                    network._connections.add((UUID(conn["from"]), UUID(conn["to"])))
            
            # Set timestamps
            network._created_at = row.created_at
            network._updated_at = row.updated_at
            
            return network
        except Exception as e:
            # Log error and return None
            print(f"Error converting row to entity: {e}")
            return None
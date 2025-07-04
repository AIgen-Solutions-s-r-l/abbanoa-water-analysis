"""Use case for calculating water network efficiency."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from src.application.dto.analysis_results_dto import NetworkEfficiencyResultDTO
from src.application.interfaces.event_bus import IEventBus
from src.application.interfaces.repositories import (
    IMonitoringNodeRepository,
    ISensorReadingRepository,
    IWaterNetworkRepository,
)
from src.domain.services.network_efficiency_service import NetworkEfficiencyService


class CalculateNetworkEfficiencyUseCase:
    """Use case for calculating water network efficiency metrics."""

    def __init__(
        self,
        water_network_repository: IWaterNetworkRepository,
        monitoring_node_repository: IMonitoringNodeRepository,
        sensor_reading_repository: ISensorReadingRepository,
        network_efficiency_service: NetworkEfficiencyService,
        event_bus: IEventBus,
    ) -> None:
        self.water_network_repository = water_network_repository
        self.monitoring_node_repository = monitoring_node_repository
        self.sensor_reading_repository = sensor_reading_repository
        self.network_efficiency_service = network_efficiency_service
        self.event_bus = event_bus

    async def execute(
        self,
        network_id: UUID,
        start_date: datetime,
        end_date: datetime,
        include_node_details: bool = True,
    ) -> NetworkEfficiencyResultDTO:
        """Calculate network efficiency for a specific time period."""
        # Validate inputs
        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        # Get the network
        network = await self.water_network_repository.get_by_id(network_id)
        if not network:
            raise ValueError(f"Network with ID {network_id} not found")

        # Load all nodes for the network
        all_nodes = await self.monitoring_node_repository.get_all()
        network_nodes = [
            node for node in all_nodes if node.id in [n.id for n in network.nodes]
        ]

        # Load readings for each node
        for node in network_nodes:
            readings = await self.sensor_reading_repository.get_by_node_id(
                node_id=node.id, start_time=start_date, end_time=end_date
            )
            for reading in readings:
                node.add_reading(reading)

        # Update network with loaded nodes
        network._nodes = {node.id: node for node in network_nodes}

        # Calculate efficiency
        efficiency_event = self.network_efficiency_service.calculate_network_efficiency(
            network=network, start_time=start_date, end_time=end_date
        )

        # Publish event
        await self.event_bus.publish(efficiency_event)

        # Get node contributions if requested
        node_contributions = {}
        if include_node_details:
            contributions = self.network_efficiency_service.analyze_node_contribution(
                network=network, start_time=start_date, end_time=end_date
            )
            # Convert UUID keys to strings for DTO
            node_contributions = {
                str(node_id): data for node_id, data in contributions.items()
            }

        # Create and return result DTO
        return NetworkEfficiencyResultDTO(
            network_id=network_id,
            period_start=start_date,
            period_end=end_date,
            efficiency_percentage=efficiency_event.efficiency_percentage,
            total_input_volume=efficiency_event.total_input,
            total_output_volume=efficiency_event.total_output,
            loss_volume=efficiency_event.total_input - efficiency_event.total_output,
            loss_percentage=efficiency_event.loss_percentage,
            node_contributions=node_contributions,
        )

    async def detect_leakage_zones(
        self,
        network_id: UUID,
        start_date: datetime,
        end_date: datetime,
        loss_threshold: float = 10.0,
    ) -> List[Dict[str, any]]:
        """Detect potential leakage zones in the network."""
        # Get the network with all data
        network = await self.water_network_repository.get_by_id(network_id)
        if not network:
            raise ValueError(f"Network with ID {network_id} not found")

        # Load all nodes and their readings
        all_nodes = await self.monitoring_node_repository.get_all()
        network_nodes = [
            node for node in all_nodes if node.id in [n.id for n in network.nodes]
        ]

        for node in network_nodes:
            readings = await self.sensor_reading_repository.get_by_node_id(
                node_id=node.id, start_time=start_date, end_time=end_date
            )
            for reading in readings:
                node.add_reading(reading)

        network._nodes = {node.id: node for node in network_nodes}

        # Detect leakage zones
        leakage_zones = self.network_efficiency_service.detect_leakage_zones(
            network=network,
            start_time=start_date,
            end_time=end_date,
            loss_threshold=loss_threshold,
        )

        # Format results
        results = []
        for from_id, to_id, loss_percentage in leakage_zones:
            from_node = network.get_node(from_id)
            to_node = network.get_node(to_id)

            results.append(
                {
                    "from_node_id": str(from_id),
                    "from_node_name": from_node.name if from_node else "Unknown",
                    "to_node_id": str(to_id),
                    "to_node_name": to_node.name if to_node else "Unknown",
                    "loss_percentage": round(loss_percentage, 2),
                    "severity": self._classify_loss_severity(loss_percentage),
                }
            )

        return results

    def _classify_loss_severity(self, loss_percentage: float) -> str:
        """Classify the severity of water loss."""
        if loss_percentage >= 30:
            return "critical"
        elif loss_percentage >= 20:
            return "high"
        elif loss_percentage >= 10:
            return "medium"
        else:
            return "low"

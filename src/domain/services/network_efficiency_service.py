"""Domain service for calculating water network efficiency."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from src.domain.entities.monitoring_node import MonitoringNode
from src.domain.entities.water_network import WaterNetwork
from src.domain.events.network_events import NetworkEfficiencyCalculatedEvent
from src.domain.value_objects.measurements import FlowRate, Volume


class NetworkEfficiencyService:
    """Service for calculating and analyzing water network efficiency."""
    
    def calculate_network_efficiency(
        self,
        network: WaterNetwork,
        start_time: datetime,
        end_time: datetime,
        input_node_types: Optional[List[str]] = None,
        output_node_types: Optional[List[str]] = None
    ) -> NetworkEfficiencyCalculatedEvent:
        """Calculate network efficiency for a given time period."""
        input_node_types = input_node_types or ["input", "source", "supply"]
        output_node_types = output_node_types or ["output", "delivery", "distribution"]
        
        # Identify input and output nodes
        input_nodes = self._get_nodes_by_type(network, input_node_types)
        output_nodes = self._get_nodes_by_type(network, output_node_types)
        
        if not input_nodes or not output_nodes:
            raise ValueError("Network must have both input and output nodes for efficiency calculation")
        
        # Calculate total input and output
        total_input = self._calculate_total_flow(input_nodes, start_time, end_time)
        total_output = self._calculate_total_flow(output_nodes, start_time, end_time)
        
        # Calculate efficiency and loss
        efficiency = 0.0
        loss_percentage = 100.0
        
        if total_input > 0:
            efficiency = (total_output / total_input) * 100
            loss_percentage = 100.0 - efficiency
        
        # Create and return event
        return NetworkEfficiencyCalculatedEvent(
            aggregate_id=network.id,
            network_id=network.id,
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            efficiency_percentage=round(efficiency, 2),
            total_input=round(total_input, 2),
            total_output=round(total_output, 2),
            loss_percentage=round(loss_percentage, 2)
        )
    
    def _get_nodes_by_type(
        self,
        network: WaterNetwork,
        node_types: List[str]
    ) -> List[MonitoringNode]:
        """Get nodes that match any of the given types."""
        matching_nodes = []
        
        for node in network.nodes:
            node_type_lower = node.node_type.lower()
            if any(t in node_type_lower for t in node_types):
                matching_nodes.append(node)
        
        return matching_nodes
    
    def _calculate_total_flow(
        self,
        nodes: List[MonitoringNode],
        start_time: datetime,
        end_time: datetime
    ) -> float:
        """Calculate total flow volume for a list of nodes."""
        total_flow = 0.0
        
        for node in nodes:
            readings = node.get_readings_in_range(start_time, end_time)
            
            # Sum up volumes if available, otherwise integrate flow rates
            for reading in readings:
                if reading.volume:
                    total_flow += reading.volume.value
                elif reading.flow_rate:
                    # Assume 30-minute intervals for flow rate integration
                    # Convert L/s to m³ for 30 minutes
                    total_flow += reading.flow_rate.value * 1800 / 1000
        
        return total_flow
    
    def analyze_node_contribution(
        self,
        network: WaterNetwork,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[UUID, Dict[str, float]]:
        """Analyze each node's contribution to network flow."""
        contributions = {}
        
        for node in network.nodes:
            total_volume = self._calculate_total_flow([node], start_time, end_time)
            
            # Calculate average flow rate
            readings = node.get_readings_in_range(start_time, end_time)
            flow_rates = [r.flow_rate.value for r in readings if r.flow_rate]
            avg_flow_rate = sum(flow_rates) / len(flow_rates) if flow_rates else 0.0
            
            contributions[node.id] = {
                "node_name": node.name,
                "total_volume": round(total_volume, 2),
                "average_flow_rate": round(avg_flow_rate, 2),
                "reading_count": len(readings)
            }
        
        return contributions
    
    def detect_leakage_zones(
        self,
        network: WaterNetwork,
        start_time: datetime,
        end_time: datetime,
        loss_threshold: float = 10.0
    ) -> List[Tuple[UUID, UUID, float]]:
        """Detect potential leakage zones between connected nodes."""
        potential_leaks = []
        
        # Check flow balance between connected nodes
        for from_id, to_id in network._connections:
            from_node = network.get_node(from_id)
            to_node = network.get_node(to_id)
            
            if not from_node or not to_node:
                continue
            
            # Calculate flow from source to destination
            from_flow = self._calculate_total_flow([from_node], start_time, end_time)
            to_flow = self._calculate_total_flow([to_node], start_time, end_time)
            
            if from_flow > 0:
                loss_percentage = ((from_flow - to_flow) / from_flow) * 100
                
                if loss_percentage > loss_threshold:
                    potential_leaks.append((from_id, to_id, loss_percentage))
        
        return potential_leaks
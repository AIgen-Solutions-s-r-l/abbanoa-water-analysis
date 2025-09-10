"""
Network Efficiency KPI Service.

This service handles all network efficiency related KPI calculations.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from src.schemas.api.kpis import NetworkEfficiencyKPIs, KPIAlert, KPIGoal, KPICard, AlertLevel, TrendDirection
from src.infrastructure.data.hybrid_data_service import HybridDataService
from .kpi_defaults import get_default_network_efficiency_kpis
from .kpi_utils import calculate_overall_efficiency_score, create_kpi_alert, create_kpi_goal

logger = logging.getLogger(__name__)


class NetworkEfficiencyService:
    """Service for network efficiency KPI calculations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def calculate_network_efficiency_kpis(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> NetworkEfficiencyKPIs:
        """Calculate network efficiency KPIs."""
        try:
            # Get network data
            network_data = await hybrid_service.get_network_efficiency_data(
                start_time, end_time, selected_nodes
            )
            
            if not network_data:
                return get_default_network_efficiency_kpis()
            
            # Calculate water loss
            water_loss_percentage = self._calculate_water_loss_percentage(network_data)
            
            # Calculate pressure efficiency
            pressure_efficiency = self._calculate_pressure_efficiency(network_data)
            
            # Calculate flow efficiency
            flow_efficiency = self._calculate_flow_efficiency(network_data)
            
            # Calculate energy efficiency
            energy_efficiency = self._calculate_energy_efficiency(network_data)
            
            # Calculate network coverage
            network_coverage = self._calculate_network_coverage(network_data)
            
            # Calculate distribution efficiency
            distribution_efficiency = self._calculate_distribution_efficiency(network_data)
            
            # Calculate overall efficiency score
            overall_efficiency_score = calculate_overall_efficiency_score(
                water_loss_percentage, pressure_efficiency, flow_efficiency,
                energy_efficiency, distribution_efficiency
            )
            
            return NetworkEfficiencyKPIs(
                water_loss_percentage=water_loss_percentage,
                pressure_efficiency_percentage=pressure_efficiency,
                flow_efficiency_percentage=flow_efficiency,
                energy_efficiency_percentage=energy_efficiency,
                network_coverage_percentage=network_coverage,
                distribution_efficiency_percentage=distribution_efficiency,
                overall_efficiency_score=overall_efficiency_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating network efficiency KPIs: {str(e)}")
            return get_default_network_efficiency_kpis()
    
    def check_network_efficiency_alerts(self, network_kpis: NetworkEfficiencyKPIs) -> List[KPIAlert]:
        """Check network efficiency alerts."""
        alerts = []
        
        if network_kpis.water_loss_percentage > 20.0:
            alerts.append(create_kpi_alert(
                category="network",
                metric_name="water_loss_percentage",
                message=f"Water loss is {network_kpis.water_loss_percentage:.1f}%, above threshold of 20%",
                severity=AlertLevel.high,
                threshold=20.0,
                current_value=network_kpis.water_loss_percentage
            ))
        
        if network_kpis.pressure_efficiency_percentage < 70.0:
            alerts.append(create_kpi_alert(
                category="network",
                metric_name="pressure_efficiency_percentage",
                message=f"Pressure efficiency is {network_kpis.pressure_efficiency_percentage:.1f}%, below threshold of 70%",
                severity=AlertLevel.medium,
                threshold=70.0,
                current_value=network_kpis.pressure_efficiency_percentage
            ))
        
        if network_kpis.energy_efficiency_percentage < 60.0:
            alerts.append(create_kpi_alert(
                category="network",
                metric_name="energy_efficiency_percentage",
                message=f"Energy efficiency is {network_kpis.energy_efficiency_percentage:.1f}%, below threshold of 60%",
                severity=AlertLevel.medium,
                threshold=60.0,
                current_value=network_kpis.energy_efficiency_percentage
            ))
        
        return alerts
    
    def generate_network_efficiency_goals(self, network_kpis: NetworkEfficiencyKPIs) -> List[KPIGoal]:
        """Generate network efficiency goals."""
        goals = []
        
        goals.append(create_kpi_goal(
            category="network",
            metric_name="water_loss_percentage",
            target_value=10.0,
            current_value=network_kpis.water_loss_percentage,
            description="Reduce water loss to under 10%",
            target_date=datetime.now() + timedelta(days=90)
        ))
        
        goals.append(create_kpi_goal(
            category="network",
            metric_name="pressure_efficiency_percentage",
            target_value=85.0,
            current_value=network_kpis.pressure_efficiency_percentage,
            description="Achieve 85% pressure efficiency",
            target_date=datetime.now() + timedelta(days=60)
        ))
        
        goals.append(create_kpi_goal(
            category="network",
            metric_name="energy_efficiency_percentage",
            target_value=75.0,
            current_value=network_kpis.energy_efficiency_percentage,
            description="Achieve 75% energy efficiency",
            target_date=datetime.now() + timedelta(days=120)
        ))
        
        return goals
    
    def generate_network_cards(self, network_kpis: NetworkEfficiencyKPIs) -> List[KPICard]:
        """Generate network efficiency KPI cards."""
        cards = []
        
        cards.append(KPICard(
            title="Water Loss",
            value=network_kpis.water_loss_percentage,
            unit="percentage",
            category="network",
            trend=TrendDirection.decreasing,
            change_percentage=-2.0,
            status="warning" if network_kpis.water_loss_percentage > 15.0 else "good",
            description="Water loss percentage"
        ))
        
        cards.append(KPICard(
            title="Pressure Efficiency",
            value=network_kpis.pressure_efficiency_percentage,
            unit="percentage",
            category="network",
            trend=TrendDirection.increasing,
            change_percentage=1.5,
            status="good" if network_kpis.pressure_efficiency_percentage >= 70.0 else "warning",
            description="Pressure efficiency percentage"
        ))
        
        cards.append(KPICard(
            title="Flow Efficiency",
            value=network_kpis.flow_efficiency_percentage,
            unit="percentage",
            category="network",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good" if network_kpis.flow_efficiency_percentage >= 80.0 else "warning",
            description="Flow efficiency percentage"
        ))
        
        cards.append(KPICard(
            title="Energy Efficiency",
            value=network_kpis.energy_efficiency_percentage,
            unit="percentage",
            category="network",
            trend=TrendDirection.increasing,
            change_percentage=3.0,
            status="good" if network_kpis.energy_efficiency_percentage >= 60.0 else "warning",
            description="Energy efficiency percentage"
        ))
        
        return cards
    
    # Private helper methods
    def _calculate_water_loss_percentage(self, network_data: Any) -> Optional[float]:
        """Calculate water loss percentage from flow differential."""
        if not network_data:
            return None
        
        input_flow = network_data.get('input_flow', 0)
        output_flow = network_data.get('output_flow', 0)
        known_consumption = network_data.get('known_consumption', 0)
        
        if input_flow <= 0:
            return None
        
        # Water loss = Input - Output - Known Consumption
        loss = input_flow - output_flow - known_consumption
        return (loss / input_flow) * 100
    
    def _calculate_pressure_efficiency(self, network_data: Any) -> Optional[float]:
        """Calculate pressure efficiency from sensor readings."""
        if not network_data:
            return None
        
        pressure_readings = network_data.get('pressure_readings', [])
        if not pressure_readings:
            return None
        
        efficiencies = []
        for reading in pressure_readings:
            actual = reading.get('pressure', 0)
            target = reading.get('target', 1)
            if target > 0:
                # Efficiency is ratio of actual to target, capped at 100%
                efficiency = min(actual / target, 1.0) * 100
                efficiencies.append(efficiency)
        
        if not efficiencies:
            return None
        
        return sum(efficiencies) / len(efficiencies)
    
    def _calculate_flow_efficiency(self, network_data: Any) -> Optional[float]:
        """Calculate flow efficiency based on pipe capacity utilization."""
        if not network_data:
            return None
        
        pipes = network_data.get('pipes', [])
        if not pipes:
            return None
        
        efficiencies = []
        for pipe in pipes:
            flow = pipe.get('flow', 0)
            capacity = pipe.get('capacity', 1)
            
            if capacity <= 0:
                continue
            
            utilization = flow / capacity
            
            # Optimal efficiency at 70-80% capacity
            if 0.7 <= utilization <= 0.8:
                efficiency = 100.0
            elif utilization < 0.7:
                efficiency = (utilization / 0.7) * 100
            else:
                # Over 80% reduces efficiency
                efficiency = max(0, 100 - ((utilization - 0.8) / 0.2) * 50)
            
            efficiencies.append(efficiency)
        
        if not efficiencies:
            return None
        
        return sum(efficiencies) / len(efficiencies)
    
    def _calculate_energy_efficiency(self, network_data: Any) -> Optional[float]:
        """Calculate energy efficiency from pump consumption data."""
        if not network_data:
            return None
        
        pumps = network_data.get('pumps', [])
        baseline = network_data.get('baseline_efficiency', 0.7)  # kWh/m³
        
        if not pumps or baseline <= 0:
            return None
        
        efficiencies = []
        for pump in pumps:
            flow_rate = pump.get('flow_rate', 0)
            energy = pump.get('energy_consumed', 0)
            
            if flow_rate > 0 and energy > 0:
                actual_efficiency = energy / flow_rate
                efficiency = (baseline / actual_efficiency) * 100
                efficiencies.append(min(efficiency, 100))
        
        if not efficiencies:
            return None
        
        return sum(efficiencies) / len(efficiencies)
    
    def _calculate_network_coverage(self, network_data: Any) -> Optional[float]:
        """Calculate network coverage from service area data."""
        if not network_data:
            return None
        
        total_area = network_data.get('total_service_area', 0)
        covered_area = network_data.get('covered_area', 0)
        
        if total_area <= 0:
            return None
        
        return (covered_area / total_area) * 100
    
    def _calculate_distribution_efficiency(self, network_data: Any) -> Optional[float]:
        """Calculate distribution efficiency from delivery metrics."""
        if not network_data:
            return None
        
        # Combine multiple factors for distribution efficiency
        delivered_volume = network_data.get('delivered_volume', 0)
        requested_volume = network_data.get('requested_volume', 0)
        
        if requested_volume <= 0:
            return None
        
        delivery_ratio = delivered_volume / requested_volume
        
        # Factor in service interruptions
        total_hours = network_data.get('total_hours', 1)
        interruption_hours = network_data.get('interruption_hours', 0)
        service_ratio = (total_hours - interruption_hours) / total_hours
        
        # Combined efficiency
        return min(delivery_ratio * service_ratio * 100, 100) 
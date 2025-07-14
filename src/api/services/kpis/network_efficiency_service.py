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
    def _calculate_water_loss_percentage(self, network_data: Any) -> float:
        """Calculate water loss percentage."""
        # Mock calculation - replace with actual logic
        return 15.0
    
    def _calculate_pressure_efficiency(self, network_data: Any) -> float:
        """Calculate pressure efficiency."""
        # Mock calculation - replace with actual logic
        return 85.0
    
    def _calculate_flow_efficiency(self, network_data: Any) -> float:
        """Calculate flow efficiency."""
        # Mock calculation - replace with actual logic
        return 90.0
    
    def _calculate_energy_efficiency(self, network_data: Any) -> float:
        """Calculate energy efficiency."""
        # Mock calculation - replace with actual logic
        return 80.0
    
    def _calculate_network_coverage(self, network_data: Any) -> float:
        """Calculate network coverage."""
        # Mock calculation - replace with actual logic
        return 95.0
    
    def _calculate_distribution_efficiency(self, network_data: Any) -> float:
        """Calculate distribution efficiency."""
        # Mock calculation - replace with actual logic
        return 88.0 
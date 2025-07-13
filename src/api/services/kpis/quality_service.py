"""
Quality KPI Service.

This service handles all water quality related KPI calculations.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from src.schemas.api.kpis import QualityKPIs, KPIAlert, KPIGoal, KPICard, AlertLevel, TrendDirection
from src.infrastructure.data.hybrid_data_service import HybridDataService
from .kpi_defaults import get_default_quality_kpis
from .kpi_utils import calculate_quality_score, create_kpi_alert, create_kpi_goal

logger = logging.getLogger(__name__)


class QualityService:
    """Service for quality KPI calculations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def calculate_quality_kpis(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> QualityKPIs:
        """Calculate water quality KPIs."""
        try:
            # Get quality data
            quality_data = await hybrid_service.get_quality_data(
                start_time, end_time, selected_nodes
            )
            
            if not quality_data:
                return get_default_quality_kpis()
            
            # Calculate quality compliance
            quality_compliance = self._calculate_quality_compliance(quality_data)
            
            # Calculate contamination incidents
            contamination_incidents = self._calculate_contamination_incidents(quality_data)
            
            # Calculate temperature compliance
            temperature_compliance = self._calculate_temperature_compliance(quality_data)
            
            # Calculate pressure compliance
            pressure_compliance = self._calculate_pressure_compliance(quality_data)
            
            # Calculate flow rate compliance
            flow_rate_compliance = self._calculate_flow_rate_compliance(quality_data)
            
            # Calculate quality score
            quality_score = calculate_quality_score(
                quality_compliance, contamination_incidents, temperature_compliance,
                pressure_compliance, flow_rate_compliance
            )
            
            return QualityKPIs(
                quality_compliance_percentage=quality_compliance,
                contamination_incidents_count=contamination_incidents,
                temperature_compliance_percentage=temperature_compliance,
                pressure_compliance_percentage=pressure_compliance,
                flow_rate_compliance_percentage=flow_rate_compliance,
                quality_score=quality_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating quality KPIs: {str(e)}")
            return get_default_quality_kpis()
    
    def check_quality_alerts(self, quality_kpis: QualityKPIs) -> List[KPIAlert]:
        """Check quality alerts."""
        alerts = []
        
        if quality_kpis.quality_compliance_percentage < 90.0:
            alerts.append(create_kpi_alert(
                category="quality",
                metric_name="quality_compliance_percentage",
                message=f"Quality compliance is {quality_kpis.quality_compliance_percentage:.1f}%, below threshold of 90%",
                severity=AlertLevel.high,
                threshold=90.0,
                current_value=quality_kpis.quality_compliance_percentage
            ))
        
        if quality_kpis.contamination_incidents_count > 5:
            alerts.append(create_kpi_alert(
                category="quality",
                metric_name="contamination_incidents_count",
                message=f"Contamination incidents count is {quality_kpis.contamination_incidents_count}, above threshold of 5",
                severity=AlertLevel.medium,
                threshold=5,
                current_value=quality_kpis.contamination_incidents_count
            ))
        
        if quality_kpis.temperature_compliance_percentage < 95.0:
            alerts.append(create_kpi_alert(
                category="quality",
                metric_name="temperature_compliance_percentage",
                message=f"Temperature compliance is {quality_kpis.temperature_compliance_percentage:.1f}%, below threshold of 95%",
                severity=AlertLevel.medium,
                threshold=95.0,
                current_value=quality_kpis.temperature_compliance_percentage
            ))
        
        return alerts
    
    def generate_quality_goals(self, quality_kpis: QualityKPIs) -> List[KPIGoal]:
        """Generate quality goals."""
        goals = []
        
        goals.append(create_kpi_goal(
            category="quality",
            metric_name="quality_compliance_percentage",
            target_value=98.0,
            current_value=quality_kpis.quality_compliance_percentage,
            description="Achieve 98% quality compliance",
            target_date=datetime.now() + timedelta(days=60)
        ))
        
        goals.append(create_kpi_goal(
            category="quality",
            metric_name="contamination_incidents_count",
            target_value=0,
            current_value=quality_kpis.contamination_incidents_count,
            description="Achieve zero contamination incidents",
            target_date=datetime.now() + timedelta(days=30)
        ))
        
        goals.append(create_kpi_goal(
            category="quality",
            metric_name="temperature_compliance_percentage",
            target_value=99.0,
            current_value=quality_kpis.temperature_compliance_percentage,
            description="Achieve 99% temperature compliance",
            target_date=datetime.now() + timedelta(days=45)
        ))
        
        return goals
    
    def generate_quality_cards(self, quality_kpis: QualityKPIs) -> List[KPICard]:
        """Generate quality KPI cards."""
        cards = []
        
        cards.append(KPICard(
            title="Quality Compliance",
            value=quality_kpis.quality_compliance_percentage,
            unit="percentage",
            category="quality",
            trend=TrendDirection.increasing,
            change_percentage=1.5,
            status="good" if quality_kpis.quality_compliance_percentage >= 90.0 else "warning",
            description="Quality compliance percentage"
        ))
        
        cards.append(KPICard(
            title="Contamination Incidents",
            value=quality_kpis.contamination_incidents_count,
            unit="count",
            category="quality",
            trend=TrendDirection.decreasing,
            change_percentage=-20.0,
            status="good" if quality_kpis.contamination_incidents_count <= 3 else "warning",
            description="Number of contamination incidents"
        ))
        
        cards.append(KPICard(
            title="Temperature Compliance",
            value=quality_kpis.temperature_compliance_percentage,
            unit="percentage",
            category="quality",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good" if quality_kpis.temperature_compliance_percentage >= 95.0 else "warning",
            description="Temperature compliance percentage"
        ))
        
        cards.append(KPICard(
            title="Pressure Compliance",
            value=quality_kpis.pressure_compliance_percentage,
            unit="percentage",
            category="quality",
            trend=TrendDirection.increasing,
            change_percentage=2.0,
            status="good" if quality_kpis.pressure_compliance_percentage >= 90.0 else "warning",
            description="Pressure compliance percentage"
        ))
        
        return cards
    
    # Private helper methods
    def _calculate_quality_compliance(self, quality_data: Any) -> float:
        """Calculate quality compliance percentage."""
        return 95.0  # Mock value
    
    def _calculate_contamination_incidents(self, quality_data: Any) -> int:
        """Calculate contamination incidents count."""
        return 2  # Mock value
    
    def _calculate_temperature_compliance(self, quality_data: Any) -> float:
        """Calculate temperature compliance percentage."""
        return 98.0  # Mock value
    
    def _calculate_pressure_compliance(self, quality_data: Any) -> float:
        """Calculate pressure compliance percentage."""
        return 92.0  # Mock value
    
    def _calculate_flow_rate_compliance(self, quality_data: Any) -> float:
        """Calculate flow rate compliance percentage."""
        return 94.0  # Mock value 
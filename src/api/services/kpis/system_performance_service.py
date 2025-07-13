"""
System Performance KPI Service.

This service handles all system performance related KPI calculations.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.schemas.api.kpis import SystemPerformanceKPIs, KPIAlert, KPIGoal, KPICard, AlertLevel
from src.infrastructure.data.hybrid_data_service import HybridDataService
from .kpi_defaults import get_default_system_performance_kpis
from .kpi_utils import calculate_performance_score, create_kpi_alert, create_kpi_goal

logger = logging.getLogger(__name__)


class SystemPerformanceService:
    """Service for system performance KPI calculations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def calculate_system_performance_kpis(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> SystemPerformanceKPIs:
        """Calculate system performance KPIs."""
        try:
            # Get system data
            system_data = await hybrid_service.get_system_performance_data(
                start_time, end_time, selected_nodes
            )
            
            if not system_data:
                return get_default_system_performance_kpis()
            
            # Calculate uptime
            uptime_percentage = self._calculate_uptime_percentage(system_data)
            
            # Calculate response time
            response_time = self._calculate_average_response_time(system_data)
            
            # Calculate throughput
            throughput = self._calculate_system_throughput(system_data)
            
            # Calculate error rate
            error_rate = self._calculate_error_rate(system_data)
            
            # Calculate resource utilization
            cpu_utilization = self._calculate_cpu_utilization(system_data)
            memory_utilization = self._calculate_memory_utilization(system_data)
            
            # Calculate availability
            availability = self._calculate_system_availability(system_data)
            
            # Calculate performance score
            performance_score = calculate_performance_score(
                uptime_percentage, response_time, throughput, error_rate
            )
            
            return SystemPerformanceKPIs(
                uptime_percentage=uptime_percentage,
                response_time_ms=response_time,
                throughput_requests_per_second=throughput,
                error_rate_percentage=error_rate,
                cpu_utilization_percentage=cpu_utilization,
                memory_utilization_percentage=memory_utilization,
                availability_percentage=availability,
                performance_score=performance_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating system performance KPIs: {str(e)}")
            return get_default_system_performance_kpis()
    
    def check_system_performance_alerts(self, system_kpis: SystemPerformanceKPIs) -> List[KPIAlert]:
        """Check system performance alerts."""
        alerts = []
        
        if system_kpis.uptime_percentage < 99.0:
            alerts.append(create_kpi_alert(
                category="system",
                metric_name="uptime_percentage",
                message=f"System uptime is {system_kpis.uptime_percentage:.1f}%, below threshold of 99%",
                severity=AlertLevel.high,
                threshold=99.0,
                current_value=system_kpis.uptime_percentage
            ))
        
        if system_kpis.error_rate_percentage > 1.0:
            alerts.append(create_kpi_alert(
                category="system",
                metric_name="error_rate_percentage",
                message=f"Error rate is {system_kpis.error_rate_percentage:.1f}%, above threshold of 1%",
                severity=AlertLevel.medium,
                threshold=1.0,
                current_value=system_kpis.error_rate_percentage
            ))
        
        if system_kpis.response_time_ms > 500.0:
            alerts.append(create_kpi_alert(
                category="system",
                metric_name="response_time_ms",
                message=f"Response time is {system_kpis.response_time_ms:.1f}ms, above threshold of 500ms",
                severity=AlertLevel.medium,
                threshold=500.0,
                current_value=system_kpis.response_time_ms
            ))
        
        if system_kpis.cpu_utilization_percentage > 80.0:
            alerts.append(create_kpi_alert(
                category="system",
                metric_name="cpu_utilization_percentage",
                message=f"CPU utilization is {system_kpis.cpu_utilization_percentage:.1f}%, above threshold of 80%",
                severity=AlertLevel.medium,
                threshold=80.0,
                current_value=system_kpis.cpu_utilization_percentage
            ))
        
        if system_kpis.memory_utilization_percentage > 85.0:
            alerts.append(create_kpi_alert(
                category="system",
                metric_name="memory_utilization_percentage",
                message=f"Memory utilization is {system_kpis.memory_utilization_percentage:.1f}%, above threshold of 85%",
                severity=AlertLevel.medium,
                threshold=85.0,
                current_value=system_kpis.memory_utilization_percentage
            ))
        
        return alerts
    
    def generate_system_performance_goals(self, system_kpis: SystemPerformanceKPIs) -> List[KPIGoal]:
        """Generate system performance goals."""
        goals = []
        
        goals.append(create_kpi_goal(
            category="system",
            metric_name="uptime_percentage",
            target_value=99.9,
            current_value=system_kpis.uptime_percentage,
            description="Achieve 99.9% system uptime",
            target_date=datetime.now()
        ))
        
        goals.append(create_kpi_goal(
            category="system",
            metric_name="response_time_ms",
            target_value=100.0,
            current_value=system_kpis.response_time_ms,
            description="Achieve sub-100ms response time",
            target_date=datetime.now()
        ))
        
        goals.append(create_kpi_goal(
            category="system",
            metric_name="error_rate_percentage",
            target_value=0.1,
            current_value=system_kpis.error_rate_percentage,
            description="Reduce error rate to under 0.1%",
            target_date=datetime.now()
        ))
        
        return goals
    
    def generate_system_cards(self, system_kpis: SystemPerformanceKPIs) -> List[KPICard]:
        """Generate system performance KPI cards."""
        from src.schemas.api.kpis import KPICard, TrendDirection
        
        cards = []
        
        cards.append(KPICard(
            title="System Uptime",
            value=system_kpis.uptime_percentage,
            unit="percentage",
            category="system",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good" if system_kpis.uptime_percentage >= 99.0 else "warning",
            description="System uptime percentage"
        ))
        
        cards.append(KPICard(
            title="Response Time",
            value=system_kpis.response_time_ms,
            unit="ms",
            category="system",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good" if system_kpis.response_time_ms <= 200.0 else "warning",
            description="Average response time"
        ))
        
        cards.append(KPICard(
            title="Throughput",
            value=system_kpis.throughput_requests_per_second,
            unit="req/s",
            category="system",
            trend=TrendDirection.increasing,
            change_percentage=5.0,
            status="good",
            description="System throughput"
        ))
        
        cards.append(KPICard(
            title="Error Rate",
            value=system_kpis.error_rate_percentage,
            unit="percentage",
            category="system",
            trend=TrendDirection.decreasing,
            change_percentage=-1.0,
            status="good" if system_kpis.error_rate_percentage <= 1.0 else "warning",
            description="System error rate"
        ))
        
        return cards
    
    # Private helper methods
    def _calculate_uptime_percentage(self, system_data: Any) -> float:
        """Calculate system uptime percentage."""
        # Mock calculation - replace with actual logic
        return 99.5
    
    def _calculate_average_response_time(self, system_data: Any) -> float:
        """Calculate average response time in milliseconds."""
        # Mock calculation - replace with actual logic
        return 150.0
    
    def _calculate_system_throughput(self, system_data: Any) -> float:
        """Calculate system throughput in requests per second."""
        # Mock calculation - replace with actual logic
        return 1000.0
    
    def _calculate_error_rate(self, system_data: Any) -> float:
        """Calculate error rate percentage."""
        # Mock calculation - replace with actual logic
        return 0.1
    
    def _calculate_cpu_utilization(self, system_data: Any) -> float:
        """Calculate CPU utilization percentage."""
        # Mock calculation - replace with actual logic
        return 65.0
    
    def _calculate_memory_utilization(self, system_data: Any) -> float:
        """Calculate memory utilization percentage."""
        # Mock calculation - replace with actual logic
        return 70.0
    
    def _calculate_system_availability(self, system_data: Any) -> float:
        """Calculate system availability percentage."""
        # Mock calculation - replace with actual logic
        return 99.9 
"""
KPI Orchestrator Service.

This service coordinates all KPI-related operations and acts as the main entry point
for KPI calculations, dashboard generation, and reporting.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from src.schemas.api.kpis import (
    KPIDashboard, KPICard, KPITrend, KPIBenchmark, KPIAlert, KPIGoal,
    KPIReport, KPIComparison, KPIConfiguration, KPIHealth, ReportFormat
)
from src.infrastructure.data.hybrid_data_service import HybridDataService

# Import all KPI services
from .system_performance_service import SystemPerformanceService
from .network_efficiency_service import NetworkEfficiencyService
from .quality_service import QualityService
from .dashboard_service import DashboardService
from .kpi_utils import (
    calculate_system_health, generate_time_points, calculate_trend_direction,
    calculate_change_percentage, calculate_kpi_improvements, calculate_kpi_regressions,
    calculate_overall_change_percentage, generate_period_comparison_insights,
    calculate_data_quality_score, calculate_component_health, determine_health_status,
    generate_health_insights
)
from .kpi_defaults import get_default_kpi_configuration_object

logger = logging.getLogger(__name__)


class KPIOrchestrator:
    """Main orchestrator service for all KPI operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize all KPI services
        self.system_service = SystemPerformanceService()
        self.network_service = NetworkEfficiencyService()
        self.quality_service = QualityService()
        self.dashboard_service = DashboardService()
        
        # For now, we'll create mock services for the remaining categories
        # These would be implemented similar to the ones above
        self.maintenance_service = None  # MaintenanceService()
        self.operational_service = None  # OperationalService()
        self.financial_service = None    # FinancialService()
        self.compliance_service = None   # ComplianceService()
    
    async def generate_kpi_dashboard(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None,
        update_frequency: int = 300
    ) -> KPIDashboard:
        """Generate comprehensive KPI dashboard with real-time metrics."""
        try:
            # Get all KPI categories concurrently
            system_kpis = await self.system_service.calculate_system_performance_kpis(
                hybrid_service, start_time, end_time, selected_nodes
            )
            network_kpis = await self.network_service.calculate_network_efficiency_kpis(
                hybrid_service, start_time, end_time, selected_nodes
            )
            quality_kpis = await self.quality_service.calculate_quality_kpis(
                hybrid_service, start_time, end_time, selected_nodes
            )
            
            # For now, use mock data for remaining categories
            from .kpi_defaults import (
                get_default_maintenance_kpis, get_default_operational_kpis,
                get_default_financial_kpis, get_default_compliance_kpis
            )
            maintenance_kpis = get_default_maintenance_kpis()
            operational_kpis = get_default_operational_kpis()
            financial_kpis = get_default_financial_kpis()
            compliance_kpis = get_default_compliance_kpis()
            
            # Calculate overall system health
            system_health = calculate_system_health([
                system_kpis, network_kpis, quality_kpis, maintenance_kpis,
                operational_kpis, financial_kpis, compliance_kpis
            ])
            
            # Generate key metrics summary
            key_metrics = self.dashboard_service.generate_key_metrics_summary(
                system_kpis, network_kpis, quality_kpis, maintenance_kpis,
                operational_kpis, financial_kpis, compliance_kpis
            )
            
            return KPIDashboard(
                timestamp=datetime.now(),
                period_start=start_time,
                period_end=end_time,
                selected_nodes=selected_nodes or [],
                system_health=system_health,
                key_metrics=key_metrics,
                system_performance=system_kpis,
                network_efficiency=network_kpis,
                quality_metrics=quality_kpis,
                maintenance_metrics=maintenance_kpis,
                operational_metrics=operational_kpis,
                financial_metrics=financial_kpis,
                compliance_metrics=compliance_kpis,
                update_frequency=update_frequency,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error generating KPI dashboard: {str(e)}")
            raise
    
    async def generate_kpi_cards(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None,
        card_type: str = "summary",
        limit: int = 20
    ) -> List[KPICard]:
        """Generate KPI cards for dashboard display."""
        try:
            # Get dashboard data
            dashboard = await self.generate_kpi_dashboard(
                hybrid_service, start_time, end_time, selected_nodes
            )
            
            cards = []
            
            # Generate cards based on type
            if card_type == "summary" or card_type == "all":
                cards.extend(self.dashboard_service.generate_summary_cards(dashboard))
            
            if card_type == "system" or card_type == "all":
                cards.extend(self.system_service.generate_system_cards(dashboard.system_performance))
            
            if card_type == "network" or card_type == "all":
                cards.extend(self.network_service.generate_network_cards(dashboard.network_efficiency))
            
            if card_type == "quality" or card_type == "all":
                cards.extend(self.quality_service.generate_quality_cards(dashboard.quality_metrics))
            
            # For maintenance, operational, financial, compliance cards
            # These would be implemented when those services are created
            
            return cards[:limit]
            
        except Exception as e:
            self.logger.error(f"Error generating KPI cards: {str(e)}")
            return []
    
    async def generate_kpi_trends(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None,
        kpi_categories: Optional[List[str]] = None,
        resolution: str = "daily"
    ) -> List[KPITrend]:
        """Generate KPI trends over time."""
        try:
            # Generate time points based on resolution
            time_points = generate_time_points(start_time, end_time, resolution)
            
            trends = []
            categories = kpi_categories or [
                "system", "network", "quality", "maintenance",
                "operational", "financial", "compliance"
            ]
            
            for category in categories:
                trend_data = await self.dashboard_service.calculate_kpi_trend_data(
                    hybrid_service, category, time_points, selected_nodes
                )
                
                if trend_data:
                    trends.append(KPITrend(
                        category=category,
                        metric_name=f"{category}_score",
                        time_series=trend_data,
                        trend_direction=calculate_trend_direction(trend_data),
                        change_percentage=calculate_change_percentage(trend_data),
                        period_start=start_time,
                        period_end=end_time
                    ))
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error generating KPI trends: {str(e)}")
            return []
    
    async def generate_kpi_benchmarks(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None,
        benchmark_type: str = "industry"
    ) -> List[KPIBenchmark]:
        """Generate KPI benchmarks for comparison."""
        try:
            # Get current dashboard
            dashboard = await self.generate_kpi_dashboard(
                hybrid_service, start_time, end_time, selected_nodes
            )
            
            benchmarks = []
            
            # Generate benchmarks based on type
            if benchmark_type == "industry":
                benchmarks.extend(self.dashboard_service.generate_industry_benchmarks(dashboard))
            elif benchmark_type == "historical":
                benchmarks.extend(await self.dashboard_service.generate_historical_benchmarks(
                    hybrid_service, dashboard, start_time, end_time, selected_nodes
                ))
            elif benchmark_type == "target":
                benchmarks.extend(self.dashboard_service.generate_target_benchmarks(dashboard))
            
            return benchmarks
            
        except Exception as e:
            self.logger.error(f"Error generating KPI benchmarks: {str(e)}")
            return []
    
    async def generate_kpi_alerts(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> List[KPIAlert]:
        """Generate KPI alerts for monitoring."""
        try:
            # Get current dashboard
            dashboard = await self.generate_kpi_dashboard(
                hybrid_service, start_time, end_time, selected_nodes
            )
            
            alerts = []
            
            # Check alerts from all services
            alerts.extend(self.system_service.check_system_performance_alerts(dashboard.system_performance))
            alerts.extend(self.network_service.check_network_efficiency_alerts(dashboard.network_efficiency))
            alerts.extend(self.quality_service.check_quality_alerts(dashboard.quality_metrics))
            
            # Sort by severity
            return sorted(alerts, key=lambda x: x.severity.value, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error generating KPI alerts: {str(e)}")
            return []
    
    async def generate_kpi_goals(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> List[KPIGoal]:
        """Generate KPI goals and track progress."""
        try:
            # Get current dashboard
            dashboard = await self.generate_kpi_dashboard(
                hybrid_service, start_time, end_time, selected_nodes
            )
            
            goals = []
            
            # Generate goals for each category
            goals.extend(self.system_service.generate_system_performance_goals(dashboard.system_performance))
            goals.extend(self.network_service.generate_network_efficiency_goals(dashboard.network_efficiency))
            goals.extend(self.quality_service.generate_quality_goals(dashboard.quality_metrics))
            
            return goals
            
        except Exception as e:
            self.logger.error(f"Error generating KPI goals: {str(e)}")
            return []
    
    async def generate_kpi_report(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None,
        report_format: str = "json"
    ) -> KPIReport:
        """Generate comprehensive KPI report."""
        try:
            # Get all data concurrently
            dashboard, trends, benchmarks, alerts, goals = await asyncio.gather(
                self.generate_kpi_dashboard(hybrid_service, start_time, end_time, selected_nodes),
                self.generate_kpi_trends(hybrid_service, start_time, end_time, selected_nodes),
                self.generate_kpi_benchmarks(hybrid_service, start_time, end_time, selected_nodes),
                self.generate_kpi_alerts(hybrid_service, start_time, end_time, selected_nodes),
                self.generate_kpi_goals(hybrid_service, start_time, end_time, selected_nodes)
            )
            
            # Generate executive summary
            executive_summary = self.dashboard_service.generate_executive_summary(
                dashboard, trends, benchmarks, alerts, goals
            )
            
            # Generate recommendations
            recommendations = self.dashboard_service.generate_kpi_recommendations(
                dashboard, trends, benchmarks, alerts, goals
            )
            
            return KPIReport(
                report_id=f"kpi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="KPI Performance Report",
                description="Comprehensive analysis of key performance indicators",
                period_start=start_time,
                period_end=end_time,
                selected_nodes=selected_nodes or [],
                executive_summary=executive_summary,
                dashboard=dashboard,
                trends=trends,
                benchmarks=benchmarks,
                alerts=alerts,
                goals=goals,
                recommendations=recommendations,
                report_format=ReportFormat(report_format),
                generated_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error generating KPI report: {str(e)}")
            raise
    
    async def compare_kpi_periods(
        self,
        hybrid_service: HybridDataService,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> KPIComparison:
        """Compare KPIs between two time periods."""
        try:
            # Get dashboards for both periods
            dashboard1, dashboard2 = await asyncio.gather(
                self.generate_kpi_dashboard(hybrid_service, period1_start, period1_end, selected_nodes),
                self.generate_kpi_dashboard(hybrid_service, period2_start, period2_end, selected_nodes)
            )
            
            # Calculate improvements and regressions
            improvements = calculate_kpi_improvements(dashboard1, dashboard2)
            regressions = calculate_kpi_regressions(dashboard1, dashboard2)
            
            # Calculate overall change
            overall_change_percentage = calculate_overall_change_percentage(dashboard1, dashboard2)
            
            # Generate insights
            insights = generate_period_comparison_insights(
                dashboard1, dashboard2, improvements, regressions
            )
            
            return KPIComparison(
                period1_start=period1_start,
                period1_end=period1_end,
                period2_start=period2_start,
                period2_end=period2_end,
                selected_nodes=selected_nodes or [],
                period1_dashboard=dashboard1,
                period2_dashboard=dashboard2,
                improvements=improvements,
                regressions=regressions,
                overall_change_percentage=overall_change_percentage,
                insights=insights,
                compared_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error comparing KPI periods: {str(e)}")
            raise
    
    async def get_kpi_configuration(
        self,
        hybrid_service: HybridDataService,
        configuration_type: str = "default"
    ) -> KPIConfiguration:
        """Get KPI configuration settings."""
        try:
            # Load configuration from database or use defaults
            config_data = await hybrid_service.get_kpi_configuration(configuration_type)
            
            if not config_data:
                return get_default_kpi_configuration_object()
            
            return KPIConfiguration(
                configuration_id=config_data.get("id", "default"),
                name=config_data.get("name", "Default KPI Configuration"),
                description=config_data.get("description", "Default KPI configuration settings"),
                thresholds=config_data.get("thresholds", {}),
                alert_rules=config_data.get("alert_rules", {}),
                goal_targets=config_data.get("goal_targets", {}),
                benchmark_settings=config_data.get("benchmark_settings", {}),
                update_frequency=config_data.get("update_frequency", 300),
                is_active=config_data.get("is_active", True),
                created_at=datetime.fromisoformat(config_data.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(config_data.get("updated_at", datetime.now().isoformat()))
            )
            
        except Exception as e:
            self.logger.error(f"Error getting KPI configuration: {str(e)}")
            return get_default_kpi_configuration_object()
    
    async def get_kpi_health(
        self,
        hybrid_service: HybridDataService,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> KPIHealth:
        """Get overall KPI system health status."""
        try:
            # Get current dashboard
            dashboard = await self.generate_kpi_dashboard(
                hybrid_service, start_time, end_time, selected_nodes
            )
            
            # Calculate health metrics
            overall_health_score = dashboard.system_health
            data_quality_score = calculate_data_quality_score(dashboard)
            system_availability = dashboard.system_performance.availability_percentage
            
            # Get component health
            component_health = calculate_component_health(dashboard)
            
            # Generate health status
            health_status = determine_health_status(overall_health_score)
            
            # Generate health insights
            health_insights = generate_health_insights(dashboard, component_health)
            
            return KPIHealth(
                overall_health_score=overall_health_score,
                health_status=health_status,
                data_quality_score=data_quality_score,
                system_availability=system_availability,
                component_health=component_health,
                health_insights=health_insights,
                last_updated=datetime.now(),
                period_start=start_time,
                period_end=end_time
            )
            
        except Exception as e:
            self.logger.error(f"Error getting KPI health: {str(e)}")
            raise 
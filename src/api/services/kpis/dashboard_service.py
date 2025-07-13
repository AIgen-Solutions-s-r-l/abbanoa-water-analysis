"""
Dashboard Service.

This service handles KPI dashboard generation, trends, alerts, and reports.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from src.schemas.api.kpis import (
    KPIDashboard, KPIMetric, KPICard, KPITrend, KPIBenchmark, KPIAlert, KPIGoal,
    KPIReport, KPIComparison, KPIHealth, TrendDirection, BenchmarkType, ReportFormat
)
from src.infrastructure.data.hybrid_data_service import HybridDataService
from .kpi_utils import (
    calculate_system_health, generate_time_points, calculate_trend_direction,
    calculate_change_percentage, calculate_kpi_improvements, calculate_kpi_regressions,
    calculate_overall_change_percentage, generate_period_comparison_insights,
    calculate_data_quality_score, calculate_component_health, determine_health_status,
    generate_health_insights, create_kpi_benchmark
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for KPI dashboard, trends, alerts, and reports generation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_key_metrics_summary(
        self,
        system_kpis, network_kpis, quality_kpis, maintenance_kpis,
        operational_kpis, financial_kpis, compliance_kpis
    ) -> List[KPIMetric]:
        """Generate key metrics summary."""
        return [
            KPIMetric(
                name="System Uptime",
                value=system_kpis.uptime_percentage,
                unit="percentage",
                category="system",
                trend=TrendDirection.stable,
                timestamp=datetime.now()
            ),
            KPIMetric(
                name="Water Loss",
                value=network_kpis.water_loss_percentage,
                unit="percentage",
                category="network",
                trend=TrendDirection.decreasing,
                timestamp=datetime.now()
            ),
            KPIMetric(
                name="Quality Compliance",
                value=quality_kpis.quality_compliance_percentage,
                unit="percentage",
                category="quality",
                trend=TrendDirection.increasing,
                timestamp=datetime.now()
            ),
            KPIMetric(
                name="Maintenance Efficiency",
                value=maintenance_kpis.maintenance_efficiency_score,
                unit="score",
                category="maintenance",
                trend=TrendDirection.stable,
                timestamp=datetime.now()
            )
        ]
    
    def generate_summary_cards(self, dashboard: KPIDashboard) -> List[KPICard]:
        """Generate summary KPI cards."""
        from src.schemas.api.kpis import KPICard
        
        return [
            KPICard(
                title="System Health",
                value=dashboard.system_health,
                unit="score",
                category="summary",
                trend=TrendDirection.stable,
                change_percentage=0.0,
                status="good" if dashboard.system_health >= 80 else "warning",
                description="Overall system health score"
            ),
            KPICard(
                title="Network Efficiency",
                value=dashboard.network_efficiency.overall_efficiency_score,
                unit="score",
                category="summary",
                trend=TrendDirection.increasing,
                change_percentage=2.5,
                status="good" if dashboard.network_efficiency.overall_efficiency_score >= 75 else "warning",
                description="Overall network efficiency score"
            ),
            KPICard(
                title="Quality Score",
                value=dashboard.quality_metrics.quality_score,
                unit="score",
                category="summary",
                trend=TrendDirection.stable,
                change_percentage=0.0,
                status="good" if dashboard.quality_metrics.quality_score >= 85 else "warning",
                description="Overall quality score"
            )
        ]
    
    async def calculate_kpi_trend_data(
        self,
        hybrid_service: HybridDataService,
        category: str,
        time_points: List[datetime],
        selected_nodes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Calculate KPI trend data for a specific category."""
        trend_data = []
        
        for i, time_point in enumerate(time_points[:-1]):
            end_time = time_points[i + 1]
            
            # Mock calculation - replace with actual logic
            if category == "system":
                value = 85.0 + (i * 0.5)  # Slight upward trend
            elif category == "network":
                value = 80.0 + (i * 0.3)  # Gradual improvement
            elif category == "quality":
                value = 95.0 - (i * 0.1)  # Slight decline
            elif category == "maintenance":
                value = 90.0 + (i * 0.2)  # Steady improvement
            elif category == "operational":
                value = 88.0 + (i * 0.4)  # Good improvement
            elif category == "financial":
                value = 75.0 + (i * 0.6)  # Strong improvement
            elif category == "compliance":
                value = 98.0 - (i * 0.05)  # Very stable
            else:
                value = 80.0
            
            trend_data.append({
                "timestamp": time_point,
                "value": value
            })
        
        return trend_data
    
    def generate_industry_benchmarks(self, dashboard: KPIDashboard) -> List[KPIBenchmark]:
        """Generate industry benchmarks."""
        return [
            create_kpi_benchmark(
                category="system",
                metric_name="uptime_percentage",
                current_value=dashboard.system_performance.uptime_percentage,
                benchmark_value=99.9,
                benchmark_type=BenchmarkType.industry
            ),
            create_kpi_benchmark(
                category="network",
                metric_name="water_loss_percentage",
                current_value=dashboard.network_efficiency.water_loss_percentage,
                benchmark_value=10.0,
                benchmark_type=BenchmarkType.industry
            ),
            create_kpi_benchmark(
                category="quality",
                metric_name="quality_compliance_percentage",
                current_value=dashboard.quality_metrics.quality_compliance_percentage,
                benchmark_value=95.0,
                benchmark_type=BenchmarkType.industry
            )
        ]
    
    async def generate_historical_benchmarks(
        self,
        hybrid_service: HybridDataService,
        dashboard: KPIDashboard,
        start_time: datetime,
        end_time: datetime,
        selected_nodes: Optional[List[str]] = None
    ) -> List[KPIBenchmark]:
        """Generate historical benchmarks."""
        # Get historical data from same period last year
        historical_start = start_time - timedelta(days=365)
        historical_end = end_time - timedelta(days=365)
        
        # Mock historical values - replace with actual data retrieval
        return [
            create_kpi_benchmark(
                category="system",
                metric_name="uptime_percentage",
                current_value=dashboard.system_performance.uptime_percentage,
                benchmark_value=98.5,
                benchmark_type=BenchmarkType.historical
            ),
            create_kpi_benchmark(
                category="network",
                metric_name="water_loss_percentage",
                current_value=dashboard.network_efficiency.water_loss_percentage,
                benchmark_value=18.0,
                benchmark_type=BenchmarkType.historical
            )
        ]
    
    def generate_target_benchmarks(self, dashboard: KPIDashboard) -> List[KPIBenchmark]:
        """Generate target benchmarks."""
        return [
            create_kpi_benchmark(
                category="system",
                metric_name="uptime_percentage",
                current_value=dashboard.system_performance.uptime_percentage,
                benchmark_value=99.5,
                benchmark_type=BenchmarkType.target
            ),
            create_kpi_benchmark(
                category="network",
                metric_name="water_loss_percentage",
                current_value=dashboard.network_efficiency.water_loss_percentage,
                benchmark_value=12.0,
                benchmark_type=BenchmarkType.target
            )
        ]
    
    def generate_executive_summary(
        self,
        dashboard: KPIDashboard,
        trends: List[KPITrend],
        benchmarks: List[KPIBenchmark],
        alerts: List[KPIAlert],
        goals: List[KPIGoal]
    ) -> str:
        """Generate executive summary for KPI report."""
        from src.schemas.api.kpis import AlertLevel, GoalStatus
        
        high_alerts = len([a for a in alerts if a.severity == AlertLevel.high])
        on_track_goals = len([g for g in goals if g.status == GoalStatus.on_track])
        total_goals = len(goals)
        
        return f"""
        Executive Summary - KPI Performance Report
        
        Overall System Health: {dashboard.system_health:.1f}/100
        
        Key Highlights:
        • System uptime: {dashboard.system_performance.uptime_percentage:.1f}%
        • Water loss: {dashboard.network_efficiency.water_loss_percentage:.1f}%
        • Quality compliance: {dashboard.quality_metrics.quality_compliance_percentage:.1f}%
        • Maintenance efficiency: {dashboard.maintenance_metrics.maintenance_efficiency_score:.1f}
        
        Alerts Status:
        • {high_alerts} high-priority alerts requiring immediate attention
        • {len(alerts) - high_alerts} medium/low priority alerts
        
        Goals Progress:
        • {on_track_goals}/{total_goals} goals are on track
        • {total_goals - on_track_goals} goals require attention
        
        Trend Analysis:
        • {len([t for t in trends if t.trend_direction == TrendDirection.increasing])} metrics showing improvement
        • {len([t for t in trends if t.trend_direction == TrendDirection.decreasing])} metrics showing decline
        • {len([t for t in trends if t.trend_direction == TrendDirection.stable])} metrics stable
        """
    
    def generate_kpi_recommendations(
        self,
        dashboard: KPIDashboard,
        trends: List[KPITrend],
        benchmarks: List[KPIBenchmark],
        alerts: List[KPIAlert],
        goals: List[KPIGoal]
    ) -> List[str]:
        """Generate KPI recommendations."""
        recommendations = []
        
        # System recommendations
        if dashboard.system_performance.uptime_percentage < 99.0:
            recommendations.append("Implement redundancy measures to improve system uptime")
        
        # Network recommendations
        if dashboard.network_efficiency.water_loss_percentage > 15.0:
            recommendations.append("Conduct network leak detection and repair campaign")
        
        # Quality recommendations
        if dashboard.quality_metrics.quality_compliance_percentage < 95.0:
            recommendations.append("Enhance water quality monitoring and treatment processes")
        
        # Maintenance recommendations
        if dashboard.maintenance_metrics.preventive_maintenance_percentage < 70.0:
            recommendations.append("Increase preventive maintenance activities to reduce reactive repairs")
        
        # Financial recommendations
        if dashboard.financial_metrics.cost_savings_percentage < 5.0:
            recommendations.append("Implement energy efficiency and cost optimization initiatives")
        
        # Compliance recommendations
        if dashboard.compliance_metrics.regulatory_compliance_percentage < 98.0:
            recommendations.append("Strengthen compliance monitoring and reporting processes")
        
        return recommendations 
"""
KPI Service Module.

This module provides comprehensive business logic for KPI calculations,
dashboard generation, alerts, and performance monitoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import pandas as pd
import numpy as np
from statistics import mean, median, stdev

from src.schemas.api.kpis import (
    KPIDashboard,
    KPIMetric,
    KPICard,
    SystemPerformanceKPIs,
    NetworkEfficiencyKPIs,
    QualityKPIs,
    MaintenanceKPIs,
    OperationalKPIs,
    FinancialKPIs,
    ComplianceKPIs,
    KPITrend,
    KPIBenchmark,
    KPIAlert,
    KPIGoal,
    KPIReport,
    KPIComparison,
    KPIConfiguration,
    KPIHealth,
    AlertLevel,
    TrendDirection,
    BenchmarkType,
    GoalStatus,
    ReportFormat
)
from src.infrastructure.data.hybrid_data_service import HybridDataService

logger = logging.getLogger(__name__)


async def generate_kpi_dashboard(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None,
    update_frequency: int = 300
) -> KPIDashboard:
    """
    Generate comprehensive KPI dashboard with real-time metrics.
    
    Args:
        hybrid_service: Data service instance
        start_time: Start time for analysis
        end_time: End time for analysis
        selected_nodes: Optional list of nodes to analyze
        update_frequency: Update frequency in seconds
        
    Returns:
        KPIDashboard: Complete dashboard with all KPI categories
    """
    try:
        # Get all KPI categories concurrently
        system_kpis, network_kpis, quality_kpis, maintenance_kpis, operational_kpis, financial_kpis, compliance_kpis = await asyncio.gather(
            calculate_system_performance_kpis(hybrid_service, start_time, end_time, selected_nodes),
            calculate_network_efficiency_kpis(hybrid_service, start_time, end_time, selected_nodes),
            calculate_quality_kpis(hybrid_service, start_time, end_time, selected_nodes),
            calculate_maintenance_kpis(hybrid_service, start_time, end_time, selected_nodes),
            calculate_operational_kpis(hybrid_service, start_time, end_time, selected_nodes),
            calculate_financial_kpis(hybrid_service, start_time, end_time, selected_nodes),
            calculate_compliance_kpis(hybrid_service, start_time, end_time, selected_nodes)
        )
        
        # Calculate overall system health
        system_health = _calculate_system_health([
            system_kpis, network_kpis, quality_kpis, maintenance_kpis,
            operational_kpis, financial_kpis, compliance_kpis
        ])
        
        # Generate key metrics summary
        key_metrics = _generate_key_metrics_summary(
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
        logger.error(f"Error generating KPI dashboard: {str(e)}")
        raise


async def calculate_system_performance_kpis(
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
            return _get_default_system_performance_kpis()
        
        # Calculate uptime
        uptime_percentage = _calculate_uptime_percentage(system_data)
        
        # Calculate response time
        response_time = _calculate_average_response_time(system_data)
        
        # Calculate throughput
        throughput = _calculate_system_throughput(system_data)
        
        # Calculate error rate
        error_rate = _calculate_error_rate(system_data)
        
        # Calculate resource utilization
        cpu_utilization = _calculate_cpu_utilization(system_data)
        memory_utilization = _calculate_memory_utilization(system_data)
        
        # Calculate availability
        availability = _calculate_system_availability(system_data)
        
        # Calculate performance score
        performance_score = _calculate_performance_score(
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
        logger.error(f"Error calculating system performance KPIs: {str(e)}")
        return _get_default_system_performance_kpis()


async def calculate_network_efficiency_kpis(
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
            return _get_default_network_efficiency_kpis()
        
        # Calculate water loss
        water_loss_percentage = _calculate_water_loss_percentage(network_data)
        
        # Calculate pressure efficiency
        pressure_efficiency = _calculate_pressure_efficiency(network_data)
        
        # Calculate flow efficiency
        flow_efficiency = _calculate_flow_efficiency(network_data)
        
        # Calculate energy efficiency
        energy_efficiency = _calculate_energy_efficiency(network_data)
        
        # Calculate network coverage
        network_coverage = _calculate_network_coverage(network_data)
        
        # Calculate distribution efficiency
        distribution_efficiency = _calculate_distribution_efficiency(network_data)
        
        # Calculate overall efficiency score
        overall_efficiency_score = _calculate_overall_efficiency_score(
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
        logger.error(f"Error calculating network efficiency KPIs: {str(e)}")
        return _get_default_network_efficiency_kpis()


async def calculate_quality_kpis(
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
            return _get_default_quality_kpis()
        
        # Calculate quality compliance
        quality_compliance = _calculate_quality_compliance(quality_data)
        
        # Calculate contamination incidents
        contamination_incidents = _calculate_contamination_incidents(quality_data)
        
        # Calculate temperature compliance
        temperature_compliance = _calculate_temperature_compliance(quality_data)
        
        # Calculate pressure compliance
        pressure_compliance = _calculate_pressure_compliance(quality_data)
        
        # Calculate flow rate compliance
        flow_rate_compliance = _calculate_flow_rate_compliance(quality_data)
        
        # Calculate quality score
        quality_score = _calculate_quality_score(
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
        logger.error(f"Error calculating quality KPIs: {str(e)}")
        return _get_default_quality_kpis()


async def calculate_maintenance_kpis(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> MaintenanceKPIs:
    """Calculate maintenance KPIs."""
    try:
        # Get maintenance data
        maintenance_data = await hybrid_service.get_maintenance_data(
            start_time, end_time, selected_nodes
        )
        
        if not maintenance_data:
            return _get_default_maintenance_kpis()
        
        # Calculate maintenance metrics
        preventive_maintenance_percentage = _calculate_preventive_maintenance_percentage(maintenance_data)
        mean_time_to_repair = _calculate_mean_time_to_repair(maintenance_data)
        mean_time_between_failures = _calculate_mean_time_between_failures(maintenance_data)
        maintenance_cost_per_unit = _calculate_maintenance_cost_per_unit(maintenance_data)
        scheduled_maintenance_completion = _calculate_scheduled_maintenance_completion(maintenance_data)
        equipment_reliability = _calculate_equipment_reliability(maintenance_data)
        maintenance_efficiency_score = _calculate_maintenance_efficiency_score(
            preventive_maintenance_percentage, mean_time_to_repair,
            mean_time_between_failures, scheduled_maintenance_completion,
            equipment_reliability
        )
        
        return MaintenanceKPIs(
            preventive_maintenance_percentage=preventive_maintenance_percentage,
            mean_time_to_repair_hours=mean_time_to_repair,
            mean_time_between_failures_hours=mean_time_between_failures,
            maintenance_cost_per_unit=maintenance_cost_per_unit,
            scheduled_maintenance_completion_percentage=scheduled_maintenance_completion,
            equipment_reliability_percentage=equipment_reliability,
            maintenance_efficiency_score=maintenance_efficiency_score,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error calculating maintenance KPIs: {str(e)}")
        return _get_default_maintenance_kpis()


async def calculate_operational_kpis(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> OperationalKPIs:
    """Calculate operational KPIs."""
    try:
        # Get operational data
        operational_data = await hybrid_service.get_operational_data(
            start_time, end_time, selected_nodes
        )
        
        if not operational_data:
            return _get_default_operational_kpis()
        
        # Calculate operational metrics
        service_availability = _calculate_service_availability(operational_data)
        customer_satisfaction = _calculate_customer_satisfaction(operational_data)
        response_time_to_incidents = _calculate_response_time_to_incidents(operational_data)
        resource_utilization = _calculate_resource_utilization(operational_data)
        process_efficiency = _calculate_process_efficiency(operational_data)
        capacity_utilization = _calculate_capacity_utilization(operational_data)
        operational_efficiency_score = _calculate_operational_efficiency_score(
            service_availability, customer_satisfaction, response_time_to_incidents,
            resource_utilization, process_efficiency, capacity_utilization
        )
        
        return OperationalKPIs(
            service_availability_percentage=service_availability,
            customer_satisfaction_score=customer_satisfaction,
            response_time_to_incidents_minutes=response_time_to_incidents,
            resource_utilization_percentage=resource_utilization,
            process_efficiency_percentage=process_efficiency,
            capacity_utilization_percentage=capacity_utilization,
            operational_efficiency_score=operational_efficiency_score,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error calculating operational KPIs: {str(e)}")
        return _get_default_operational_kpis()


async def calculate_financial_kpis(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> FinancialKPIs:
    """Calculate financial KPIs."""
    try:
        # Get financial data
        financial_data = await hybrid_service.get_financial_data(
            start_time, end_time, selected_nodes
        )
        
        if not financial_data:
            return _get_default_financial_kpis()
        
        # Calculate financial metrics
        operational_cost_per_unit = _calculate_operational_cost_per_unit(financial_data)
        energy_cost_per_unit = _calculate_energy_cost_per_unit(financial_data)
        maintenance_cost_percentage = _calculate_maintenance_cost_percentage(financial_data)
        revenue_per_unit = _calculate_revenue_per_unit(financial_data)
        cost_savings_percentage = _calculate_cost_savings_percentage(financial_data)
        roi_percentage = _calculate_roi_percentage(financial_data)
        financial_efficiency_score = _calculate_financial_efficiency_score(
            operational_cost_per_unit, energy_cost_per_unit,
            maintenance_cost_percentage, revenue_per_unit,
            cost_savings_percentage, roi_percentage
        )
        
        return FinancialKPIs(
            operational_cost_per_unit=operational_cost_per_unit,
            energy_cost_per_unit=energy_cost_per_unit,
            maintenance_cost_percentage=maintenance_cost_percentage,
            revenue_per_unit=revenue_per_unit,
            cost_savings_percentage=cost_savings_percentage,
            roi_percentage=roi_percentage,
            financial_efficiency_score=financial_efficiency_score,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error calculating financial KPIs: {str(e)}")
        return _get_default_financial_kpis()


async def calculate_compliance_kpis(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> ComplianceKPIs:
    """Calculate compliance KPIs."""
    try:
        # Get compliance data
        compliance_data = await hybrid_service.get_compliance_data(
            start_time, end_time, selected_nodes
        )
        
        if not compliance_data:
            return _get_default_compliance_kpis()
        
        # Calculate compliance metrics
        regulatory_compliance = _calculate_regulatory_compliance(compliance_data)
        safety_compliance = _calculate_safety_compliance(compliance_data)
        environmental_compliance = _calculate_environmental_compliance(compliance_data)
        reporting_compliance = _calculate_reporting_compliance(compliance_data)
        audit_score = _calculate_audit_score(compliance_data)
        violations_count = _calculate_violations_count(compliance_data)
        compliance_efficiency_score = _calculate_compliance_efficiency_score(
            regulatory_compliance, safety_compliance, environmental_compliance,
            reporting_compliance, audit_score, violations_count
        )
        
        return ComplianceKPIs(
            regulatory_compliance_percentage=regulatory_compliance,
            safety_compliance_percentage=safety_compliance,
            environmental_compliance_percentage=environmental_compliance,
            reporting_compliance_percentage=reporting_compliance,
            audit_score=audit_score,
            violations_count=violations_count,
            compliance_efficiency_score=compliance_efficiency_score,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error calculating compliance KPIs: {str(e)}")
        return _get_default_compliance_kpis()


async def generate_kpi_cards(
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
        dashboard = await generate_kpi_dashboard(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        cards = []
        
        # Generate cards based on type
        if card_type == "summary" or card_type == "all":
            cards.extend(_generate_summary_cards(dashboard))
        
        if card_type == "system" or card_type == "all":
            cards.extend(_generate_system_cards(dashboard.system_performance))
        
        if card_type == "network" or card_type == "all":
            cards.extend(_generate_network_cards(dashboard.network_efficiency))
        
        if card_type == "quality" or card_type == "all":
            cards.extend(_generate_quality_cards(dashboard.quality_metrics))
        
        if card_type == "maintenance" or card_type == "all":
            cards.extend(_generate_maintenance_cards(dashboard.maintenance_metrics))
        
        if card_type == "operational" or card_type == "all":
            cards.extend(_generate_operational_cards(dashboard.operational_metrics))
        
        if card_type == "financial" or card_type == "all":
            cards.extend(_generate_financial_cards(dashboard.financial_metrics))
        
        if card_type == "compliance" or card_type == "all":
            cards.extend(_generate_compliance_cards(dashboard.compliance_metrics))
        
        return cards[:limit]
        
    except Exception as e:
        logger.error(f"Error generating KPI cards: {str(e)}")
        return []


async def generate_kpi_trends(
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
        time_points = _generate_time_points(start_time, end_time, resolution)
        
        trends = []
        categories = kpi_categories or [
            "system", "network", "quality", "maintenance",
            "operational", "financial", "compliance"
        ]
        
        for category in categories:
            trend_data = await _calculate_kpi_trend_data(
                hybrid_service, category, time_points, selected_nodes
            )
            
            if trend_data:
                trends.append(KPITrend(
                    category=category,
                    metric_name=f"{category}_score",
                    time_series=trend_data,
                    trend_direction=_calculate_trend_direction(trend_data),
                    change_percentage=_calculate_change_percentage(trend_data),
                    period_start=start_time,
                    period_end=end_time
                ))
        
        return trends
        
    except Exception as e:
        logger.error(f"Error generating KPI trends: {str(e)}")
        return []


async def generate_kpi_benchmarks(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None,
    benchmark_type: str = "industry"
) -> List[KPIBenchmark]:
    """Generate KPI benchmarks for comparison."""
    try:
        # Get current dashboard
        dashboard = await generate_kpi_dashboard(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        benchmarks = []
        
        # Generate benchmarks based on type
        if benchmark_type == "industry":
            benchmarks.extend(_generate_industry_benchmarks(dashboard))
        elif benchmark_type == "historical":
            benchmarks.extend(await _generate_historical_benchmarks(
                hybrid_service, dashboard, start_time, end_time, selected_nodes
            ))
        elif benchmark_type == "target":
            benchmarks.extend(_generate_target_benchmarks(dashboard))
        
        return benchmarks
        
    except Exception as e:
        logger.error(f"Error generating KPI benchmarks: {str(e)}")
        return []


async def generate_kpi_alerts(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> List[KPIAlert]:
    """Generate KPI alerts for monitoring."""
    try:
        # Get current dashboard
        dashboard = await generate_kpi_dashboard(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        alerts = []
        
        # Check system performance alerts
        alerts.extend(_check_system_performance_alerts(dashboard.system_performance))
        
        # Check network efficiency alerts
        alerts.extend(_check_network_efficiency_alerts(dashboard.network_efficiency))
        
        # Check quality alerts
        alerts.extend(_check_quality_alerts(dashboard.quality_metrics))
        
        # Check maintenance alerts
        alerts.extend(_check_maintenance_alerts(dashboard.maintenance_metrics))
        
        # Check operational alerts
        alerts.extend(_check_operational_alerts(dashboard.operational_metrics))
        
        # Check financial alerts
        alerts.extend(_check_financial_alerts(dashboard.financial_metrics))
        
        # Check compliance alerts
        alerts.extend(_check_compliance_alerts(dashboard.compliance_metrics))
        
        return sorted(alerts, key=lambda x: x.severity.value, reverse=True)
        
    except Exception as e:
        logger.error(f"Error generating KPI alerts: {str(e)}")
        return []


async def generate_kpi_goals(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> List[KPIGoal]:
    """Generate KPI goals and track progress."""
    try:
        # Get current dashboard
        dashboard = await generate_kpi_dashboard(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        goals = []
        
        # Generate goals for each category
        goals.extend(_generate_system_performance_goals(dashboard.system_performance))
        goals.extend(_generate_network_efficiency_goals(dashboard.network_efficiency))
        goals.extend(_generate_quality_goals(dashboard.quality_metrics))
        goals.extend(_generate_maintenance_goals(dashboard.maintenance_metrics))
        goals.extend(_generate_operational_goals(dashboard.operational_metrics))
        goals.extend(_generate_financial_goals(dashboard.financial_metrics))
        goals.extend(_generate_compliance_goals(dashboard.compliance_metrics))
        
        return goals
        
    except Exception as e:
        logger.error(f"Error generating KPI goals: {str(e)}")
        return []


async def generate_kpi_report(
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
            generate_kpi_dashboard(hybrid_service, start_time, end_time, selected_nodes),
            generate_kpi_trends(hybrid_service, start_time, end_time, selected_nodes),
            generate_kpi_benchmarks(hybrid_service, start_time, end_time, selected_nodes),
            generate_kpi_alerts(hybrid_service, start_time, end_time, selected_nodes),
            generate_kpi_goals(hybrid_service, start_time, end_time, selected_nodes)
        )
        
        # Generate executive summary
        executive_summary = _generate_executive_summary(
            dashboard, trends, benchmarks, alerts, goals
        )
        
        # Generate recommendations
        recommendations = _generate_kpi_recommendations(
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
        logger.error(f"Error generating KPI report: {str(e)}")
        raise


async def compare_kpi_periods(
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
            generate_kpi_dashboard(hybrid_service, period1_start, period1_end, selected_nodes),
            generate_kpi_dashboard(hybrid_service, period2_start, period2_end, selected_nodes)
        )
        
        # Calculate improvements and regressions
        improvements = _calculate_kpi_improvements(dashboard1, dashboard2)
        regressions = _calculate_kpi_regressions(dashboard1, dashboard2)
        
        # Calculate overall change
        overall_change_percentage = _calculate_overall_change_percentage(dashboard1, dashboard2)
        
        # Generate insights
        insights = _generate_period_comparison_insights(
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
        logger.error(f"Error comparing KPI periods: {str(e)}")
        raise


async def get_kpi_configuration(
    hybrid_service: HybridDataService,
    configuration_type: str = "default"
) -> KPIConfiguration:
    """Get KPI configuration settings."""
    try:
        # Load configuration from database or use defaults
        config_data = await hybrid_service.get_kpi_configuration(configuration_type)
        
        if not config_data:
            config_data = _get_default_kpi_configuration()
        
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
        logger.error(f"Error getting KPI configuration: {str(e)}")
        return _get_default_kpi_configuration_object()


async def get_kpi_health(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> KPIHealth:
    """Get overall KPI system health status."""
    try:
        # Get current dashboard
        dashboard = await generate_kpi_dashboard(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        # Calculate health metrics
        overall_health_score = dashboard.system_health
        data_quality_score = _calculate_data_quality_score(dashboard)
        system_availability = dashboard.system_performance.availability_percentage
        
        # Get component health
        component_health = _calculate_component_health(dashboard)
        
        # Generate health status
        health_status = _determine_health_status(overall_health_score)
        
        # Generate health insights
        health_insights = _generate_health_insights(dashboard, component_health)
        
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
        logger.error(f"Error getting KPI health: {str(e)}")
        raise


# Helper functions (implementation details)

def _calculate_system_health(kpi_categories: List[Any]) -> float:
    """Calculate overall system health score."""
    scores = []
    for category in kpi_categories:
        if hasattr(category, 'performance_score'):
            scores.append(category.performance_score)
        elif hasattr(category, 'overall_efficiency_score'):
            scores.append(category.overall_efficiency_score)
        elif hasattr(category, 'quality_score'):
            scores.append(category.quality_score)
        elif hasattr(category, 'maintenance_efficiency_score'):
            scores.append(category.maintenance_efficiency_score)
        elif hasattr(category, 'operational_efficiency_score'):
            scores.append(category.operational_efficiency_score)
        elif hasattr(category, 'financial_efficiency_score'):
            scores.append(category.financial_efficiency_score)
        elif hasattr(category, 'compliance_efficiency_score'):
            scores.append(category.compliance_efficiency_score)
    
    return mean(scores) if scores else 0.0


def _generate_key_metrics_summary(
    system_kpis: SystemPerformanceKPIs,
    network_kpis: NetworkEfficiencyKPIs,
    quality_kpis: QualityKPIs,
    maintenance_kpis: MaintenanceKPIs,
    operational_kpis: OperationalKPIs,
    financial_kpis: FinancialKPIs,
    compliance_kpis: ComplianceKPIs
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


def _calculate_uptime_percentage(system_data: Any) -> float:
    """Calculate system uptime percentage."""
    # Mock calculation - replace with actual logic
    return 99.5


def _calculate_average_response_time(system_data: Any) -> float:
    """Calculate average response time in milliseconds."""
    # Mock calculation - replace with actual logic
    return 150.0


def _calculate_system_throughput(system_data: Any) -> float:
    """Calculate system throughput in requests per second."""
    # Mock calculation - replace with actual logic
    return 1000.0


def _calculate_error_rate(system_data: Any) -> float:
    """Calculate error rate percentage."""
    # Mock calculation - replace with actual logic
    return 0.1


def _calculate_cpu_utilization(system_data: Any) -> float:
    """Calculate CPU utilization percentage."""
    # Mock calculation - replace with actual logic
    return 65.0


def _calculate_memory_utilization(system_data: Any) -> float:
    """Calculate memory utilization percentage."""
    # Mock calculation - replace with actual logic
    return 70.0


def _calculate_system_availability(system_data: Any) -> float:
    """Calculate system availability percentage."""
    # Mock calculation - replace with actual logic
    return 99.9


def _calculate_performance_score(
    uptime: float, response_time: float, throughput: float, error_rate: float
) -> float:
    """Calculate overall performance score."""
    # Weighted scoring algorithm
    uptime_score = uptime
    response_score = max(0, 100 - (response_time / 10))
    throughput_score = min(100, throughput / 10)
    error_score = max(0, 100 - (error_rate * 10))
    
    return (uptime_score * 0.3 + response_score * 0.2 + 
            throughput_score * 0.2 + error_score * 0.3)


def _calculate_water_loss_percentage(network_data: Any) -> float:
    """Calculate water loss percentage."""
    # Mock calculation - replace with actual logic
    return 15.0


def _calculate_pressure_efficiency(network_data: Any) -> float:
    """Calculate pressure efficiency."""
    # Mock calculation - replace with actual logic
    return 85.0


def _calculate_flow_efficiency(network_data: Any) -> float:
    """Calculate flow efficiency."""
    # Mock calculation - replace with actual logic
    return 90.0


def _calculate_energy_efficiency(network_data: Any) -> float:
    """Calculate energy efficiency."""
    # Mock calculation - replace with actual logic
    return 80.0


def _calculate_network_coverage(network_data: Any) -> float:
    """Calculate network coverage."""
    # Mock calculation - replace with actual logic
    return 95.0


def _calculate_distribution_efficiency(network_data: Any) -> float:
    """Calculate distribution efficiency."""
    # Mock calculation - replace with actual logic
    return 88.0


def _calculate_overall_efficiency_score(
    water_loss: float, pressure_eff: float, flow_eff: float,
    energy_eff: float, distribution_eff: float
) -> float:
    """Calculate overall efficiency score."""
    # Weighted scoring algorithm
    water_loss_score = max(0, 100 - water_loss)
    
    return (water_loss_score * 0.3 + pressure_eff * 0.2 + 
            flow_eff * 0.2 + energy_eff * 0.15 + distribution_eff * 0.15)


# Default KPI objects for error handling

def _get_default_system_performance_kpis() -> SystemPerformanceKPIs:
    """Get default system performance KPIs."""
    return SystemPerformanceKPIs(
        uptime_percentage=0.0,
        response_time_ms=0.0,
        throughput_requests_per_second=0.0,
        error_rate_percentage=0.0,
        cpu_utilization_percentage=0.0,
        memory_utilization_percentage=0.0,
        availability_percentage=0.0,
        performance_score=0.0,
        timestamp=datetime.now()
    )


def _get_default_network_efficiency_kpis() -> NetworkEfficiencyKPIs:
    """Get default network efficiency KPIs."""
    return NetworkEfficiencyKPIs(
        water_loss_percentage=0.0,
        pressure_efficiency_percentage=0.0,
        flow_efficiency_percentage=0.0,
        energy_efficiency_percentage=0.0,
        network_coverage_percentage=0.0,
        distribution_efficiency_percentage=0.0,
        overall_efficiency_score=0.0,
        timestamp=datetime.now()
    )


def _get_default_quality_kpis() -> QualityKPIs:
    """Get default quality KPIs."""
    return QualityKPIs(
        quality_compliance_percentage=0.0,
        contamination_incidents_count=0,
        temperature_compliance_percentage=0.0,
        pressure_compliance_percentage=0.0,
        flow_rate_compliance_percentage=0.0,
        quality_score=0.0,
        timestamp=datetime.now()
    )


def _get_default_maintenance_kpis() -> MaintenanceKPIs:
    """Get default maintenance KPIs."""
    return MaintenanceKPIs(
        preventive_maintenance_percentage=0.0,
        mean_time_to_repair_hours=0.0,
        mean_time_between_failures_hours=0.0,
        maintenance_cost_per_unit=0.0,
        scheduled_maintenance_completion_percentage=0.0,
        equipment_reliability_percentage=0.0,
        maintenance_efficiency_score=0.0,
        timestamp=datetime.now()
    )


def _get_default_operational_kpis() -> OperationalKPIs:
    """Get default operational KPIs."""
    return OperationalKPIs(
        service_availability_percentage=0.0,
        customer_satisfaction_score=0.0,
        response_time_to_incidents_minutes=0.0,
        resource_utilization_percentage=0.0,
        process_efficiency_percentage=0.0,
        capacity_utilization_percentage=0.0,
        operational_efficiency_score=0.0,
        timestamp=datetime.now()
    )


def _get_default_financial_kpis() -> FinancialKPIs:
    """Get default financial KPIs."""
    return FinancialKPIs(
        operational_cost_per_unit=0.0,
        energy_cost_per_unit=0.0,
        maintenance_cost_percentage=0.0,
        revenue_per_unit=0.0,
        cost_savings_percentage=0.0,
        roi_percentage=0.0,
        financial_efficiency_score=0.0,
        timestamp=datetime.now()
    )


def _get_default_compliance_kpis() -> ComplianceKPIs:
    """Get default compliance KPIs."""
    return ComplianceKPIs(
        regulatory_compliance_percentage=0.0,
        safety_compliance_percentage=0.0,
        environmental_compliance_percentage=0.0,
        reporting_compliance_percentage=0.0,
        audit_score=0.0,
        violations_count=0,
        compliance_efficiency_score=0.0,
        timestamp=datetime.now()
    )


def _get_default_kpi_configuration() -> Dict[str, Any]:
    """Get default KPI configuration."""
    return {
        "id": "default",
        "name": "Default KPI Configuration",
        "description": "Default KPI configuration settings",
        "thresholds": {},
        "alert_rules": {},
        "goal_targets": {},
        "benchmark_settings": {},
        "update_frequency": 300,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


def _get_default_kpi_configuration_object() -> KPIConfiguration:
    """Get default KPI configuration object."""
    return KPIConfiguration(
        configuration_id="default",
        name="Default KPI Configuration",
        description="Default KPI configuration settings",
        thresholds={},
        alert_rules={},
        goal_targets={},
        benchmark_settings={},
        update_frequency=300,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


# Additional helper functions would be implemented here...
# For brevity, I'm showing the structure. Each function would contain
# the actual business logic for calculations, card generation, etc.

def _calculate_quality_compliance(quality_data: Any) -> float:
    """Calculate quality compliance percentage."""
    return 95.0  # Mock value

def _calculate_contamination_incidents(quality_data: Any) -> int:
    """Calculate contamination incidents count."""
    return 2  # Mock value

def _calculate_temperature_compliance(quality_data: Any) -> float:
    """Calculate temperature compliance percentage."""
    return 98.0  # Mock value

def _calculate_pressure_compliance(quality_data: Any) -> float:
    """Calculate pressure compliance percentage."""
    return 92.0  # Mock value

def _calculate_flow_rate_compliance(quality_data: Any) -> float:
    """Calculate flow rate compliance percentage."""
    return 94.0  # Mock value

def _calculate_quality_score(
    quality_compliance: float, contamination_incidents: int,
    temperature_compliance: float, pressure_compliance: float,
    flow_rate_compliance: float
) -> float:
    """Calculate overall quality score."""
    incident_penalty = contamination_incidents * 5
    base_score = (quality_compliance + temperature_compliance + 
                  pressure_compliance + flow_rate_compliance) / 4
    return max(0, base_score - incident_penalty)

# Continue with all other helper functions...
# (Implementation would continue with all remaining helper functions)

def _generate_summary_cards(dashboard: KPIDashboard) -> List[KPICard]:
    """Generate summary KPI cards."""
    return [
        KPICard(
            title="System Health",
            value=dashboard.system_health,
            unit="score",
            category="summary",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good",
            description="Overall system health score"
        )
    ]

def _generate_system_cards(system_kpis: SystemPerformanceKPIs) -> List[KPICard]:
    """Generate system performance KPI cards."""
    return [
        KPICard(
            title="System Uptime",
            value=system_kpis.uptime_percentage,
            unit="percentage",
            category="system",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good",
            description="System uptime percentage"
        )
    ]

def _generate_network_cards(network_kpis: NetworkEfficiencyKPIs) -> List[KPICard]:
    """Generate network efficiency KPI cards."""
    return [
        KPICard(
            title="Water Loss",
            value=network_kpis.water_loss_percentage,
            unit="percentage",
            category="network",
            trend=TrendDirection.decreasing,
            change_percentage=-2.0,
            status="warning",
            description="Water loss percentage"
        )
    ]

def _generate_quality_cards(quality_kpis: QualityKPIs) -> List[KPICard]:
    """Generate quality KPI cards."""
    return [
        KPICard(
            title="Quality Compliance",
            value=quality_kpis.quality_compliance_percentage,
            unit="percentage",
            category="quality",
            trend=TrendDirection.increasing,
            change_percentage=1.5,
            status="good",
            description="Quality compliance percentage"
        )
    ]

def _generate_maintenance_cards(maintenance_kpis: MaintenanceKPIs) -> List[KPICard]:
    """Generate maintenance KPI cards."""
    return [
        KPICard(
            title="Maintenance Efficiency",
            value=maintenance_kpis.maintenance_efficiency_score,
            unit="score",
            category="maintenance",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good",
            description="Maintenance efficiency score"
        )
    ]

def _generate_operational_cards(operational_kpis: OperationalKPIs) -> List[KPICard]:
    """Generate operational KPI cards."""
    return [
        KPICard(
            title="Service Availability",
            value=operational_kpis.service_availability_percentage,
            unit="percentage",
            category="operational",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good",
            description="Service availability percentage"
        )
    ]

def _generate_financial_cards(financial_kpis: FinancialKPIs) -> List[KPICard]:
    """Generate financial KPI cards."""
    return [
        KPICard(
            title="Cost Savings",
            value=financial_kpis.cost_savings_percentage,
            unit="percentage",
            category="financial",
            trend=TrendDirection.increasing,
            change_percentage=3.0,
            status="good",
            description="Cost savings percentage"
        )
    ]

def _generate_compliance_cards(compliance_kpis: ComplianceKPIs) -> List[KPICard]:
    """Generate compliance KPI cards."""
    return [
        KPICard(
            title="Regulatory Compliance",
            value=compliance_kpis.regulatory_compliance_percentage,
            unit="percentage",
            category="compliance",
            trend=TrendDirection.stable,
            change_percentage=0.0,
            status="good",
            description="Regulatory compliance percentage"
        )
    ]

# Additional helper functions for trends, benchmarks, alerts, and goals

def _generate_time_points(start_time: datetime, end_time: datetime, resolution: str) -> List[datetime]:
    """Generate time points based on resolution."""
    time_points = []
    current_time = start_time
    
    if resolution == "hourly":
        delta = timedelta(hours=1)
    elif resolution == "daily":
        delta = timedelta(days=1)
    elif resolution == "weekly":
        delta = timedelta(weeks=1)
    elif resolution == "monthly":
        delta = timedelta(days=30)
    else:
        delta = timedelta(days=1)
    
    while current_time <= end_time:
        time_points.append(current_time)
        current_time += delta
    
    return time_points


async def _calculate_kpi_trend_data(
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


def _calculate_trend_direction(trend_data: List[Dict[str, Any]]) -> TrendDirection:
    """Calculate trend direction from trend data."""
    if len(trend_data) < 2:
        return TrendDirection.stable
    
    first_value = trend_data[0]["value"]
    last_value = trend_data[-1]["value"]
    
    change_percentage = ((last_value - first_value) / first_value) * 100
    
    if change_percentage > 2:
        return TrendDirection.increasing
    elif change_percentage < -2:
        return TrendDirection.decreasing
    else:
        return TrendDirection.stable


def _calculate_change_percentage(trend_data: List[Dict[str, Any]]) -> float:
    """Calculate percentage change from trend data."""
    if len(trend_data) < 2:
        return 0.0
    
    first_value = trend_data[0]["value"]
    last_value = trend_data[-1]["value"]
    
    return ((last_value - first_value) / first_value) * 100


def _generate_industry_benchmarks(dashboard: KPIDashboard) -> List[KPIBenchmark]:
    """Generate industry benchmarks."""
    return [
        KPIBenchmark(
            category="system",
            metric_name="uptime_percentage",
            current_value=dashboard.system_performance.uptime_percentage,
            benchmark_value=99.9,
            benchmark_type=BenchmarkType.industry,
            difference_percentage=dashboard.system_performance.uptime_percentage - 99.9,
            status="below" if dashboard.system_performance.uptime_percentage < 99.9 else "above"
        ),
        KPIBenchmark(
            category="network",
            metric_name="water_loss_percentage",
            current_value=dashboard.network_efficiency.water_loss_percentage,
            benchmark_value=10.0,
            benchmark_type=BenchmarkType.industry,
            difference_percentage=dashboard.network_efficiency.water_loss_percentage - 10.0,
            status="above" if dashboard.network_efficiency.water_loss_percentage > 10.0 else "below"
        ),
        KPIBenchmark(
            category="quality",
            metric_name="quality_compliance_percentage",
            current_value=dashboard.quality_metrics.quality_compliance_percentage,
            benchmark_value=95.0,
            benchmark_type=BenchmarkType.industry,
            difference_percentage=dashboard.quality_metrics.quality_compliance_percentage - 95.0,
            status="above" if dashboard.quality_metrics.quality_compliance_percentage > 95.0 else "below"
        )
    ]


async def _generate_historical_benchmarks(
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
        KPIBenchmark(
            category="system",
            metric_name="uptime_percentage",
            current_value=dashboard.system_performance.uptime_percentage,
            benchmark_value=98.5,
            benchmark_type=BenchmarkType.historical,
            difference_percentage=dashboard.system_performance.uptime_percentage - 98.5,
            status="above" if dashboard.system_performance.uptime_percentage > 98.5 else "below"
        )
    ]


def _generate_target_benchmarks(dashboard: KPIDashboard) -> List[KPIBenchmark]:
    """Generate target benchmarks."""
    return [
        KPIBenchmark(
            category="system",
            metric_name="uptime_percentage",
            current_value=dashboard.system_performance.uptime_percentage,
            benchmark_value=99.5,
            benchmark_type=BenchmarkType.target,
            difference_percentage=dashboard.system_performance.uptime_percentage - 99.5,
            status="above" if dashboard.system_performance.uptime_percentage > 99.5 else "below"
        )
    ]


def _check_system_performance_alerts(system_kpis: SystemPerformanceKPIs) -> List[KPIAlert]:
    """Check system performance alerts."""
    alerts = []
    
    if system_kpis.uptime_percentage < 99.0:
        alerts.append(KPIAlert(
            category="system",
            metric_name="uptime_percentage",
            message=f"System uptime is {system_kpis.uptime_percentage:.1f}%, below threshold of 99%",
            severity=AlertLevel.high,
            threshold=99.0,
            current_value=system_kpis.uptime_percentage,
            timestamp=datetime.now()
        ))
    
    if system_kpis.error_rate_percentage > 1.0:
        alerts.append(KPIAlert(
            category="system",
            metric_name="error_rate_percentage",
            message=f"Error rate is {system_kpis.error_rate_percentage:.1f}%, above threshold of 1%",
            severity=AlertLevel.medium,
            threshold=1.0,
            current_value=system_kpis.error_rate_percentage,
            timestamp=datetime.now()
        ))
    
    return alerts


def _check_network_efficiency_alerts(network_kpis: NetworkEfficiencyKPIs) -> List[KPIAlert]:
    """Check network efficiency alerts."""
    alerts = []
    
    if network_kpis.water_loss_percentage > 20.0:
        alerts.append(KPIAlert(
            category="network",
            metric_name="water_loss_percentage",
            message=f"Water loss is {network_kpis.water_loss_percentage:.1f}%, above threshold of 20%",
            severity=AlertLevel.high,
            threshold=20.0,
            current_value=network_kpis.water_loss_percentage,
            timestamp=datetime.now()
        ))
    
    return alerts


def _check_quality_alerts(quality_kpis: QualityKPIs) -> List[KPIAlert]:
    """Check quality alerts."""
    alerts = []
    
    if quality_kpis.quality_compliance_percentage < 90.0:
        alerts.append(KPIAlert(
            category="quality",
            metric_name="quality_compliance_percentage",
            message=f"Quality compliance is {quality_kpis.quality_compliance_percentage:.1f}%, below threshold of 90%",
            severity=AlertLevel.high,
            threshold=90.0,
            current_value=quality_kpis.quality_compliance_percentage,
            timestamp=datetime.now()
        ))
    
    if quality_kpis.contamination_incidents_count > 5:
        alerts.append(KPIAlert(
            category="quality",
            metric_name="contamination_incidents_count",
            message=f"Contamination incidents count is {quality_kpis.contamination_incidents_count}, above threshold of 5",
            severity=AlertLevel.medium,
            threshold=5,
            current_value=quality_kpis.contamination_incidents_count,
            timestamp=datetime.now()
        ))
    
    return alerts


def _check_maintenance_alerts(maintenance_kpis: MaintenanceKPIs) -> List[KPIAlert]:
    """Check maintenance alerts."""
    alerts = []
    
    if maintenance_kpis.mean_time_to_repair_hours > 24.0:
        alerts.append(KPIAlert(
            category="maintenance",
            metric_name="mean_time_to_repair_hours",
            message=f"Mean time to repair is {maintenance_kpis.mean_time_to_repair_hours:.1f} hours, above threshold of 24 hours",
            severity=AlertLevel.medium,
            threshold=24.0,
            current_value=maintenance_kpis.mean_time_to_repair_hours,
            timestamp=datetime.now()
        ))
    
    return alerts


def _check_operational_alerts(operational_kpis: OperationalKPIs) -> List[KPIAlert]:
    """Check operational alerts."""
    alerts = []
    
    if operational_kpis.service_availability_percentage < 95.0:
        alerts.append(KPIAlert(
            category="operational",
            metric_name="service_availability_percentage",
            message=f"Service availability is {operational_kpis.service_availability_percentage:.1f}%, below threshold of 95%",
            severity=AlertLevel.high,
            threshold=95.0,
            current_value=operational_kpis.service_availability_percentage,
            timestamp=datetime.now()
        ))
    
    return alerts


def _check_financial_alerts(financial_kpis: FinancialKPIs) -> List[KPIAlert]:
    """Check financial alerts."""
    alerts = []
    
    if financial_kpis.operational_cost_per_unit > 100.0:
        alerts.append(KPIAlert(
            category="financial",
            metric_name="operational_cost_per_unit",
            message=f"Operational cost per unit is {financial_kpis.operational_cost_per_unit:.2f}, above threshold of 100",
            severity=AlertLevel.medium,
            threshold=100.0,
            current_value=financial_kpis.operational_cost_per_unit,
            timestamp=datetime.now()
        ))
    
    return alerts


def _check_compliance_alerts(compliance_kpis: ComplianceKPIs) -> List[KPIAlert]:
    """Check compliance alerts."""
    alerts = []
    
    if compliance_kpis.regulatory_compliance_percentage < 98.0:
        alerts.append(KPIAlert(
            category="compliance",
            metric_name="regulatory_compliance_percentage",
            message=f"Regulatory compliance is {compliance_kpis.regulatory_compliance_percentage:.1f}%, below threshold of 98%",
            severity=AlertLevel.high,
            threshold=98.0,
            current_value=compliance_kpis.regulatory_compliance_percentage,
            timestamp=datetime.now()
        ))
    
    if compliance_kpis.violations_count > 0:
        alerts.append(KPIAlert(
            category="compliance",
            metric_name="violations_count",
            message=f"Violations count is {compliance_kpis.violations_count}, above threshold of 0",
            severity=AlertLevel.high,
            threshold=0,
            current_value=compliance_kpis.violations_count,
            timestamp=datetime.now()
        ))
    
    return alerts


def _generate_system_performance_goals(system_kpis: SystemPerformanceKPIs) -> List[KPIGoal]:
    """Generate system performance goals."""
    return [
        KPIGoal(
            category="system",
            metric_name="uptime_percentage",
            target_value=99.9,
            current_value=system_kpis.uptime_percentage,
            progress_percentage=(system_kpis.uptime_percentage / 99.9) * 100,
            status=GoalStatus.on_track if system_kpis.uptime_percentage >= 99.0 else GoalStatus.at_risk,
            target_date=datetime.now() + timedelta(days=30),
            description="Achieve 99.9% system uptime"
        )
    ]


def _generate_network_efficiency_goals(network_kpis: NetworkEfficiencyKPIs) -> List[KPIGoal]:
    """Generate network efficiency goals."""
    return [
        KPIGoal(
            category="network",
            metric_name="water_loss_percentage",
            target_value=10.0,
            current_value=network_kpis.water_loss_percentage,
            progress_percentage=max(0, (20.0 - network_kpis.water_loss_percentage) / 10.0 * 100),
            status=GoalStatus.on_track if network_kpis.water_loss_percentage <= 15.0 else GoalStatus.at_risk,
            target_date=datetime.now() + timedelta(days=90),
            description="Reduce water loss to under 10%"
        )
    ]


def _generate_quality_goals(quality_kpis: QualityKPIs) -> List[KPIGoal]:
    """Generate quality goals."""
    return [
        KPIGoal(
            category="quality",
            metric_name="quality_compliance_percentage",
            target_value=98.0,
            current_value=quality_kpis.quality_compliance_percentage,
            progress_percentage=(quality_kpis.quality_compliance_percentage / 98.0) * 100,
            status=GoalStatus.on_track if quality_kpis.quality_compliance_percentage >= 95.0 else GoalStatus.at_risk,
            target_date=datetime.now() + timedelta(days=60),
            description="Achieve 98% quality compliance"
        )
    ]


def _generate_maintenance_goals(maintenance_kpis: MaintenanceKPIs) -> List[KPIGoal]:
    """Generate maintenance goals."""
    return [
        KPIGoal(
            category="maintenance",
            metric_name="preventive_maintenance_percentage",
            target_value=80.0,
            current_value=maintenance_kpis.preventive_maintenance_percentage,
            progress_percentage=(maintenance_kpis.preventive_maintenance_percentage / 80.0) * 100,
            status=GoalStatus.on_track if maintenance_kpis.preventive_maintenance_percentage >= 70.0 else GoalStatus.at_risk,
            target_date=datetime.now() + timedelta(days=120),
            description="Achieve 80% preventive maintenance"
        )
    ]


def _generate_operational_goals(operational_kpis: OperationalKPIs) -> List[KPIGoal]:
    """Generate operational goals."""
    return [
        KPIGoal(
            category="operational",
            metric_name="service_availability_percentage",
            target_value=99.0,
            current_value=operational_kpis.service_availability_percentage,
            progress_percentage=(operational_kpis.service_availability_percentage / 99.0) * 100,
            status=GoalStatus.on_track if operational_kpis.service_availability_percentage >= 97.0 else GoalStatus.at_risk,
            target_date=datetime.now() + timedelta(days=30),
            description="Achieve 99% service availability"
        )
    ]


def _generate_financial_goals(financial_kpis: FinancialKPIs) -> List[KPIGoal]:
    """Generate financial goals."""
    return [
        KPIGoal(
            category="financial",
            metric_name="cost_savings_percentage",
            target_value=15.0,
            current_value=financial_kpis.cost_savings_percentage,
            progress_percentage=(financial_kpis.cost_savings_percentage / 15.0) * 100,
            status=GoalStatus.on_track if financial_kpis.cost_savings_percentage >= 10.0 else GoalStatus.at_risk,
            target_date=datetime.now() + timedelta(days=180),
            description="Achieve 15% cost savings"
        )
    ]


def _generate_compliance_goals(compliance_kpis: ComplianceKPIs) -> List[KPIGoal]:
    """Generate compliance goals."""
    return [
        KPIGoal(
            category="compliance",
            metric_name="regulatory_compliance_percentage",
            target_value=100.0,
            current_value=compliance_kpis.regulatory_compliance_percentage,
            progress_percentage=compliance_kpis.regulatory_compliance_percentage,
            status=GoalStatus.on_track if compliance_kpis.regulatory_compliance_percentage >= 98.0 else GoalStatus.at_risk,
            target_date=datetime.now() + timedelta(days=90),
            description="Achieve 100% regulatory compliance"
        )
    ]


def _generate_executive_summary(
    dashboard: KPIDashboard,
    trends: List[KPITrend],
    benchmarks: List[KPIBenchmark],
    alerts: List[KPIAlert],
    goals: List[KPIGoal]
) -> str:
    """Generate executive summary for KPI report."""
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


def _generate_kpi_recommendations(
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


def _calculate_kpi_improvements(dashboard1: KPIDashboard, dashboard2: KPIDashboard) -> List[str]:
    """Calculate KPI improvements between periods."""
    improvements = []
    
    # Compare system performance
    if dashboard2.system_performance.uptime_percentage > dashboard1.system_performance.uptime_percentage:
        improvements.append("System uptime improved")
    
    # Compare network efficiency
    if dashboard2.network_efficiency.water_loss_percentage < dashboard1.network_efficiency.water_loss_percentage:
        improvements.append("Water loss reduced")
    
    # Compare quality metrics
    if dashboard2.quality_metrics.quality_compliance_percentage > dashboard1.quality_metrics.quality_compliance_percentage:
        improvements.append("Quality compliance improved")
    
    return improvements


def _calculate_kpi_regressions(dashboard1: KPIDashboard, dashboard2: KPIDashboard) -> List[str]:
    """Calculate KPI regressions between periods."""
    regressions = []
    
    # Compare system performance
    if dashboard2.system_performance.uptime_percentage < dashboard1.system_performance.uptime_percentage:
        regressions.append("System uptime declined")
    
    # Compare network efficiency
    if dashboard2.network_efficiency.water_loss_percentage > dashboard1.network_efficiency.water_loss_percentage:
        regressions.append("Water loss increased")
    
    # Compare quality metrics
    if dashboard2.quality_metrics.quality_compliance_percentage < dashboard1.quality_metrics.quality_compliance_percentage:
        regressions.append("Quality compliance declined")
    
    return regressions


def _calculate_overall_change_percentage(dashboard1: KPIDashboard, dashboard2: KPIDashboard) -> float:
    """Calculate overall change percentage between periods."""
    return ((dashboard2.system_health - dashboard1.system_health) / dashboard1.system_health) * 100


def _generate_period_comparison_insights(
    dashboard1: KPIDashboard,
    dashboard2: KPIDashboard,
    improvements: List[str],
    regressions: List[str]
) -> List[str]:
    """Generate insights from period comparison."""
    insights = []
    
    if len(improvements) > len(regressions):
        insights.append("Overall performance shows positive trend")
    elif len(regressions) > len(improvements):
        insights.append("Overall performance shows declining trend")
    else:
        insights.append("Overall performance remains stable")
    
    if improvements:
        insights.append(f"Key improvements: {', '.join(improvements)}")
    
    if regressions:
        insights.append(f"Areas needing attention: {', '.join(regressions)}")
    
    return insights


def _calculate_data_quality_score(dashboard: KPIDashboard) -> float:
    """Calculate data quality score."""
    # Mock calculation based on completeness and accuracy
    return 92.5


def _calculate_component_health(dashboard: KPIDashboard) -> Dict[str, float]:
    """Calculate component health scores."""
    return {
        "system": dashboard.system_performance.performance_score,
        "network": dashboard.network_efficiency.overall_efficiency_score,
        "quality": dashboard.quality_metrics.quality_score,
        "maintenance": dashboard.maintenance_metrics.maintenance_efficiency_score,
        "operational": dashboard.operational_metrics.operational_efficiency_score,
        "financial": dashboard.financial_metrics.financial_efficiency_score,
        "compliance": dashboard.compliance_metrics.compliance_efficiency_score
    }


def _determine_health_status(health_score: float) -> str:
    """Determine health status based on score."""
    if health_score >= 90:
        return "excellent"
    elif health_score >= 80:
        return "good"
    elif health_score >= 70:
        return "fair"
    elif health_score >= 60:
        return "poor"
    else:
        return "critical"


def _generate_health_insights(dashboard: KPIDashboard, component_health: Dict[str, float]) -> List[str]:
    """Generate health insights."""
    insights = []
    
    # Find best and worst performing components
    best_component = max(component_health.items(), key=lambda x: x[1])
    worst_component = min(component_health.items(), key=lambda x: x[1])
    
    insights.append(f"Best performing area: {best_component[0]} ({best_component[1]:.1f})")
    insights.append(f"Area needing attention: {worst_component[0]} ({worst_component[1]:.1f})")
    
    # Overall health assessment
    if dashboard.system_health >= 90:
        insights.append("System is operating at optimal levels")
    elif dashboard.system_health >= 80:
        insights.append("System is performing well with minor optimization opportunities")
    elif dashboard.system_health >= 70:
        insights.append("System performance is acceptable but improvements needed")
    else:
        insights.append("System requires immediate attention and optimization")
    
    return insights


# Additional calculation functions for maintenance, operational, financial, and compliance KPIs

def _calculate_preventive_maintenance_percentage(maintenance_data: Any) -> float:
    """Calculate preventive maintenance percentage."""
    return 75.0  # Mock value


def _calculate_mean_time_to_repair(maintenance_data: Any) -> float:
    """Calculate mean time to repair in hours."""
    return 8.5  # Mock value


def _calculate_mean_time_between_failures(maintenance_data: Any) -> float:
    """Calculate mean time between failures in hours."""
    return 720.0  # Mock value (30 days)


def _calculate_maintenance_cost_per_unit(maintenance_data: Any) -> float:
    """Calculate maintenance cost per unit."""
    return 50.0  # Mock value


def _calculate_scheduled_maintenance_completion(maintenance_data: Any) -> float:
    """Calculate scheduled maintenance completion percentage."""
    return 95.0  # Mock value


def _calculate_equipment_reliability(maintenance_data: Any) -> float:
    """Calculate equipment reliability percentage."""
    return 92.0  # Mock value


def _calculate_maintenance_efficiency_score(
    preventive_percentage: float,
    mean_time_to_repair: float,
    mean_time_between_failures: float,
    scheduled_completion: float,
    equipment_reliability: float
) -> float:
    """Calculate maintenance efficiency score."""
    # Weighted scoring algorithm
    preventive_score = preventive_percentage
    repair_score = max(0, 100 - (mean_time_to_repair / 24 * 100))
    reliability_score = equipment_reliability
    completion_score = scheduled_completion
    
    return (preventive_score * 0.3 + repair_score * 0.2 + 
            reliability_score * 0.3 + completion_score * 0.2)


def _calculate_service_availability(operational_data: Any) -> float:
    """Calculate service availability percentage."""
    return 99.2  # Mock value


def _calculate_customer_satisfaction(operational_data: Any) -> float:
    """Calculate customer satisfaction score."""
    return 4.2  # Mock value (out of 5)


def _calculate_response_time_to_incidents(operational_data: Any) -> float:
    """Calculate response time to incidents in minutes."""
    return 15.0  # Mock value


def _calculate_resource_utilization(operational_data: Any) -> float:
    """Calculate resource utilization percentage."""
    return 85.0  # Mock value


def _calculate_process_efficiency(operational_data: Any) -> float:
    """Calculate process efficiency percentage."""
    return 88.0  # Mock value


def _calculate_capacity_utilization(operational_data: Any) -> float:
    """Calculate capacity utilization percentage."""
    return 78.0  # Mock value


def _calculate_operational_efficiency_score(
    service_availability: float,
    customer_satisfaction: float,
    response_time: float,
    resource_utilization: float,
    process_efficiency: float,
    capacity_utilization: float
) -> float:
    """Calculate operational efficiency score."""
    # Weighted scoring algorithm
    availability_score = service_availability
    satisfaction_score = customer_satisfaction * 20  # Convert to 100 scale
    response_score = max(0, 100 - (response_time / 60 * 100))
    
    return (availability_score * 0.25 + satisfaction_score * 0.2 + 
            response_score * 0.15 + resource_utilization * 0.15 + 
            process_efficiency * 0.15 + capacity_utilization * 0.1)


def _calculate_operational_cost_per_unit(financial_data: Any) -> float:
    """Calculate operational cost per unit."""
    return 85.0  # Mock value


def _calculate_energy_cost_per_unit(financial_data: Any) -> float:
    """Calculate energy cost per unit."""
    return 25.0  # Mock value


def _calculate_maintenance_cost_percentage(financial_data: Any) -> float:
    """Calculate maintenance cost percentage."""
    return 15.0  # Mock value


def _calculate_revenue_per_unit(financial_data: Any) -> float:
    """Calculate revenue per unit."""
    return 120.0  # Mock value


def _calculate_cost_savings_percentage(financial_data: Any) -> float:
    """Calculate cost savings percentage."""
    return 8.5  # Mock value


def _calculate_roi_percentage(financial_data: Any) -> float:
    """Calculate return on investment percentage."""
    return 12.0  # Mock value


def _calculate_financial_efficiency_score(
    operational_cost: float,
    energy_cost: float,
    maintenance_cost_percentage: float,
    revenue: float,
    cost_savings: float,
    roi: float
) -> float:
    """Calculate financial efficiency score."""
    # Cost efficiency (lower is better)
    cost_efficiency = max(0, 100 - ((operational_cost + energy_cost) / 200 * 100))
    
    # Revenue efficiency
    revenue_efficiency = min(100, revenue / 100 * 100)
    
    # Savings and ROI
    savings_score = min(100, cost_savings * 10)
    roi_score = min(100, roi * 8)
    
    return (cost_efficiency * 0.3 + revenue_efficiency * 0.2 + 
            savings_score * 0.25 + roi_score * 0.25)


def _calculate_regulatory_compliance(compliance_data: Any) -> float:
    """Calculate regulatory compliance percentage."""
    return 98.5  # Mock value


def _calculate_safety_compliance(compliance_data: Any) -> float:
    """Calculate safety compliance percentage."""
    return 99.0  # Mock value


def _calculate_environmental_compliance(compliance_data: Any) -> float:
    """Calculate environmental compliance percentage."""
    return 97.5  # Mock value


def _calculate_reporting_compliance(compliance_data: Any) -> float:
    """Calculate reporting compliance percentage."""
    return 95.0  # Mock value


def _calculate_audit_score(compliance_data: Any) -> float:
    """Calculate audit score."""
    return 88.0  # Mock value


def _calculate_violations_count(compliance_data: Any) -> int:
    """Calculate violations count."""
    return 1  # Mock value


def _calculate_compliance_efficiency_score(
    regulatory_compliance: float,
    safety_compliance: float,
    environmental_compliance: float,
    reporting_compliance: float,
    audit_score: float,
    violations_count: int
) -> float:
    """Calculate compliance efficiency score."""
    # Average compliance scores
    avg_compliance = (regulatory_compliance + safety_compliance + 
                     environmental_compliance + reporting_compliance) / 4
    
    # Violation penalty
    violation_penalty = violations_count * 10
    
    # Overall score
    base_score = (avg_compliance * 0.6 + audit_score * 0.4)
    
    return max(0, base_score - violation_penalty) 
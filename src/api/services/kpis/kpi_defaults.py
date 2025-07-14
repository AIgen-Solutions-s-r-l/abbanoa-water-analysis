"""
KPI Defaults Module.

This module provides default KPI objects for error handling and fallback scenarios.
"""

from datetime import datetime
from src.schemas.api.kpis import (
    SystemPerformanceKPIs,
    NetworkEfficiencyKPIs,
    QualityKPIs,
    MaintenanceKPIs,
    OperationalKPIs,
    FinancialKPIs,
    ComplianceKPIs,
    KPIConfiguration
)


def get_default_system_performance_kpis() -> SystemPerformanceKPIs:
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


def get_default_network_efficiency_kpis() -> NetworkEfficiencyKPIs:
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


def get_default_quality_kpis() -> QualityKPIs:
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


def get_default_maintenance_kpis() -> MaintenanceKPIs:
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


def get_default_operational_kpis() -> OperationalKPIs:
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


def get_default_financial_kpis() -> FinancialKPIs:
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


def get_default_compliance_kpis() -> ComplianceKPIs:
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


def get_default_kpi_configuration() -> dict:
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


def get_default_kpi_configuration_object() -> KPIConfiguration:
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
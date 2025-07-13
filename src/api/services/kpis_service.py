"""
KPI Service Module.

This module provides comprehensive business logic for KPI calculations,
dashboard generation, alerts, and performance monitoring.

This service acts as a facade over the refactored KPI services architecture.
"""

import logging
from datetime import datetime
from typing import List, Optional

from src.schemas.api.kpis import (
    KPIDashboard,
    KPICard,
    KPITrend,
    KPIBenchmark,
    KPIAlert,
    KPIGoal,
    KPIReport,
    KPIComparison,
    KPIConfiguration,
    KPIHealth
)
from src.infrastructure.data.hybrid_data_service import HybridDataService
from src.api.services.kpis import KPIOrchestrator

logger = logging.getLogger(__name__)

# Create a global orchestrator instance
_kpi_orchestrator = KPIOrchestrator()


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
    return await _kpi_orchestrator.generate_kpi_dashboard(
        hybrid_service, start_time, end_time, selected_nodes, update_frequency
    )


# Individual KPI calculation functions are now handled by specific services
# These functions are deprecated and will be removed in a future version
# Use the orchestrator methods instead


async def generate_kpi_cards(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None,
    card_type: str = "summary",
    limit: int = 20
) -> List[KPICard]:
    """Generate KPI cards for dashboard display."""
    return await _kpi_orchestrator.generate_kpi_cards(
        hybrid_service, start_time, end_time, selected_nodes, card_type, limit
    )


async def generate_kpi_trends(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None,
    kpi_categories: Optional[List[str]] = None,
    resolution: str = "daily"
) -> List[KPITrend]:
    """Generate KPI trends over time."""
    return await _kpi_orchestrator.generate_kpi_trends(
        hybrid_service, start_time, end_time, selected_nodes, kpi_categories, resolution
    )


async def generate_kpi_benchmarks(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None,
    benchmark_type: str = "industry"
) -> List[KPIBenchmark]:
    """Generate KPI benchmarks for comparison."""
    return await _kpi_orchestrator.generate_kpi_benchmarks(
        hybrid_service, start_time, end_time, selected_nodes, benchmark_type
    )


async def generate_kpi_alerts(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> List[KPIAlert]:
    """Generate KPI alerts for monitoring."""
    return await _kpi_orchestrator.generate_kpi_alerts(
        hybrid_service, start_time, end_time, selected_nodes
    )


async def generate_kpi_goals(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> List[KPIGoal]:
    """Generate KPI goals and track progress."""
    return await _kpi_orchestrator.generate_kpi_goals(
        hybrid_service, start_time, end_time, selected_nodes
    )


async def generate_kpi_report(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None,
    report_format: str = "json"
) -> KPIReport:
    """Generate comprehensive KPI report."""
    return await _kpi_orchestrator.generate_kpi_report(
        hybrid_service, start_time, end_time, selected_nodes, report_format
    )


async def compare_kpi_periods(
    hybrid_service: HybridDataService,
    period1_start: datetime,
    period1_end: datetime,
    period2_start: datetime,
    period2_end: datetime,
    selected_nodes: Optional[List[str]] = None
) -> KPIComparison:
    """Compare KPIs between two time periods."""
    return await _kpi_orchestrator.compare_kpi_periods(
        hybrid_service, period1_start, period1_end, period2_start, period2_end, selected_nodes
    )


async def get_kpi_configuration(
    hybrid_service: HybridDataService,
    configuration_type: str = "default"
) -> KPIConfiguration:
    """Get KPI configuration settings."""
    return await _kpi_orchestrator.get_kpi_configuration(hybrid_service, configuration_type)


async def get_kpi_health(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> KPIHealth:
    """Get overall KPI system health status."""
    return await _kpi_orchestrator.get_kpi_health(
        hybrid_service, start_time, end_time, selected_nodes
    )


# All helper functions have been moved to the refactored service architecture
# This file now acts as a facade over the new KPI services
"""
Main Streamlit application for Abbanoa Water Infrastructure Dashboard.

This module serves as the entry point for the Streamlit dashboard,
orchestrating the various tabs and components.
"""

import asyncio
from datetime import datetime
from typing import Optional
import os

import streamlit as st
from dependency_injector.wiring import Provide, inject

# Import use cases
from src.application.use_cases.analyze_consumption_patterns import (
    AnalyzeConsumptionPatternsUseCase,
)
from src.application.use_cases.calculate_network_efficiency import (
    CalculateNetworkEfficiencyUseCase,
)
from src.application.use_cases.detect_network_anomalies import (
    DetectNetworkAnomaliesUseCase,
)

# Import DI container
from src.infrastructure.di_container import Container

# Import hybrid architecture components
from src.infrastructure.cache.cache_initializer import initialize_cache_on_startup
from src.infrastructure.etl.etl_scheduler import get_etl_scheduler

# Import components
from src.presentation.streamlit.components.forecast_tab import ForecastTab
from src.presentation.streamlit.components.sidebar_filters import SidebarFilters
from src.presentation.streamlit.config.theme import apply_custom_theme
from src.presentation.streamlit.utils.data_fetcher import DataFetcher
from src.presentation.streamlit.utils.performance_monitor import performance_monitor

# Page configuration
st.set_page_config(
    page_title="Abbanoa Water Network Forecasting Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis",
        "Report a bug": "https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis/issues",
        "About": "Water Infrastructure Forecasting Dashboard v0.5.0",
    },
)

# Apply custom theme
apply_custom_theme()

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.district_id = "DIST_001"
    st.session_state.metric = "flow_rate"
    st.session_state.horizon = 7
    st.session_state.last_update = datetime.now()
    st.session_state.bigquery_connected = True  # We have real data in BigQuery!
    st.session_state.hybrid_architecture = True  # Using PostgreSQL + Redis + BigQuery
    
    # Initialize hybrid architecture on first load
    with st.spinner("Initializing hybrid data architecture..."):
        # Set Redis configuration
        os.environ["REDIS_HOST"] = os.getenv("REDIS_HOST", "localhost")
        os.environ["REDIS_PORT"] = os.getenv("REDIS_PORT", "6379")
        
        # Initialize cache (non-blocking)
        try:
            # Run cache initialization in a thread to avoid blocking
            import threading
            def init_cache():
                try:
                    initialize_cache_on_startup(force_refresh=False)
                except Exception as e:
                    print(f"Cache initialization error: {e}")
            
            cache_thread = threading.Thread(target=init_cache, daemon=True)
            cache_thread.start()
            st.session_state.cache_initialized = True
        except Exception as e:
            st.warning(f"Cache initialization error: {e}")
            st.session_state.cache_initialized = False


@st.cache_resource
def get_data_fetcher() -> DataFetcher:
    """Return a cached instance of the DataFetcher."""
    return DataFetcher()


class DashboardApp:
    """Main dashboard application class."""

    @inject
    def __init__(
        self,
        analyze_consumption_use_case: AnalyzeConsumptionPatternsUseCase = Provide[
            Container.analyze_consumption_patterns_use_case
        ],
        detect_anomalies_use_case: DetectNetworkAnomaliesUseCase = Provide[
            Container.detect_network_anomalies_use_case
        ],
        calculate_efficiency_use_case: CalculateNetworkEfficiencyUseCase = Provide[
            Container.calculate_network_efficiency_use_case
        ],
    ):
        """Initialize the dashboard application with injected dependencies."""
        self.analyze_consumption_use_case = analyze_consumption_use_case
        self.detect_anomalies_use_case = detect_anomalies_use_case
        self.calculate_efficiency_use_case = calculate_efficiency_use_case

        self.data_fetcher = get_data_fetcher()
        self.sidebar_filters = SidebarFilters()
        self.forecast_tab = ForecastTab(self.data_fetcher)

    def render_header(self) -> None:
        """Render the main header section."""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(
                """
                <div style="text-align: center;">
                    <h1 style="color: #1f77b4; margin-bottom: 0;">
                        💧 Water Network Forecasting Dashboard
                    </h1>
                    <p style="color: #666; font-size: 1.1rem;">
                        Abbanoa Infrastructure Monitoring System
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            # Refresh button
            if st.button("🔄 Refresh", use_container_width=True):
                st.session_state.last_update = datetime.now()
                st.rerun()

            # Last updated time
            st.caption(
                f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}"
            )

    def render_tabs(self) -> None:
        """Render the main tab navigation."""
        # Check if API is available
        from src.presentation.streamlit.utils.api_client import get_api_client
        api_client = get_api_client()
        use_api = api_client.health_check()
        
        if use_api:
            # Use API-based components for better performance
            from src.presentation.streamlit.components.overview_tab_api import OverviewTab
            from src.presentation.streamlit.components.anomaly_tab_api import AnomalyTab
            from src.presentation.streamlit.components.efficiency_tab_api import EfficiencyTab
            
            overview_tab = OverviewTab()
            anomaly_tab = AnomalyTab()
            efficiency_tab = EfficiencyTab()
            
            # Still use old components for tabs not yet migrated
            from src.presentation.streamlit.components.consumption_tab import ConsumptionTab
            from src.presentation.streamlit.components.reports_tab import ReportsTab
            consumption_tab = ConsumptionTab(self.analyze_consumption_use_case)
            reports_tab = ReportsTab()
            
            st.session_state.using_api = True
            
        else:
            # Fallback to old components if API is not available
            from src.presentation.streamlit.components.anomaly_tab import AnomalyTab
            from src.presentation.streamlit.components.consumption_tab import ConsumptionTab
            from src.presentation.streamlit.components.efficiency_tab import EfficiencyTab
            from src.presentation.streamlit.components.reports_tab import ReportsTab
            
            # Use Redis-based overview tab if cache is initialized
            if st.session_state.get("cache_initialized", False):
                from src.presentation.streamlit.components.overview_tab_redis import OverviewTab
                overview_tab = OverviewTab()
            else:
                from src.presentation.streamlit.components.overview_tab import OverviewTab
                overview_tab = OverviewTab(self.calculate_efficiency_use_case)
                
            anomaly_tab = AnomalyTab(self.detect_anomalies_use_case)
            consumption_tab = ConsumptionTab(self.analyze_consumption_use_case)
            efficiency_tab = EfficiencyTab(self.calculate_efficiency_use_case)
            reports_tab = ReportsTab()
            
            st.session_state.using_api = False

        # Create tabs - enhanced with new comprehensive features
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
            [
                "📈 Forecast",
                "🚀 Enhanced Overview",
                "📊 KPI Dashboard", 
                "🧪 Water Quality",
                "🔍 Anomaly Detection",
                "📈 Consumption Patterns",
                "🔗 Network Efficiency",
                "📋 Reports",
                "⚡ Performance Monitor",
                "📊 Classic Overview"
            ]
        )

        with tab1:
            # New forecast tab
            with st.spinner("Loading forecast data..."):
                # Measure forecast tab performance
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("Forecast Tab", current_time_range)
                def render_forecast_tab():
                    return self.forecast_tab.render()
                render_forecast_tab()

        with tab2:
            # Enhanced overview with comprehensive metrics
            with st.spinner("Loading enhanced overview..."):
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("Enhanced Overview Tab", current_time_range)
                def render_enhanced_overview_tab():
                    from src.presentation.streamlit.components.enhanced_overview_tab import EnhancedOverviewTab
                    enhanced_overview = EnhancedOverviewTab()
                    return enhanced_overview.render(
                        time_range=current_time_range,
                        selected_nodes=st.session_state.get("selected_nodes", ["All Nodes"]),
                    )
                render_enhanced_overview_tab()
        
        with tab3:
            # KPI Dashboard
            with st.spinner("Loading KPI dashboard..."):
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("KPI Dashboard Tab", current_time_range)
                def render_kpi_dashboard_tab():
                    from src.presentation.streamlit.components.kpi_dashboard_tab import KPIDashboardTab
                    kpi_dashboard = KPIDashboardTab()
                    return kpi_dashboard.render(
                        time_range=current_time_range,
                        selected_nodes=st.session_state.get("selected_nodes", ["All Nodes"]),
                    )
                render_kpi_dashboard_tab()
        
        with tab4:
            # Water Quality Monitoring
            with st.spinner("Loading water quality analysis..."):
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("Water Quality Tab", current_time_range)
                def render_water_quality_tab():
                    from src.presentation.streamlit.components.water_quality_tab import WaterQualityTab
                    water_quality = WaterQualityTab()
                    return water_quality.render(
                        time_range=current_time_range,
                        selected_nodes=st.session_state.get("selected_nodes", ["All Nodes"]),
                    )
                render_water_quality_tab()

        with tab5:
            # Anomaly detection from old dashboard
            with st.spinner("Loading anomaly data..."):
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("Anomaly Tab", current_time_range)
                def render_anomaly_tab():
                    return anomaly_tab.render(time_range=current_time_range)
                render_anomaly_tab()

        with tab6:
            # Consumption patterns from old dashboard
            with st.spinner("Loading consumption data..."):
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("Consumption Tab", current_time_range)
                def render_consumption_tab():
                    return consumption_tab.render(
                        time_range=current_time_range,
                        selected_nodes=st.session_state.get("selected_nodes", ["All Nodes"]),
                    )
                render_consumption_tab()

        with tab7:
            # Network efficiency from old dashboard
            with st.spinner("Loading efficiency data..."):
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("Efficiency Tab", current_time_range)
                def render_efficiency_tab():
                    return efficiency_tab.render(time_range=current_time_range)
                render_efficiency_tab()

        with tab8:
            # Reports from old dashboard
            with st.spinner("Loading reports..."):
                @performance_monitor.measure_time("Reports Tab", "N/A")
                def render_reports_tab():
                    return reports_tab.render()
                render_reports_tab()

        with tab9:
            # Performance monitoring tab
            performance_monitor.render_performance_dashboard()
        
        with tab10:
            # Classic overview (original)
            with st.spinner("Loading classic overview..."):
                current_time_range = st.session_state.get("time_range", "Last 24 Hours")
                @performance_monitor.measure_time("Classic Overview Tab", current_time_range)
                def render_classic_overview_tab():
                    return overview_tab.render(
                        time_range=current_time_range,
                        selected_nodes=st.session_state.get("selected_nodes", ["All Nodes"]),
                    )
                render_classic_overview_tab()

    def run(self) -> None:
        """Run the main dashboard application."""
        # Render sidebar filters
        self.sidebar_filters.render()

        # Main content area
        self.render_header()
        st.divider()
        self.render_tabs()

        # Footer with data source indicator
        st.markdown("---")

        # Check data architecture status
        if st.session_state.get("using_api", False):
            data_source = "🚀 Using Processing Services API (Optimized)"
        elif st.session_state.get("hybrid_architecture", False):
            if st.session_state.get("cache_initialized", False):
                data_source = "🟢 Hybrid Architecture Active (Redis + PostgreSQL + BigQuery)"
            else:
                data_source = "🟡 Hybrid Architecture Initializing..."
        elif st.session_state.get("bigquery_connected", False):
            data_source = "🔵 Connected to BigQuery Only"
        else:
            data_source = "⚫ Using Demo Data"

        st.markdown(
            f"""
            <div style="text-align: center; color: #999; font-size: 0.8rem;">
                {data_source} | Powered by BigQuery ML | ARIMA_PLUS Models | 
                <a href="https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis" 
                   style="color: #1f77b4;">View on GitHub</a>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main():
    """Main entry point for the Streamlit application."""
    # Initialize DI container
    container = Container()

    # Configure container
    container.config.bigquery.project_id.from_env(
        "BIGQUERY_PROJECT_ID", default="abbanoa-464816"
    )
    container.config.bigquery.dataset_id.from_env(
        "BIGQUERY_DATASET_ID", default="water_infrastructure"
    )
    container.config.bigquery.location.from_env("BIGQUERY_LOCATION", default="EU")
    container.config.bigquery.credentials_path.from_env(
        "GOOGLE_APPLICATION_CREDENTIALS", default=None
    )

    container.config.anomaly_detection.z_score_threshold.from_env(
        "ANOMALY_Z_SCORE", default=3.0
    )
    container.config.anomaly_detection.min_data_points.from_env(
        "ANOMALY_MIN_POINTS", default=10
    )
    container.config.anomaly_detection.rolling_window_hours.from_env(
        "ANOMALY_WINDOW_HOURS", default=24
    )

    # Wire the container
    container.wire(modules=[__name__])

    # Create and run app
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()

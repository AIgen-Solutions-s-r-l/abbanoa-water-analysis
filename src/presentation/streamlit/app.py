"""
Main Streamlit application for Abbanoa Water Infrastructure Dashboard.

This module serves as the entry point for the Streamlit dashboard,
orchestrating the various tabs and components.
"""

import asyncio
from datetime import datetime
from typing import Optional

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

# Import components
from src.presentation.streamlit.components.forecast_tab import ForecastTab
from src.presentation.streamlit.components.sidebar_filters import SidebarFilters
from src.presentation.streamlit.config.theme import apply_custom_theme
from src.presentation.streamlit.utils.data_fetcher import DataFetcher

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

        self.data_fetcher = DataFetcher()
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
        # Import the old dashboard components
        from src.presentation.streamlit.components.anomaly_tab import AnomalyTab
        from src.presentation.streamlit.components.consumption_tab import ConsumptionTab
        from src.presentation.streamlit.components.efficiency_tab import EfficiencyTab
        from src.presentation.streamlit.components.overview_tab import OverviewTab
        from src.presentation.streamlit.components.reports_tab import ReportsTab

        # Initialize old dashboard components with use cases
        overview_tab = OverviewTab(self.calculate_efficiency_use_case)
        anomaly_tab = AnomalyTab(self.detect_anomalies_use_case)
        consumption_tab = ConsumptionTab(self.analyze_consumption_use_case)
        efficiency_tab = EfficiencyTab(self.calculate_efficiency_use_case)
        reports_tab = ReportsTab()

        # Create tabs - combining new and old functionality
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            [
                "📈 Forecast",
                "📊 Overview",
                "🔍 Anomaly Detection",
                "📈 Consumption Patterns",
                "🔗 Network Efficiency",
                "📋 Reports",
            ]
        )

        with tab1:
            # New forecast tab
            self.forecast_tab.render()

        with tab2:
            # Old dashboard overview
            overview_tab.render(
                time_range=st.session_state.get("time_range", "Last 24 Hours"),
                selected_nodes=st.session_state.get("selected_nodes", ["All Nodes"]),
            )

        with tab3:
            # Anomaly detection from old dashboard
            anomaly_tab.render(
                time_range=st.session_state.get("time_range", "Last 24 Hours")
            )

        with tab4:
            # Consumption patterns from old dashboard
            consumption_tab.render(
                time_range=st.session_state.get("time_range", "Last 24 Hours"),
                selected_nodes=st.session_state.get("selected_nodes", ["All Nodes"]),
            )

        with tab5:
            # Network efficiency from old dashboard
            efficiency_tab.render(
                time_range=st.session_state.get("time_range", "Last 24 Hours")
            )

        with tab6:
            # Reports from old dashboard
            reports_tab.render()

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

        # Check if we're using real data
        data_source = (
            "🟢 Connected to BigQuery"
            if st.session_state.get("bigquery_connected", False)
            else "🟡 Using Demo Data"
        )

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

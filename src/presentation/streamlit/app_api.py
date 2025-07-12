"""
Streamlit Dashboard Application - API Version.

This version uses the REST API instead of direct BigQuery connections.
"""

import os
from datetime import datetime, timedelta

import streamlit as st

from src.presentation.streamlit.components.anomaly_tab_api import AnomalyTab
from src.presentation.streamlit.components.efficiency_tab_api import EfficiencyTab
from src.presentation.streamlit.components.forecast_tab import ForecastTab

# Import existing API-based components
from src.presentation.streamlit.components.overview_tab_api import OverviewTab

# Import API client and utilities
from src.presentation.streamlit.utils.api_client import APIClient
from src.presentation.streamlit.utils.data_fetcher import DataFetcher


class DashboardApp:
    """Main dashboard application using API."""

    def __init__(self):
        """Initialize the dashboard with API client."""
        # Initialize API client
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_client = APIClient(base_url=api_base_url)
        self.data_fetcher = DataFetcher(api_base_url=api_base_url)

        # Initialize components (they use their own API clients)
        self.overview_tab = OverviewTab()
        self.efficiency_tab = EfficiencyTab()
        self.anomaly_tab = AnomalyTab()
        self.forecast_tab = ForecastTab(data_fetcher=self.data_fetcher)

        # Session state
        if "selected_node" not in st.session_state:
            st.session_state.selected_node = None
        if "selected_date_range" not in st.session_state:
            st.session_state.selected_date_range = (
                datetime.now() - timedelta(days=7),
                datetime.now(),
            )

    def run(self):
        """Run the Streamlit application."""
        st.set_page_config(
            page_title="Abbanoa Water Infrastructure Monitor",
            page_icon="💧",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Apply custom CSS
        self._apply_custom_css()

        # Sidebar
        with st.sidebar:
            self._render_sidebar()

        # Main content
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🏠 Overview", "📊 Network Efficiency", "⚠️ Anomalies", "📈 Forecasts"]
        )

        with tab1:
            # Get time range and selected nodes from session state
            time_range = st.session_state.get("time_range", "7d")
            selected_nodes = st.session_state.get("selected_nodes", [])
            self.overview_tab.render(
                time_range=time_range, selected_nodes=selected_nodes
            )

        with tab2:
            # Get time range from session state
            time_range = st.session_state.get("time_range", "7d")
            self.efficiency_tab.render(time_range=time_range)

        with tab3:
            # Get time range and selected nodes from session state
            time_range = st.session_state.get("time_range", "7d")
            selected_nodes = st.session_state.get("selected_nodes", [])
            self.anomaly_tab.render(
                time_range=time_range, selected_nodes=selected_nodes
            )

        with tab4:
            self.forecast_tab.render()

    def _render_sidebar(self):
        """Render sidebar with controls."""
        st.title("💧 Abbanoa Monitor")
        st.markdown("---")

        # Time range selector
        st.subheader("📅 Time Range")
        time_range_options = {
            "Last 24 Hours": "24h",
            "Last 7 Days": "7d",
            "Last 30 Days": "30d",
            "Last 90 Days": "90d",
            "Last 1 Year": "365d",
        }
        selected_range = st.selectbox(
            "Select Time Range",
            options=list(time_range_options.keys()),
            index=1,  # Default to 7 days
        )
        st.session_state.time_range = time_range_options[selected_range]

        # Node selector
        st.markdown("---")
        st.subheader("📍 Node Selection")

        # Get nodes list from API
        try:
            nodes = self.api_client.get_nodes()
            if nodes:
                node_ids = [node.get("node_id", "") for node in nodes]
                selected_nodes = st.multiselect(
                    "Select Nodes", options=node_ids, default=[]
                )
                st.session_state.selected_nodes = selected_nodes
            else:
                st.info("No nodes available")
                st.session_state.selected_nodes = []
        except Exception as e:
            st.error(f"Error loading nodes: {str(e)}")
            st.session_state.selected_nodes = []

        # Refresh button
        st.markdown("---")
        if st.button("🔄 Refresh Data", use_container_width=True):
            # Clear cache
            st.cache_data.clear()
            st.rerun()

        # System info
        st.markdown("---")
        st.caption("System Status")
        status = self.api_client.get_system_status()
        if status:
            if status.get("status") == "healthy":
                st.success("✅ System Healthy")
            else:
                st.error("❌ System Issues")

            st.caption(f"Last Update: {status.get('timestamp', 'Unknown')}")

    def _apply_custom_css(self):
        """Apply custom CSS styling."""
        st.markdown(
            """
            <style>
            /* Main container */
            .main {
                padding: 1rem;
            }

            /* Metric cards */
            div[data-testid="metric-container"] {
                background-color: #f0f2f6;
                border: 1px solid #e0e2e6;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 1rem;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 0.5rem 1rem;
                font-weight: 500;
            }

            /* Sidebar */
            .css-1d391kg {
                background-color: #f5f7fa;
            }

            /* Buttons */
            .stButton > button {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                font-weight: 500;
                transition: background-color 0.3s;
            }

            .stButton > button:hover {
                background-color: #0052a3;
            }

            /* Success/Error messages */
            .stSuccess {
                background-color: #d4edda;
                border-color: #c3e6cb;
                color: #155724;
            }

            .stError {
                background-color: #f8d7da;
                border-color: #f5c6cb;
                color: #721c24;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


def main():
    """Main entry point for the Streamlit application."""
    # Create and run app (no DI container needed)
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()

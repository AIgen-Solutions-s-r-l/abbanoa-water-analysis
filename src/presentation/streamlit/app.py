"""
Main Streamlit application for Abbanoa Water Infrastructure Dashboard.

This module serves as the entry point for the Streamlit dashboard,
orchestrating the various tabs and components.
"""

import streamlit as st
from datetime import datetime
import asyncio
from typing import Optional

# Import components
from src.presentation.streamlit.components.forecast_tab import ForecastTab
from src.presentation.streamlit.components.sidebar_filters import SidebarFilters
from src.presentation.streamlit.utils.data_fetcher import DataFetcher
from src.presentation.streamlit.config.theme import apply_custom_theme

# Page configuration
st.set_page_config(
    page_title="Abbanoa Water Network Forecasting Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis',
        'Report a bug': 'https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis/issues',
        'About': 'Water Infrastructure Forecasting Dashboard v0.5.0'
    }
)

# Apply custom theme
apply_custom_theme()

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.district_id = "DIST_001"
    st.session_state.metric = "flow_rate"
    st.session_state.horizon = 7
    st.session_state.last_update = datetime.now()


class DashboardApp:
    """Main dashboard application class."""
    
    def __init__(self):
        """Initialize the dashboard application."""
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
                unsafe_allow_html=True
            )
        
        with col3:
            # Refresh button
            if st.button("🔄 Refresh", use_container_width=True):
                st.session_state.last_update = datetime.now()
                st.rerun()
            
            # Last updated time
            st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    def render_tabs(self) -> None:
        """Render the main tab navigation."""
        # Import the old dashboard components
        from src.presentation.streamlit.components.overview_tab import OverviewTab
        from src.presentation.streamlit.components.anomaly_tab import AnomalyTab
        from src.presentation.streamlit.components.consumption_tab import ConsumptionTab
        from src.presentation.streamlit.components.efficiency_tab import EfficiencyTab
        from src.presentation.streamlit.components.reports_tab import ReportsTab
        
        # Initialize old dashboard components
        overview_tab = OverviewTab()
        anomaly_tab = AnomalyTab()
        consumption_tab = ConsumptionTab()
        efficiency_tab = EfficiencyTab()
        reports_tab = ReportsTab()
        
        # Create tabs - combining new and old functionality
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Forecast",
            "📊 Overview", 
            "🔍 Anomaly Detection",
            "📈 Consumption Patterns",
            "🔗 Network Efficiency",
            "📋 Reports"
        ])
        
        with tab1:
            # New forecast tab
            self.forecast_tab.render()
        
        with tab2:
            # Old dashboard overview
            overview_tab.render(
                time_range=st.session_state.get('time_range', 'Last 24 Hours'),
                selected_nodes=st.session_state.get('selected_nodes', ['All Nodes'])
            )
        
        with tab3:
            # Anomaly detection from old dashboard
            anomaly_tab.render(
                time_range=st.session_state.get('time_range', 'Last 24 Hours')
            )
        
        with tab4:
            # Consumption patterns from old dashboard
            consumption_tab.render(
                time_range=st.session_state.get('time_range', 'Last 24 Hours'),
                selected_nodes=st.session_state.get('selected_nodes', ['All Nodes'])
            )
        
        with tab5:
            # Network efficiency from old dashboard
            efficiency_tab.render(
                time_range=st.session_state.get('time_range', 'Last 24 Hours')
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
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #999; font-size: 0.8rem;">
                Powered by BigQuery ML | ARIMA_PLUS Models | 
                <a href="https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis" 
                   style="color: #1f77b4;">View on GitHub</a>
            </div>
            """,
            unsafe_allow_html=True
        )


def main():
    """Main entry point for the Streamlit application."""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()
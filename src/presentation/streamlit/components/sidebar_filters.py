"""
Sidebar filters component for the Streamlit dashboard.

This module implements the interactive sidebar with district, metric,
and horizon selectors that update without page reloads.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Tuple

import streamlit as st


class SidebarFilters:
    """Sidebar filters component for parameter selection."""

    def __init__(self):
        """Initialize the sidebar filters."""
        self.districts = ["DIST_001", "DIST_002", "DIST_003"]
        self.metrics = {
            "flow_rate": "Flow Rate (L/s)",
            "reservoir_level": "Reservoir Level (m)",
            "pressure": "Pressure (bar)",
        }

    def render(self) -> None:
        """Render the sidebar with all filters."""
        with st.sidebar:
            # Logo/Header
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h2 style="color: #1f77b4;">💧 Abbanoa</h2>
                    <p style="color: #666; font-size: 0.9rem;">Water Infrastructure Monitor</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("---")

            # General Dashboard Filters (from old dashboard)
            st.markdown("### 📊 General Filters")

            # Time range selection
            time_range = st.selectbox(
                "Time Range",
                [
                    "Last 6 Hours",
                    "Last 24 Hours",
                    "Last 3 Days",
                    "Last Week",
                    "Last Month",
                    "Last Year",
                    "Custom Range",
                ],
                index=1,
                key="time_range",
                help="Select time range for overview and analysis tabs",
            )

            # Custom date range selector
            if time_range == "Custom Range":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Start Date",
                        value=None,
                        min_value=None,
                        max_value=None,
                        key="custom_start_date",
                        help="Select start date for custom range",
                    )
                with col2:
                    end_date = st.date_input(
                        "End Date",
                        value=None,
                        min_value=None,
                        max_value=None,
                        key="custom_end_date",
                        help="Select end date for custom range",
                    )

                # Store custom dates in session state
                if start_date and end_date:
                    st.session_state.custom_date_range = (start_date, end_date)
                    if start_date > end_date:
                        st.error("Start date must be before end date")
                else:
                    st.info("Please select both start and end dates")

            # Data availability notice
            with st.expander("📅 Data Availability"):
                st.info(
                    """
                    **Available Data Range:**
                    - Start: November 13, 2024
                    - End: March 31, 2025
                    
                    Data is available in 30-minute intervals
                    from Selargius monitoring nodes.
                    """
                )

            # Node selection
            selected_nodes = st.multiselect(
                "Select Nodes",
                [
                    "All Nodes",
                    "--- Original Nodes ---",
                    "Sant'Anna",
                    "Seneca",
                    "Selargius Tank",
                    "External Supply",
                    "--- Distribution Nodes ---",
                    "Distribution 215542",
                    "Distribution 215600",
                    "Distribution 273933",
                    "--- Monitoring Nodes ---",
                    "Monitoring 281492",
                    "Monitoring 288399",
                    "Monitoring 288400",
                ],
                default=["All Nodes"],
                key="selected_nodes",
                help="Select nodes to monitor",
            )

            st.markdown("---")

            # Filter Section for Forecast
            st.markdown("### 🎛️ Forecast Parameters")

            # District selector
            self._render_district_selector()

            # Metric selector
            self._render_metric_selector()

            # Horizon selector
            self._render_horizon_selector()

            st.markdown("---")

            # Additional options
            self._render_additional_options()

            # Connection status
            self._render_connection_status()

            # Info section
            self._render_info_section()

    def _render_district_selector(self) -> None:
        """Render the district selection dropdown."""
        st.selectbox(
            label="Select District",
            options=self.districts,
            index=self.districts.index(st.session_state.district_id),
            key="district_selector",
            help="Choose the district for forecast visualization",
            on_change=self._on_district_change,
        )

    def _render_metric_selector(self) -> None:
        """Render the metric selection dropdown."""
        # Create formatted options for display
        metric_options = list(self.metrics.keys())
        metric_labels = list(self.metrics.values())

        # Get current index
        current_index = metric_options.index(st.session_state.metric)

        # Create selectbox with formatted labels
        selected_label = st.selectbox(
            label="Select Metric",
            options=metric_labels,
            index=current_index,
            key="metric_selector",
            help="Choose the metric to forecast",
            on_change=self._on_metric_change,
        )

        # Store the actual metric value in session state
        selected_metric = [k for k, v in self.metrics.items() if v == selected_label][0]
        if selected_metric != st.session_state.metric:
            st.session_state.metric = selected_metric

    def _render_horizon_selector(self) -> None:
        """Render the forecast horizon slider."""
        horizon = st.slider(
            label="Forecast Horizon (days)",
            min_value=1,
            max_value=7,
            value=st.session_state.horizon,
            step=1,
            key="horizon_slider",
            help="Number of days to forecast",
            on_change=self._on_horizon_change,
        )

        # Display horizon info
        st.caption(f"Forecasting {horizon} day{'s' if horizon > 1 else ''} ahead")

    def _render_additional_options(self) -> None:
        """Render additional configuration options."""
        st.markdown("### ⚙️ Display Options")

        # Show confidence interval toggle
        show_ci = st.checkbox(
            "Show Confidence Interval",
            value=True,
            key="show_confidence_interval",
            help="Display 80% confidence interval bands on the forecast",
        )

        # Show historical data toggle
        show_historical = st.checkbox(
            "Show Historical Data",
            value=True,
            key="show_historical",
            help="Display 30 days of historical data before forecast",
        )

        # Auto-refresh toggle
        auto_refresh = st.checkbox(
            "Auto-refresh (5 min)",
            value=False,
            key="auto_refresh",
            help="Automatically refresh data every 5 minutes",
        )

        if auto_refresh:
            # Set up auto-refresh using st.empty() and time.sleep()
            st.info("Auto-refresh enabled")

    def _render_connection_status(self) -> None:
        """Render the database connection status."""
        st.markdown("---")
        st.markdown("### 🔌 Data Source")

        if st.session_state.get("bigquery_connected", False):
            st.success("✅ Connected to BigQuery")
        else:
            st.warning("⚠️ Using Demo Data")
            with st.expander("Setup BigQuery Connection"):
                st.markdown(
                    """
                    To connect to real data:
                    
                    1. Set environment variables:
                       - `BIGQUERY_PROJECT_ID`
                       - `GOOGLE_APPLICATION_CREDENTIALS`
                    
                    2. Ensure BigQuery tables exist:
                       - `monitoring_nodes`
                       - `sensor_readings`
                       - `water_networks`
                    
                    3. Populate tables with data
                    
                    The dashboard will automatically use
                    real data when available.
                    """
                )

    def _render_info_section(self) -> None:
        """Render the information section."""
        st.markdown("---")
        st.markdown("### ℹ️ Information")

        # Model info
        with st.expander("Model Information"):
            st.markdown(
                """
                **Model Type:** ARIMA_PLUS  
                **Training Data:** 2 years historical  
                **Update Frequency:** Daily  
                **Accuracy (MAPE):** < 15%  
                
                The model uses advanced time series
                forecasting with Italian holiday
                adjustments and seasonal patterns.
                """
            )

        # Help
        with st.expander("How to Use"):
            st.markdown(
                """
                1. **Select District:** Choose the water
                   distribution district to analyze
                   
                2. **Select Metric:** Pick the measurement
                   type (flow rate, pressure, or level)
                   
                3. **Set Horizon:** Adjust the number of
                   days to forecast (1-7 days)
                   
                4. **View Results:** The forecast will
                   update automatically without reloading
                   
                5. **Export Data:** Use the export buttons
                   to download forecast data
                """
            )

        # Performance metrics
        with st.expander("System Performance"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("API Latency", "< 300ms", "✓")
            with col2:
                st.metric("Cache TTL", "5 min", "↻")

    # Callback methods for state management
    def _on_district_change(self) -> None:
        """Handle district selection change."""
        new_district = st.session_state.district_selector
        if new_district != st.session_state.district_id:
            st.session_state.district_id = new_district
            # Clear cached data to force refresh
            st.session_state.forecast_data = None
            st.session_state.historical_data = None

    def _on_metric_change(self) -> None:
        """Handle metric selection change."""
        # Get the metric key from the label
        selected_label = st.session_state.metric_selector
        new_metric = [k for k, v in self.metrics.items() if v == selected_label][0]

        if new_metric != st.session_state.metric:
            st.session_state.metric = new_metric
            # Clear cached data to force refresh
            st.session_state.forecast_data = None
            st.session_state.historical_data = None

    def _on_horizon_change(self) -> None:
        """Handle horizon slider change."""
        new_horizon = st.session_state.horizon_slider
        if new_horizon != st.session_state.horizon:
            st.session_state.horizon = new_horizon
            # Clear forecast data to force refresh
            st.session_state.forecast_data = None

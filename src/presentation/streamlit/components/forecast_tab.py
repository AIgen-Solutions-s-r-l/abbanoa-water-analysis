"""
Forecast tab component for the Streamlit dashboard.

This module implements the main forecast visualization tab with interactive
Plotly charts and real-time data updates.
"""

from datetime import datetime
from typing import Optional
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.presentation.streamlit.utils.data_fetcher import DataFetcher
from src.presentation.streamlit.utils.plot_builder import PlotBuilder


class ForecastTab:
    """Forecast tab component for visualizing predictions."""

    def __init__(self, data_fetcher: DataFetcher):
        """
        Initialize the forecast tab.

        Args:
            data_fetcher: Data fetcher instance for retrieving forecast data
        """
        self.data_fetcher = data_fetcher
        self.plot_builder = PlotBuilder()
        self._init_session_state()

    def _init_session_state(self) -> None:
        """Initialize session state variables for the forecast tab."""
        if "forecast_data" not in st.session_state:
            st.session_state.forecast_data = None
        if "historical_data" not in st.session_state:
            st.session_state.historical_data = None
        if "loading_forecast" not in st.session_state:
            st.session_state.loading_forecast = False
        if "district_id" not in st.session_state:
            st.session_state.district_id = "selargius"  # Default district
        if "metric" not in st.session_state:
            st.session_state.metric = "flow_rate"  # Default metric
        if "horizon" not in st.session_state:
            st.session_state.horizon = 7  # Default horizon in days

    def render(self) -> None:
        """Main render method for the forecast tab."""
        # Create columns for layout
        col1, col2 = st.columns([3, 1])

        with col1:
            self._render_header()
            self._render_forecast_chart()

        with col2:
            self._render_metrics_cards()
            self._render_export_options()

    def _render_header(self) -> None:
        """Render the header section of the forecast tab."""
        st.markdown("### 📈 7-Day Forecast with Historical Context")

        # Create columns for controls
        col1, col2, col3 = st.columns(3)

        with col1:
            # District selector
            district_options = [
                "selargius",
                "monserrato",
                "quartu",
            ]  # Add more districts as needed
            district = st.selectbox(
                "District",
                options=district_options,
                index=(
                    district_options.index(st.session_state.district_id)
                    if st.session_state.district_id in district_options
                    else 0
                ),
                key="forecast_district",
            )
            if district != st.session_state.district_id:
                st.session_state.district_id = district
                st.session_state.forecast_data = None  # Reset data to trigger refresh

        with col2:
            # Metric selector
            metric_options = {
                "flow_rate": "Flow Rate (L/s)",
                "reservoir_level": "Reservoir Level (m)",
                "pressure": "Pressure (bar)",
            }
            metric = st.selectbox(
                "Metric",
                options=list(metric_options.keys()),
                format_func=lambda x: metric_options[x],
                index=(
                    list(metric_options.keys()).index(st.session_state.metric)
                    if st.session_state.metric in metric_options
                    else 0
                ),
                key="forecast_metric",
            )
            if metric != st.session_state.metric:
                st.session_state.metric = metric
                st.session_state.forecast_data = None  # Reset data to trigger refresh

        with col3:
            # Horizon selector
            horizon_options = [3, 7, 14, 30]
            horizon = st.selectbox(
                "Forecast Days",
                options=horizon_options,
                index=(
                    horizon_options.index(st.session_state.horizon)
                    if st.session_state.horizon in horizon_options
                    else 1
                ),
                key="forecast_horizon",
            )
            if horizon != st.session_state.horizon:
                st.session_state.horizon = horizon
                st.session_state.forecast_data = None  # Reset data to trigger refresh

        # Display current selection
        st.markdown(
            f"""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                <strong>Current Selection:</strong> {st.session_state.district_id} | {metric_options.get(st.session_state.metric, st.session_state.metric)} | {st.session_state.horizon} days
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _render_forecast_chart(self) -> None:
        """Render the main forecast visualization chart."""
        # Create container for the chart
        chart_container = st.container()

        with chart_container:
            # Check if we need to fetch new data
            if self._should_fetch_data():
                with st.spinner("Loading forecast data..."):
                    self._fetch_and_cache_data()

            # Get data from session state
            forecast_df = st.session_state.forecast_data
            historical_df = st.session_state.historical_data

            if forecast_df is not None and not forecast_df.empty:
                # Build the Plotly figure
                fig = self._build_forecast_plot(historical_df, forecast_df)

                # Display the chart
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": f"forecast_{st.session_state.district_id}_{st.session_state.metric}",
                        },
                    },
                )
            else:
                # Provide more helpful message and debug info
                st.warning("📊 No forecast data loaded yet.")
                st.info(
                    """
                **To view forecasts:**
                1. Ensure the API server is running (`./run_api.sh`)
                2. Click the button below to load forecast data
                
                The forecast will show:
                - 7-day predictions with 80% confidence intervals
                - Historical context from the last 30 days
                - ARIMA model predictions or fallback calculations
                """
                )
                if st.button("🔄 Load Forecast Data", type="primary"):
                    with st.spinner("Loading forecast data..."):
                        self._fetch_and_cache_data()
                    st.rerun()

    def _should_fetch_data(self) -> bool:
        """Check if new data should be fetched."""
        # Always fetch if no data exists
        if st.session_state.forecast_data is None:
            return True

        # Check if parameters changed (handled by sidebar callbacks)
        return False

    def _fetch_forecast_data(
        self, district_id: str, metric: str, horizon: int
    ) -> pd.DataFrame:
        """
        Fetch forecast data with caching.

        Args:
            district_id: District identifier
            metric: Metric type
            horizon: Forecast horizon in days

        Returns:
            DataFrame with forecast data
        """

        # Use a separate cached function to avoid hashing self
        @st.cache_data(ttl=300)  # Cache for 5 minutes
        def _cached_fetch(district_id: str, metric: str, horizon: int) -> pd.DataFrame:
            # Create a new data fetcher instance inside the cached function
            from src.presentation.streamlit.utils.data_fetcher import DataFetcher

            fetcher = DataFetcher()
            return fetcher.get_forecast(district_id, metric, horizon)

        return _cached_fetch(district_id, metric, horizon)

    def _fetch_historical_data(
        self, district_id: str, metric: str, days_back: int = 30
    ) -> pd.DataFrame:
        """
        Fetch historical data with caching.

        Args:
            district_id: District identifier
            metric: Metric type
            days_back: Number of days of historical data

        Returns:
            DataFrame with historical data
        """

        # Use a separate cached function to avoid hashing self
        @st.cache_data(ttl=3600)  # Cache for 1 hour
        def _cached_fetch_historical(
            district_id: str, metric: str, days_back: int
        ) -> pd.DataFrame:
            # Create a new data fetcher instance inside the cached function
            from src.presentation.streamlit.utils.data_fetcher import DataFetcher

            fetcher = DataFetcher()
            return fetcher.get_historical_data(district_id, metric, days_back)

        return _cached_fetch_historical(district_id, metric, days_back)

    def _fetch_and_cache_data(self) -> None:
        """Fetch both forecast and historical data and update session state."""
        try:
            # Get current parameters
            district_id = st.session_state.district_id
            metric = st.session_state.metric
            horizon = st.session_state.horizon

            # Fetch forecast data
            forecast_df = self._fetch_forecast_data(district_id, metric, horizon)
            st.session_state.forecast_data = forecast_df

            # Fetch historical data
            historical_df = self._fetch_historical_data(district_id, metric, 30)
            st.session_state.historical_data = historical_df

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.session_state.forecast_data = pd.DataFrame()
            st.session_state.historical_data = pd.DataFrame()

    def _build_forecast_plot(
        self, historical_df: Optional[pd.DataFrame], forecast_df: pd.DataFrame
    ) -> go.Figure:
        """
        Build the Plotly figure for forecast visualization.

        Args:
            historical_df: Historical data
            forecast_df: Forecast data

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        # Add historical data trace if available
        if historical_df is not None and not historical_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=historical_df["timestamp"],
                    y=historical_df["value"],
                    mode="lines",
                    name="Historical",
                    line=dict(color="#1f77b4", width=2),
                    hovertemplate="<b>Historical</b><br>"
                    + "Date: %{x|%Y-%m-%d %H:%M}<br>"
                    + "Value: %{y:.2f}<br>"
                    + "<extra></extra>",
                )
            )

        # Add forecast trace - use 'predicted' column from DataFetcher
        fig.add_trace(
            go.Scatter(
                x=forecast_df["timestamp"],
                y=forecast_df["predicted"],
                mode="lines+markers",
                name="Forecast",
                line=dict(color="#ff7f0e", width=2, dash="dash"),
                marker=dict(size=6),
                hovertemplate="<b>Forecast</b><br>"
                + "Date: %{x|%Y-%m-%d}<br>"
                + "Value: %{y:.2f}<br>"
                + "<extra></extra>",
            )
        )

        # Add confidence interval - directly use backend-calculated bounds
        if (
            "lower_bound" in forecast_df.columns
            and "upper_bound" in forecast_df.columns
        ):
            # Add upper bound (invisible)
            fig.add_trace(
                go.Scatter(
                    x=forecast_df["timestamp"],
                    y=forecast_df["upper_bound"],
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

            # Add lower bound with fill
            fig.add_trace(
                go.Scatter(
                    x=forecast_df["timestamp"],
                    y=forecast_df["lower_bound"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(255, 127, 14, 0.2)",
                    name="80% Confidence Interval",
                    hovertemplate="<b>Confidence Interval</b><br>"
                    + "Date: %{x|%Y-%m-%d}<br>"
                    + "Lower: %{y:.2f}<br>"
                    + "<extra></extra>",
                )
            )

        # Update layout
        metric_units = {
            "flow_rate": "Flow Rate (L/s)",
            "reservoir_level": "Reservoir Level (m)",
            "pressure": "Pressure (bar)",
        }

        fig.update_layout(
            title={
                "text": f"7-Day Forecast: {st.session_state.district_id} - {metric_units.get(st.session_state.metric, '')}",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 20},
            },
            xaxis_title="Date",
            yaxis_title=metric_units.get(st.session_state.metric, "Value"),
            template="plotly_white",
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            xaxis=dict(rangeslider=dict(visible=False), type="date"),
            yaxis=dict(fixedrange=False),
        )

        # Note: Vertical line for "now" removed due to Plotly timestamp compatibility issues
        # Can be re-added once timestamp format is standardized

        return fig

    def _render_metrics_cards(self) -> None:
        """Render metrics cards showing key statistics."""
        st.markdown("### 📊 Key Metrics")

        forecast_df = st.session_state.forecast_data

        if forecast_df is not None and not forecast_df.empty:
            # Use pre-calculated values from backend - no frontend calculations
            current_value = forecast_df["predicted"].iloc[0]

            # Display metrics
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="Next Day Forecast",
                    value=f"{current_value:.2f}",
                    delta=None,  # Could be provided by backend if needed
                )

            with col2:
                # Use confidence level directly from data
                confidence_level = 80  # Default 80% confidence intervals
                st.metric(
                    label="Confidence Level",
                    value=f"{confidence_level}%",
                    delta=None,
                )

            # Model info
            st.info(
                f"**Model:** ARIMA_PLUS | **Updated:** {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}"
            )
        else:
            st.info("Select parameters to view metrics")

    def _render_export_options(self) -> None:
        """Render export options for data and charts."""
        st.markdown("### 💾 Export Options")

        forecast_df = st.session_state.forecast_data

        if forecast_df is not None and not forecast_df.empty:
            # Prepare data for export
            export_df = forecast_df.copy()
            export_df["district_id"] = st.session_state.district_id
            export_df["metric"] = st.session_state.metric

            # CSV download button
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"forecast_{st.session_state.district_id}_{st.session_state.metric}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # Excel download would require xlsxwriter
            # JSON download
            json_str = export_df.to_json(orient="records", date_format="iso")
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"forecast_{st.session_state.district_id}_{st.session_state.metric}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.info("No data to export")

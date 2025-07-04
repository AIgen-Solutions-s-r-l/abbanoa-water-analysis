"""
Consumption patterns tab component for the integrated dashboard.

This component analyzes and displays water consumption patterns across the network.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.application.dto.analysis_results_dto import ConsumptionPatternDTO
from src.application.use_cases.analyze_consumption_patterns import (
    AnalyzeConsumptionPatternsUseCase,
)


class ConsumptionTab:
    """Consumption patterns analysis tab."""

    def __init__(self, analyze_consumption_use_case: AnalyzeConsumptionPatternsUseCase):
        """Initialize the consumption tab with use case."""
        self.analyze_consumption_use_case = analyze_consumption_use_case

    def render(self, time_range: str, selected_nodes: List[str]) -> None:
        """
        Render the consumption patterns tab.

        Args:
            time_range: Selected time range
            selected_nodes: List of selected nodes
        """
        st.header("📈 Consumption Patterns Analysis")

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="Total Consumption", value="0 m³", delta=None)

        with col2:
            st.metric(label="Peak Hour", value="--:--", delta=None)

        with col3:
            st.metric(label="Min Hour", value="--:--", delta=None)

        with col4:
            st.metric(label="Avg Daily", value="0 m³", delta=None)

        # Consumption trends
        st.subheader("Consumption Trends")
        self._render_consumption_trends(time_range, selected_nodes)

        # Pattern analysis
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Daily Pattern")
            self._render_daily_pattern()

        with col2:
            st.subheader("Weekly Pattern")
            self._render_weekly_pattern()

        # Peak analysis
        st.subheader("Peak Consumption Analysis")
        self._render_peak_analysis(selected_nodes)

        # Consumption heatmap
        st.subheader("Consumption Heatmap")
        self._render_consumption_heatmap()

        # Efficiency metrics
        st.subheader("Consumption Efficiency")
        self._render_efficiency_metrics()

    def _render_consumption_trends(
        self, time_range: str, selected_nodes: List[str]
    ) -> None:
        """Render consumption trends chart."""
        # Get real consumption data
        consumption_data = self._get_consumption_data(time_range, selected_nodes)

        if consumption_data is not None and not consumption_data.empty:
            df = consumption_data
        else:
            # Return empty dataframe - no synthetic data
            data = {"timestamp": pd.DatetimeIndex([])}

            nodes = (
                ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"]
                if "All Nodes" in selected_nodes
                else selected_nodes
            )

            for node in nodes:
                data[node] = []

            df = pd.DataFrame(data)

        # Create line chart
        fig = px.line(
            df,
            x="timestamp",
            y=[col for col in df.columns if col != "timestamp"],
            title="Water Consumption Trends",
            labels={"value": "Consumption (m³/h)", "timestamp": "Time"},
        )

        fig.update_layout(
            height=400,
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_daily_pattern(self) -> None:
        """Render average daily consumption pattern."""
        hours = list(range(24))
        consumption = [0] * 24  # No synthetic data

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=consumption,
                mode="lines+markers",
                name="Average",
                line=dict(color="#1f77b4", width=3),
                fill="tozeroy",
                fillcolor="rgba(31, 119, 180, 0.2)",
            )
        )

        # Add peak hours annotation
        peak_hour = consumption.index(max(consumption))
        fig.add_annotation(
            x=peak_hour,
            y=max(consumption),
            text=f"Peak: {peak_hour}:00",
            showarrow=True,
            arrowhead=2,
        )

        fig.update_layout(
            height=350,
            xaxis_title="Hour of Day",
            yaxis_title="Consumption (m³/h)",
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_weekly_pattern(self) -> None:
        """Render weekly consumption pattern."""
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        consumption = [0, 0, 0, 0, 0, 0, 0]  # No synthetic data

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=days,
                y=consumption,
                marker_color=[
                    "#1f77b4" if c >= 100 else "#ff7f0e" for c in consumption
                ],
                text=[f"{c}%" for c in consumption],
                textposition="outside",
            )
        )

        fig.update_layout(
            height=350,
            xaxis_title="Day of Week",
            yaxis_title="Relative Consumption (%)",
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_peak_analysis(self, selected_nodes: List[str]) -> None:
        """Render peak consumption analysis."""
        nodes = (
            ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"]
            if "All Nodes" in selected_nodes
            else selected_nodes
        )

        # Create peak data - no synthetic values
        peak_data = []
        for node in nodes[:4]:  # Limit to 4 nodes
            peak_data.append(
                {
                    "Node": node,
                    "Morning Peak (6-9)": 0,
                    "Evening Peak (18-21)": 0,
                    "Night Minimum (2-5)": 0,
                }
            )

        df = pd.DataFrame(peak_data)

        # Create grouped bar chart
        fig = go.Figure()

        for col in [
            "Morning Peak (6-9)",
            "Evening Peak (18-21)",
            "Night Minimum (2-5)",
        ]:
            fig.add_trace(
                go.Bar(
                    name=col,
                    x=df["Node"],
                    y=df[col],
                    text=[f"{v:.0f}" for v in df[col]],
                    textposition="outside",
                )
            )

        fig.update_layout(
            height=350,
            barmode="group",
            xaxis_title="Node",
            yaxis_title="Consumption (m³/h)",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_consumption_heatmap(self) -> None:
        """Render consumption heatmap by hour and day."""
        # Generate heatmap data
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = list(range(24))

        # No synthetic data - all zeros
        z_data = [[0] * 24 for _ in days]

        fig = go.Figure(
            data=go.Heatmap(
                z=z_data,
                x=hours,
                y=days,
                colorscale="Blues",
                text=[[f"{val:.0f}" for val in row] for row in z_data],
                texttemplate="%{text}",
                textfont={"size": 10},
            )
        )

        fig.update_layout(
            height=300,
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            title="Water Consumption Heatmap (m³/h)",
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_efficiency_metrics(self) -> None:
        """Render consumption efficiency metrics."""
        col1, col2, col3 = st.columns(3)

        with col1:
            # Non-revenue water - no data
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=0,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Non-Revenue Water (%)"},
                    delta={"reference": 0},
                    gauge={
                        "axis": {"range": [None, 20]},
                        "bar": {"color": "#1f77b4"},
                        "steps": [
                            {"range": [0, 5], "color": "lightgreen"},
                            {"range": [5, 10], "color": "yellow"},
                            {"range": [10, 20], "color": "lightcoral"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 15,
                        },
                    },
                )
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Per capita consumption - no data
            fig = go.Figure(
                go.Indicator(
                    mode="number+delta",
                    value=0,
                    number={"suffix": " L/day"},
                    title={"text": "Per Capita Consumption"},
                    delta={"reference": 0},
                )
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            # System efficiency - no data
            fig = go.Figure(
                go.Indicator(
                    mode="number+delta",
                    value=0,
                    number={"suffix": "%"},
                    title={"text": "Distribution Efficiency"},
                    delta={"reference": 0},
                )
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

    def _get_hourly_factor(self, hour: int) -> float:
        """Get consumption factor for given hour."""
        # Typical residential consumption pattern
        if 6 <= hour <= 9:  # Morning peak
            return 1.2 + 0.1 * (hour - 6)
        elif 18 <= hour <= 21:  # Evening peak
            return 1.1 + 0.05 * (hour - 18)
        elif 0 <= hour <= 5:  # Night minimum
            return 0.5 + 0.05 * hour
        else:  # Daytime normal
            return 1.0

    def _get_time_params(self, time_range: str) -> tuple:
        """Get time parameters based on selected range."""
        params = {
            "Last 6 Hours": (12, "30min"),
            "Last 24 Hours": (48, "30min"),
            "Last 3 Days": (72, "H"),
            "Last Week": (168, "H"),
            "Last Month": (720, "H"),  # 30 days
            "Last Year": (8760, "H"),  # 365 days
            "Custom Range": None,  # Will be handled separately
        }
        return params.get(time_range, (48, "30min"))

    def _get_consumption_data(
        self, time_range: str, selected_nodes: List[str]
    ) -> Optional[pd.DataFrame]:
        """Get real consumption data directly from repository."""
        try:
            # Calculate time delta
            time_deltas = {
                "Last 6 Hours": timedelta(hours=6),
                "Last 24 Hours": timedelta(hours=24),
                "Last 3 Days": timedelta(days=3),
                "Last Week": timedelta(days=7),
                "Last Month": timedelta(days=30),
                "Last Year": timedelta(days=365),
            }

            # Handle custom date range
            if time_range == "Custom Range" and hasattr(
                st.session_state, "custom_date_range"
            ):
                start_date, end_date = st.session_state.custom_date_range
                # Convert dates to datetime
                start_time = datetime.combine(start_date, datetime.min.time())
                end_time = datetime.combine(end_date, datetime.max.time())
            else:
                delta = time_deltas.get(time_range, timedelta(hours=24))
                # Use the actual available data range: November 13, 2024 to March 31, 2025
                data_end = datetime(2025, 3, 31, 23, 59, 59)
                data_start = datetime(2024, 11, 13, 0, 0, 0)

                # Calculate desired end time (use current time or data end, whichever is earlier)
                end_time = min(data_end, datetime.now())

                # Calculate start time, but don't go before data start
                proposed_start = end_time - delta
                start_time = max(proposed_start, data_start)

            # Get data directly from repository
            from uuid import UUID

            from src.infrastructure.di_container import Container

            container = Container()
            container.config.from_dict(
                {
                    "bigquery": {
                        "project_id": "abbanoa-464816",
                        "dataset_id": "water_infrastructure",
                        "credentials_path": None,
                        "location": "US",
                    }
                }
            )

            sensor_repo = container.sensor_reading_repository()

            # Define node mappings
            node_mapping = {
                "Sant'Anna": UUID("00000000-0000-0000-0000-000000000001"),
                "Seneca": UUID("00000000-0000-0000-0000-000000000002"),
                "Selargius Tank": UUID("00000000-0000-0000-0000-000000000003"),
            }

            # Determine which nodes to fetch
            if "All Nodes" in selected_nodes:
                nodes_to_fetch = list(node_mapping.keys())
            else:
                nodes_to_fetch = [
                    node for node in selected_nodes if node in node_mapping
                ]

            if not nodes_to_fetch:
                st.warning("No valid nodes selected")
                return None

            # Fetch data for each node
            all_data = []
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            for node_name in nodes_to_fetch:
                node_id = node_mapping[node_name]
                try:
                    readings = loop.run_until_complete(
                        sensor_repo.get_by_node_id(
                            node_id=node_id, start_time=start_time, end_time=end_time
                        )
                    )

                    for reading in readings:
                        # Handle both value objects and raw values
                        flow_val = reading.flow_rate
                        if hasattr(flow_val, "value"):
                            flow_val = flow_val.value
                        elif flow_val is None:
                            flow_val = 0

                        vol_val = reading.volume
                        if hasattr(vol_val, "value"):
                            vol_val = vol_val.value
                        elif vol_val is None:
                            vol_val = 0

                        all_data.append(
                            {
                                "timestamp": reading.timestamp,
                                "node_name": node_name,
                                "flow_rate": float(flow_val),
                                "volume": float(vol_val),
                            }
                        )

                except Exception as e:
                    st.warning(f"Error fetching data for {node_name}: {str(e)}")
                    continue

            if not all_data:
                st.info(
                    f"No data found for the selected time range ({start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')})"
                )
                return None

            # Convert to DataFrame and pivot
            df = pd.DataFrame(all_data)
            df = df.pivot_table(
                index="timestamp",
                columns="node_name",
                values="flow_rate",
                aggfunc="mean",
            ).reset_index()

            # Fill NaN values with 0
            df = df.fillna(0)

            st.success(
                f"✅ Found {len(all_data)} readings across {len(nodes_to_fetch)} nodes"
            )

            return df

        except Exception as e:
            # Show specific error for debugging
            st.error(f"Error fetching consumption data: {str(e)}")
            st.info(
                "Possible causes: BigQuery not connected, no data in selected range, or missing credentials."
            )
            import traceback

            st.code(traceback.format_exc())

        return None

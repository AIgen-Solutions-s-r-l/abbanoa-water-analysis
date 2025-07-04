"""
Network efficiency tab component for the integrated dashboard.

This component displays network efficiency metrics and performance indicators.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.application.dto.analysis_results_dto import NetworkEfficiencyResultDTO
from src.application.use_cases.calculate_network_efficiency import (
    CalculateNetworkEfficiencyUseCase,
)


class EfficiencyTab:
    """Network efficiency analysis tab."""

    def __init__(
        self, calculate_efficiency_use_case: CalculateNetworkEfficiencyUseCase
    ):
        """Initialize the efficiency tab with use case."""
        self.calculate_efficiency_use_case = calculate_efficiency_use_case
        self._efficiency_cache = None
        self._cache_time = None

    def render(self, time_range: str) -> None:
        """
        Render the network efficiency tab.

        Args:
            time_range: Selected time range
        """
        st.header("🔗 Network Efficiency Analysis")

        # Get real efficiency data
        efficiency_data = self._get_efficiency_data(time_range)

        # Key efficiency metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Overall Efficiency",
                value=(
                    f"{efficiency_data.efficiency_percentage:.1f}%"
                    if efficiency_data
                    else "0.0%"
                ),
                delta=None,
            )

        with col2:
            st.metric(
                label="Water Loss Rate",
                value=(
                    f"{efficiency_data.loss_percentage:.1f}%"
                    if efficiency_data
                    else "0.0%"
                ),
                delta=None,
            )

        with col3:
            # Use custom attribute if available, otherwise calculate
            energy_eff = (
                getattr(efficiency_data, "energy_efficiency", 0)
                if efficiency_data
                else 0
            )
            st.metric(
                label="Energy Efficiency",
                value=f"{energy_eff:.2f} kWh/m³" if energy_eff else "0.00 kWh/m³",
                delta=None,
            )

        with col4:
            st.metric(label="Network Pressure", value="0.0 bar", delta=None)

        # Efficiency trends
        st.subheader("Efficiency Trends")
        self._render_efficiency_trends(time_range)

        # Component analysis
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Component Efficiency")
            self._render_component_efficiency()

        with col2:
            st.subheader("Loss Distribution")
            self._render_loss_distribution()

        # Pressure analysis
        st.subheader("Network Pressure Analysis")
        self._render_pressure_analysis()

        # Energy consumption
        st.subheader("Energy Consumption Analysis")
        self._render_energy_analysis()

        # Recommendations
        st.subheader("Efficiency Recommendations")
        self._render_recommendations()

    def _render_efficiency_trends(self, time_range: str) -> None:
        """Render efficiency trends over time."""
        # No synthetic data - use empty data
        time_data = pd.DatetimeIndex([])
        efficiency_trend = []
        water_loss = []
        energy_consumption = []

        # Create subplot figure
        fig = make_subplots(
            rows=3,
            cols=1,
            subplot_titles=(
                "Overall Efficiency (%)",
                "Water Loss Rate (%)",
                "Energy Consumption (kWh/m³)",
            ),
            vertical_spacing=0.1,
        )

        # Overall efficiency
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=efficiency_trend,
                mode="lines",
                name="Efficiency",
                line=dict(color="#2ca02c", width=2),
                fill="tozeroy",
                fillcolor="rgba(44, 160, 44, 0.1)",
            ),
            row=1,
            col=1,
        )

        # Water loss
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=water_loss,
                mode="lines",
                name="Water Loss",
                line=dict(color="#dc3545", width=2),
                fill="tozeroy",
                fillcolor="rgba(220, 53, 69, 0.1)",
            ),
            row=2,
            col=1,
        )

        # Energy consumption
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=energy_consumption,
                mode="lines",
                name="Energy",
                line=dict(color="#ff7f0e", width=2),
            ),
            row=3,
            col=1,
        )

        # Add target lines
        fig.add_hline(
            y=95,
            line_dash="dash",
            line_color="green",
            row=1,
            col=1,
            annotation_text="Target: 95%",
        )
        fig.add_hline(
            y=5,
            line_dash="dash",
            line_color="red",
            row=2,
            col=1,
            annotation_text="Target: <5%",
        )
        fig.add_hline(
            y=0.40,
            line_dash="dash",
            line_color="orange",
            row=3,
            col=1,
            annotation_text="Target: 0.40",
        )

        fig.update_layout(height=600, showlegend=False, hovermode="x unified")

        st.plotly_chart(fig, use_container_width=True)

    def _render_component_efficiency(self) -> None:
        """Render component-wise efficiency breakdown."""
        components = ["Pumps", "Valves", "Pipes", "Meters", "Storage"]
        efficiency = [0, 0, 0, 0, 0]  # No synthetic data

        fig = go.Figure(
            go.Bar(
                x=components,
                y=efficiency,
                marker_color=[
                    "green" if e >= 92 else "orange" if e >= 88 else "red"
                    for e in efficiency
                ],
                text=[f"{e}%" for e in efficiency],
                textposition="outside",
            )
        )

        # Add target line
        fig.add_hline(
            y=92, line_dash="dash", line_color="gray", annotation_text="Target"
        )

        fig.update_layout(
            height=350,
            xaxis_title="Component",
            yaxis_title="Efficiency (%)",
            yaxis_range=[80, 100],
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_loss_distribution(self) -> None:
        """Render water loss distribution pie chart."""
        labels = ["No Data"]
        values = [1]  # Need at least one value for pie chart

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker_colors=["#dc3545", "#ff7f0e", "#ffc107", "#6c757d"],
                )
            ]
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hoverinfo="label+percent+value",
        )

        fig.update_layout(
            height=350,
            annotations=[
                dict(text="Water<br>Loss", x=0.5, y=0.5, font_size=20, showarrow=False)
            ],
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_pressure_analysis(self) -> None:
        """Render network pressure analysis."""
        # No synthetic data
        zones = ["Zone A", "Zone B", "Zone C", "Zone D"]
        current_pressure = [0, 0, 0, 0]
        optimal_min = [0, 0, 0, 0]
        optimal_max = [0, 0, 0, 0]

        fig = go.Figure()

        # Add optimal range
        fig.add_trace(
            go.Scatter(
                x=zones + zones[::-1],
                y=optimal_max + optimal_min[::-1],
                fill="toself",
                fillcolor="rgba(0, 255, 0, 0.1)",
                line=dict(color="rgba(255, 255, 255, 0)"),
                showlegend=True,
                name="Optimal Range",
            )
        )

        # Add current pressure
        fig.add_trace(
            go.Scatter(
                x=zones,
                y=current_pressure,
                mode="lines+markers",
                name="Current Pressure",
                line=dict(color="#1f77b4", width=3),
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            height=300,
            xaxis_title="Network Zone",
            yaxis_title="Pressure (bar)",
            yaxis_range=[3, 5],
            hovermode="x",
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_energy_analysis(self) -> None:
        """Render energy consumption analysis."""
        # No synthetic data - all zeros
        hours = list(range(24))
        pumping_energy = [0] * 24
        treatment_energy = [0] * 24
        distribution_energy = [0] * 24

        fig = go.Figure()

        # Stacked area chart
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=pumping_energy,
                mode="lines",
                name="Pumping",
                stackgroup="one",
                fillcolor="rgba(31, 119, 180, 0.5)",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=hours,
                y=treatment_energy,
                mode="lines",
                name="Treatment",
                stackgroup="one",
                fillcolor="rgba(255, 127, 14, 0.5)",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=hours,
                y=distribution_energy,
                mode="lines",
                name="Distribution",
                stackgroup="one",
                fillcolor="rgba(44, 160, 44, 0.5)",
            )
        )

        fig.update_layout(
            height=350,
            xaxis_title="Hour of Day",
            yaxis_title="Energy Consumption (kWh)",
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_recommendations(self) -> None:
        """Render efficiency improvement recommendations."""
        # No synthetic data
        recommendations = []

        if recommendations:
            df = pd.DataFrame(recommendations)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Priority": st.column_config.TextColumn("Priority", width="small"),
                    "Area": st.column_config.TextColumn("Area", width="medium"),
                    "Issue": st.column_config.TextColumn("Issue", width="large"),
                    "Action": st.column_config.TextColumn(
                        "Recommended Action", width="large"
                    ),
                    "Impact": st.column_config.TextColumn(
                        "Expected Impact", width="medium"
                    ),
                },
            )
        else:
            st.info("No recommendations available. Waiting for real data.")

    def _get_energy_factor(self, hour: int) -> float:
        """Get energy consumption factor for given hour."""
        # Energy consumption pattern
        if 6 <= hour <= 9:  # Morning peak
            return 1.3
        elif 18 <= hour <= 21:  # Evening peak
            return 1.2
        elif 0 <= hour <= 5:  # Night minimum
            return 0.6
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
            "Custom Range": None,  # Will be handled separately
        }
        return params.get(time_range, (48, "30min"))

    def _get_efficiency_data(self, time_range: str) -> NetworkEfficiencyResultDTO:
        """Get real efficiency data from use case."""
        try:
            # Use cache if available and recent
            if self._efficiency_cache and self._cache_time:
                if self._cache_time and datetime.now() - self._cache_time < timedelta(
                    minutes=5
                ):
                    return self._efficiency_cache

            # Calculate time delta
            time_deltas = {
                "Last 6 Hours": timedelta(hours=6),
                "Last 24 Hours": timedelta(hours=24),
                "Last 3 Days": timedelta(days=3),
                "Last Week": timedelta(days=7),
                "Last Month": timedelta(days=30),
                "Last Year": timedelta(days=365),
            }

            delta = time_deltas.get(time_range, timedelta(hours=24))
            # Return None - no synthetic data
            end_time = None
            start_time = None

            # Run the use case
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                self.calculate_efficiency_use_case.execute(
                    start_time=start_time, end_time=end_time
                )
            )

            # Cache the result
            self._efficiency_cache = result
            self._cache_time = datetime.now() if result else None

            return result

        except Exception as e:
            # Return None - no synthetic data
            return None

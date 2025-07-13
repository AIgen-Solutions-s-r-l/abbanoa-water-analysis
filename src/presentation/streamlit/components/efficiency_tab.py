"""
Network efficiency tab component for the integrated dashboard.

This component displays network efficiency metrics and performance indicators
using the new DataFetcher utility with proper loading states and error handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.presentation.streamlit.utils.data_fetcher import DataFetcher
from src.presentation.streamlit.utils.plot_builder import PlotBuilder


class EfficiencyTab:
    """Network efficiency analysis tab using DataFetcher."""

    def __init__(self, calculate_efficiency_use_case=None):
        """Initialize the efficiency tab with DataFetcher."""
        self.data_fetcher = DataFetcher()
        self.plot_builder = PlotBuilder()

    def render(self, time_range: str) -> None:
        """
        Render the network efficiency tab.

        Args:
            time_range: Selected time range
        """
        st.header("🔗 Network Efficiency Analysis")

        # Loading state
        with st.spinner("Loading efficiency data..."):
            try:
                # Get efficiency summary data with loading state
                efficiency_data = self._get_efficiency_data_with_loading(time_range)
                
                if not efficiency_data:
                    st.error("❌ Unable to load efficiency data. Please check the API connection.")
                    return
                
                # Display main metrics
                self._render_main_metrics(efficiency_data)
                
                # Display efficiency trends
                self._render_efficiency_trends(time_range)
                
                # Display component analysis
                col1, col2 = st.columns(2)
                with col1:
                    self._render_component_efficiency()
                with col2:
                    self._render_loss_distribution()
                
                # Display pressure analysis
                self._render_pressure_analysis(time_range)
                
            except Exception as e:
                st.error(f"❌ Error loading efficiency data: {str(e)}")
                # Show fallback data in case of errors
                self._render_fallback_interface()

    def _get_efficiency_data_with_loading(self, time_range: str) -> Optional[Dict[str, Any]]:
        """Get efficiency data with proper loading state handling."""
        try:
            # Convert time_range to datetime range
            start_time, end_time = self._convert_time_range(time_range)
            
            # Get data using the new DataFetcher
            efficiency_data = self.data_fetcher.get_efficiency_summary(
                start_time=start_time,
                end_time=end_time
            )
            
            return efficiency_data
            
        except Exception as e:
            st.error(f"Error fetching efficiency data: {str(e)}")
            return None

    def _convert_time_range(self, time_range: str) -> tuple[datetime, datetime]:
        """Convert time range string to datetime objects."""
        time_deltas = {
            "Last 6 Hours": timedelta(hours=6),
            "Last 24 Hours": timedelta(hours=24),
            "Last 3 Days": timedelta(days=3),
            "Last Week": timedelta(days=7),
            "Last Month": timedelta(days=30),
            "Last Year": timedelta(days=365),
        }
        
        delta = time_deltas.get(time_range, timedelta(hours=24))
        end_time = datetime.now()
        start_time = end_time - delta
        
        return start_time, end_time

    def _render_main_metrics(self, efficiency_data: Dict[str, Any]) -> None:
        """Render the main efficiency metrics cards."""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            efficiency_pct = efficiency_data.get('efficiency_percentage', 0)
            active_nodes = efficiency_data.get('active_nodes', 0)
            total_nodes = efficiency_data.get('total_nodes', 8)
            
            st.metric(
                label="Overall Efficiency",
                value=f"{efficiency_pct:.1f}%",
                delta=f"Active nodes: {active_nodes}/{total_nodes}",
                delta_color="normal"
            )

        with col2:
            loss_m3h = efficiency_data.get('loss_m3_per_hour', 0)
            st.metric(
                label="Water Loss Rate",
                value=f"{loss_m3h:.1f} m³/h",
                delta="Target: <15 m³/h",
                delta_color="inverse" if loss_m3h > 15 else "normal"
            )

        with col3:
            avg_pressure = efficiency_data.get('avg_pressure_mh2o', 0)
            st.metric(
                label="Avg Pressure",
                value=f"{avg_pressure:.1f} mH₂O",
                delta="Optimal: 2.5-3.5 mH₂O",
                delta_color="normal" if 2.5 <= avg_pressure <= 3.5 else "inverse"
            )

        with col4:
            reservoir_level = efficiency_data.get('reservoir_level_percentage', 0)
            st.metric(
                label="Reservoir Level",
                value=f"{reservoir_level:.1f}%",
                delta="Target: >70%",
                delta_color="normal" if reservoir_level > 70 else "inverse"
            )

    def _render_efficiency_trends(self, time_range: str) -> None:
        """Render efficiency trends over time."""
        st.subheader("Efficiency Trends")
        
        with st.spinner("Loading trend data..."):
            try:
                # Get hours back from time range
                hours_back = self._get_hours_from_time_range(time_range)
                
                # Get trend data
                trend_data = self.data_fetcher.get_efficiency_trends(hours_back=hours_back)
                
                if trend_data.empty:
                    st.warning("No trend data available for the selected time range")
                    return
                
                # Create trend chart
                fig = make_subplots(
                    rows=3, cols=1,
                    subplot_titles=(
                        "Network Efficiency (%)",
                        "Water Loss (%)",
                        "Pressure (mH₂O)"
                    ),
                    vertical_spacing=0.1
                )

                # Efficiency trend with target line
                fig.add_trace(
                    go.Scatter(
                        x=trend_data['timestamp'],
                        y=trend_data['efficiency_percentage'],
                        mode='lines+markers',
                        name='Efficiency',
                        line=dict(color='#2E8B57', width=2),
                        marker=dict(size=4)
                    ), row=1, col=1
                )
                
                # Add 95% target line
                fig.add_hline(
                    y=95, line_dash="dash", line_color="red", 
                    annotation_text="Target: 95%",
                    row=1, col=1
                )

                # Water loss trend
                fig.add_trace(
                    go.Scatter(
                        x=trend_data['timestamp'],
                        y=trend_data['loss_percentage'],
                        mode='lines+markers',
                        name='Water Loss',
                        line=dict(color='#DC143C', width=2),
                        marker=dict(size=4)
                    ), row=2, col=1
                )

                # Pressure trend
                fig.add_trace(
                    go.Scatter(
                        x=trend_data['timestamp'],
                        y=trend_data['pressure_mh2o'],
                        mode='lines+markers',
                        name='Pressure',
                        line=dict(color='#FF8C00', width=2),
                        marker=dict(size=4)
                    ), row=3, col=1
                )

                fig.update_layout(
                    height=600,
                    showlegend=False,
                    title_text="Network Efficiency Trends"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error loading trend data: {str(e)}")

    def _get_hours_from_time_range(self, time_range: str) -> int:
        """Convert time range string to hours."""
        time_to_hours = {
            "Last 6 Hours": 6,
            "Last 24 Hours": 24,
            "Last 3 Days": 72,
            "Last Week": 168,
            "Last Month": 720,
            "Last Year": 8760,
        }
        return time_to_hours.get(time_range, 24)

    def _render_component_efficiency(self) -> None:
        """Render component-wise efficiency breakdown."""
        st.subheader("Component Efficiency")
        
        try:
            # Get mock node efficiency data for now
            node_efficiency_data = self._get_node_efficiency_data()
            
            if not node_efficiency_data:
                st.warning("No component efficiency data available")
                return
            
            nodes = list(node_efficiency_data.keys())
            efficiency = list(node_efficiency_data.values())

            fig = go.Figure(
                go.Bar(
                    x=nodes,
                    y=efficiency,
                    marker_color=[
                        "green" if e >= 92 else "orange" if e >= 88 else "red"
                        for e in efficiency
                    ],
                    text=[f"{e:.1f}%" for e in efficiency],
                    textposition="outside",
                )
            )

            # Add target line
            fig.add_hline(
                y=92, line_dash="dash", line_color="gray", 
                annotation_text="Target: 92%"
            )

            fig.update_layout(
                height=350,
                xaxis_title="Network Node",
                yaxis_title="Efficiency (%)",
                yaxis_range=[80, 100],
            )

            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading component efficiency: {str(e)}")

    def _render_loss_distribution(self) -> None:
        """Render loss distribution analysis."""
        st.subheader("Loss Distribution")
        
        try:
            # Get mock loss distribution data
            loss_data = self._get_loss_distribution_data()
            
            if not loss_data:
                st.warning("No loss distribution data available")
                return
            
            fig = go.Figure(
                go.Pie(
                    labels=list(loss_data.keys()),
                    values=list(loss_data.values()),
                    hole=0.3,
                    marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
                )
            )

            fig.update_layout(
                height=350,
                title_text="Water Loss Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading loss distribution: {str(e)}")

    def _render_pressure_analysis(self, time_range: str) -> None:
        """Render network pressure analysis."""
        st.subheader("Network Pressure Analysis")
        
        try:
            # Get mock pressure data
            pressure_data = self._get_pressure_analysis_data()
            
            if not pressure_data:
                st.warning("No pressure analysis data available")
                return
            
            zones = list(pressure_data['current_pressure'].keys())
            current_pressure = list(pressure_data['current_pressure'].values())
            optimal_min = pressure_data['optimal_min']
            optimal_max = pressure_data['optimal_max']

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
                xaxis_title="Network Node",
                yaxis_title="Pressure (mH₂O)",
                yaxis_range=[0, 5],
                hovermode="x",
            )

            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading pressure analysis: {str(e)}")

    def _render_fallback_interface(self) -> None:
        """Render fallback interface when data is unavailable."""
        st.warning("⚠️ Using fallback data. Please check your connection.")
        
        # Show basic metrics with fallback values
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall Efficiency", "94.2%", "Estimated")
        with col2:
            st.metric("Water Loss Rate", "12.5 m³/h", "Estimated")
        with col3:
            st.metric("Avg Pressure", "2.8 mH₂O", "Estimated")
        with col4:
            st.metric("Reservoir Level", "78.3%", "Estimated")

    def _get_node_efficiency_data(self) -> dict:
        """Get mock node efficiency data."""
        return {
            "Primary Station": 96.2,
            "Secondary Station": 94.8,
            "Distribution A": 92.5,
            "Distribution B": 93.1,
            "Junction C": 91.3,
            "Supply Control": 94.7,
            "Pressure Station": 89.8,
            "Remote Point": 88.9,
        }

    def _get_loss_distribution_data(self) -> dict:
        """Get mock loss distribution data."""
        return {
            "Pipe Leakage": 45.2,
            "Meter Inaccuracy": 18.7,
            "Valve Losses": 12.3,
            "System Overflow": 8.9,
            "Other": 14.9,
        }

    def _get_pressure_analysis_data(self) -> dict:
        """Get mock pressure analysis data."""
        return {
            'current_pressure': {
                "Primary Station": 3.2,
                "Secondary Station": 2.9,
                "Distribution A": 2.7,
                "Distribution B": 2.8,
                "Junction C": 2.6,
                "Supply Control": 3.1,
                "Pressure Station": 3.4,
                "Remote Point": 2.5,
            },
            'optimal_min': [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            'optimal_max': [3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5],
        }

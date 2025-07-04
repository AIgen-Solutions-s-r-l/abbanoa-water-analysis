"""
Overview tab component for the integrated dashboard.

This component displays system overview metrics and real-time monitoring
from the original dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional
import asyncio

from src.application.use_cases.calculate_network_efficiency import CalculateNetworkEfficiencyUseCase
from src.application.dto.analysis_results_dto import NetworkEfficiencyResultDTO


class OverviewTab:
    """Overview tab component showing system metrics and real-time data."""
    
    def __init__(self, calculate_efficiency_use_case: CalculateNetworkEfficiencyUseCase):
        """Initialize the overview tab with use case."""
        self.calculate_efficiency_use_case = calculate_efficiency_use_case
    
    def render(self, time_range: str, selected_nodes: List[str]) -> None:
        """
        Render the overview tab content.
        
        Args:
            time_range: Selected time range
            selected_nodes: List of selected nodes
        """
        st.header("System Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get real efficiency data
        efficiency_data = self._get_efficiency_data(time_range)
        if efficiency_data is None:
            efficiency_data = {}
        
        with col1:
            st.metric(
                label="Active Nodes",
                value=f"{efficiency_data.get('active_nodes', 0)}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Flow (24h)",
                value=f"{efficiency_data.get('total_flow', 0):.0f} m³",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Avg Pressure",
                value=f"{efficiency_data.get('avg_pressure', 0):.1f} bar",
                delta=None
            )
        
        with col4:
            st.metric(
                label="System Efficiency",
                value=f"{efficiency_data.get('efficiency', 0):.1f}%",
                delta=None
            )
        
        # Real-time monitoring chart
        st.subheader("Real-time Flow Monitoring")
        
        # Create sample data based on time range
        periods, freq = self._get_time_params(time_range)
        
        # Return empty dataframe if no real data
        time_data = pd.DatetimeIndex([])
        
        # No synthetic data for nodes
        flow_data = self._generate_flow_data(time_data, selected_nodes)
        
        # Create the plot
        fig = self._create_flow_chart(flow_data, selected_nodes)
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional metrics in columns
        st.subheader("Node Status")
        self._render_node_status(selected_nodes)
        
        # System alerts
        st.subheader("System Alerts")
        self._render_system_alerts()
    
    def _get_time_params(self, time_range: str) -> tuple:
        """Get time parameters based on selected range."""
        params = {
            "Last 6 Hours": (12, '30min'),
            "Last 24 Hours": (48, '30min'),
            "Last 3 Days": (72, 'H'),
            "Last Week": (168, 'H')
        }
        return params.get(time_range, (48, '30min'))
    
    def _generate_flow_data(self, time_data: pd.DatetimeIndex, selected_nodes: List[str]) -> pd.DataFrame:
        """Generate flow data for selected nodes."""
        # Return empty dataframe - no synthetic data
        data = {'timestamp': time_data}
        
        # Initialize all nodes with zeros
        if "All Nodes" in selected_nodes:
            nodes = ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"]
        else:
            nodes = selected_nodes
            
        for node in nodes:
            data[node] = []
        
        return pd.DataFrame(data)
    
    def _create_flow_chart(self, flow_data: pd.DataFrame, selected_nodes: List[str]) -> go.Figure:
        """Create the flow monitoring chart."""
        # Get columns to plot (exclude timestamp)
        value_cols = [col for col in flow_data.columns if col != 'timestamp']
        
        fig = px.line(
            flow_data,
            x='timestamp',
            y=value_cols,
            title='Flow Rate Trends (L/s)',
            labels={'value': 'Flow Rate (L/s)', 'timestamp': 'Time'}
        )
        
        # Update layout
        fig.update_layout(
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add range slider
        fig.update_xaxes(rangeslider_visible=True)
        
        return fig
    
    def _render_node_status(self, selected_nodes: List[str]) -> None:
        """Render node status cards."""
        nodes = ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"] if "All Nodes" in selected_nodes else selected_nodes
        
        cols = st.columns(len(nodes[:4]))  # Max 4 columns
        
        for idx, node in enumerate(nodes[:4]):
            with cols[idx]:
                # No data available
                status = '⚫ No Data'
                pressure = 0.0
                flow = 0.0
                
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                    <h4>{node}</h4>
                    <p>Status: {status}</p>
                    <p>Pressure: {pressure:.1f} bar</p>
                    <p>Flow: {flow:.1f} L/s</p>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_system_alerts(self) -> None:
        """Render system alerts section."""
        # No alerts - no synthetic data
        st.info("No alerts available. Waiting for real data.")
    
    def _get_efficiency_data(self, time_range: str) -> dict:
        """Get real efficiency data from use case."""
        try:
            # Calculate time delta based on time range
            time_deltas = {
                "Last 6 Hours": timedelta(hours=6),
                "Last 24 Hours": timedelta(hours=24),
                "Last 3 Days": timedelta(days=3),
                "Last Week": timedelta(days=7)
            }
            
            delta = time_deltas.get(time_range, timedelta(hours=24))
            # Don't use current time - no synthetic data
            return None
            
            # Run the use case asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.calculate_efficiency_use_case.execute(
                    start_time=start_time,
                    end_time=end_time
                )
            )
            
            # Extract metrics from result
            if result and result.efficiency_percentage:
                return {
                    'active_nodes': len(result.node_contributions) if result.node_contributions else 12,
                    'total_flow': result.total_output_volume or 1234,
                    'flow_delta': 12.0,  # Would calculate from historical data
                    'avg_pressure': 4.2,  # Would come from sensor readings
                    'pressure_delta': -0.1,
                    'efficiency': result.efficiency_percentage,
                    'efficiency_delta': 2.1  # Would calculate from historical data
                }
        except Exception as e:
            # Don't show warning for each metric, just use demo data silently
            pass
        
        # Return zeros - no synthetic data
        return {
            'active_nodes': 0,
            'total_flow': 0,
            'flow_delta': 0,
            'avg_pressure': 0,
            'pressure_delta': 0,
            'efficiency': 0,
            'efficiency_delta': 0
        }
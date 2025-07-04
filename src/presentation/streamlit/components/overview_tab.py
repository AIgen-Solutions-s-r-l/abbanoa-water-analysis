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
from typing import List


class OverviewTab:
    """Overview tab component showing system metrics and real-time data."""
    
    def __init__(self):
        """Initialize the overview tab."""
        pass
    
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
        
        with col1:
            st.metric(
                label="Active Nodes",
                value="12",
                delta="2 new this week"
            )
        
        with col2:
            st.metric(
                label="Total Flow (24h)",
                value="1,234 m³",
                delta="12% vs yesterday"
            )
        
        with col3:
            st.metric(
                label="Avg Pressure",
                value="4.2 bar",
                delta="-0.1 bar"
            )
        
        with col4:
            st.metric(
                label="System Efficiency",
                value="92.5%",
                delta="2.1%"
            )
        
        # Real-time monitoring chart
        st.subheader("Real-time Flow Monitoring")
        
        # Create sample data based on time range
        periods, freq = self._get_time_params(time_range)
        
        time_data = pd.date_range(
            end=datetime.now(),
            periods=periods,
            freq=freq
        )
        
        # Generate flow data for nodes
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
        """Generate simulated flow data for selected nodes."""
        data = {'timestamp': time_data}
        
        # Node configurations with different patterns
        node_patterns = {
            "Sant'Anna": lambda x: 100 + 20 * np.sin(x/10) + np.random.normal(0, 2, len(x)),
            "Seneca": lambda x: 80 + 15 * np.cos(x/8) + np.random.normal(0, 1.5, len(x)),
            "Selargius Tank": lambda x: 180 + 25 * np.sin(x/12) + np.random.normal(0, 3, len(x)),
            "External Supply": lambda x: 150 + 10 * np.sin(x/15) + np.random.normal(0, 2.5, len(x))
        }
        
        x = np.arange(len(time_data))
        
        if "All Nodes" in selected_nodes:
            for node, pattern in node_patterns.items():
                data[node] = pattern(x)
        else:
            for node in selected_nodes:
                if node in node_patterns:
                    data[node] = node_patterns[node](x)
        
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
                # Generate random status
                status = np.random.choice(['🟢 Normal', '🟡 Warning', '🔴 Alert'], p=[0.7, 0.2, 0.1])
                pressure = np.random.uniform(3.8, 4.5)
                flow = np.random.uniform(70, 120)
                
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
        alerts = [
            {"time": "10:30", "type": "Warning", "node": "Seneca", "message": "Pressure drop detected"},
            {"time": "09:15", "type": "Info", "node": "Sant'Anna", "message": "Scheduled maintenance completed"},
            {"time": "08:45", "type": "Alert", "node": "External Supply", "message": "Flow rate anomaly detected"}
        ]
        
        for alert in alerts[:3]:  # Show last 3 alerts
            alert_color = {
                "Warning": "#ffc107",
                "Info": "#17a2b8",
                "Alert": "#dc3545"
            }.get(alert['type'], "#6c757d")
            
            st.markdown(f"""
            <div style="border-left: 4px solid {alert_color}; padding-left: 1rem; margin-bottom: 0.5rem;">
                <strong>{alert['time']} - {alert['node']}</strong><br>
                <span style="color: {alert_color};">[{alert['type']}]</span> {alert['message']}
            </div>
            """, unsafe_allow_html=True)
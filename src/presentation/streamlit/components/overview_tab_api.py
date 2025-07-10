"""
Overview tab component using the Processing Services API.

This component displays system overview metrics fetched from the API,
eliminating the need for direct calculations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from src.presentation.streamlit.utils.api_client import get_api_client


class OverviewTab:
    """Overview tab component using API."""
    
    def __init__(self):
        """Initialize the overview tab with API client."""
        self.api_client = get_api_client()
        
    def render(self, time_range: str, selected_nodes: List[str]) -> None:
        """
        Render the overview tab content.
        
        Args:
            time_range: Selected time range
            selected_nodes: List of selected nodes
        """
        # Check API health first
        if not self.api_client.health_check():
            st.error("⚠️ Cannot connect to processing services. Please ensure they are running.")
            st.info("Start services with: `./scripts/start_processing_services.sh`")
            return
            
        # Get dashboard summary for efficiency
        summary = self.api_client.get_dashboard_summary()
        
        if not summary:
            st.warning("No data available. The processing service may still be initializing.")
            return
            
        # Display header
        st.header("System Overview")
        
        # Map time range to API format
        time_range_map = {
            "Last 6 Hours": "6h",
            "Last 24 Hours": "24h",
            "Last 3 Days": "3d",
            "Last Week": "7d",
            "Last Month": "30d",
            "Last Year": "30d"  # API limitation
        }
        api_time_range = time_range_map.get(time_range, "24h")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get network metrics
        network_metrics = self.api_client.get_network_metrics(api_time_range)
        
        if network_metrics:
            with col1:
                st.metric(
                    "Active Nodes",
                    f"{network_metrics['active_nodes']}/{len(summary['nodes'])}",
                    f"{(network_metrics['active_nodes'] / len(summary['nodes']) * 100):.0f}%"
                )
                
            with col2:
                st.metric(
                    "Total Flow",
                    f"{network_metrics['total_flow']:.1f} L/s",
                    f"{network_metrics['total_volume']:.0f} m³"
                )
                
            with col3:
                st.metric(
                    "Avg Pressure",
                    f"{network_metrics['avg_pressure']:.2f} bar"
                )
                
            with col4:
                st.metric(
                    "Network Efficiency",
                    f"{network_metrics['efficiency_percentage']:.1f}%",
                    f"{network_metrics['anomaly_count']} anomalies"
                )
        
        # Create two columns for charts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Real-time monitoring chart
            st.subheader("Real-time Flow Monitoring")
            flow_fig = self._create_flow_chart(summary['nodes'], selected_nodes)
            st.plotly_chart(flow_fig, use_container_width=True)
            
        with col2:
            # Node status
            st.subheader("Node Status")
            self._render_node_status(summary['nodes'])
            
        # Bottom row - anomalies and predictions
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Anomalies")
            self._render_anomalies(api_time_range)
            
        with col2:
            st.subheader("System Health")
            self._render_system_health()
            
    def _create_flow_chart(self, nodes: List[Dict], selected_nodes: List[str]) -> go.Figure:
        """Create flow monitoring chart."""
        fig = go.Figure()
        
        # Filter nodes based on selection
        if selected_nodes and selected_nodes != ["All Nodes"]:
            nodes = [n for n in nodes if n['node_name'] in selected_nodes]
            
        if not nodes:
            fig.add_annotation(
                text="No data available for selected nodes",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray")
            )
        else:
            # Create simple bar chart of current flow rates
            node_names = [n['node_name'] for n in nodes]
            flow_rates = [n.get('flow_rate', 0) for n in nodes]
            
            fig.add_trace(go.Bar(
                x=node_names,
                y=flow_rates,
                text=[f"{fr:.1f} L/s" for fr in flow_rates],
                textposition='auto',
                marker_color='lightblue'
            ))
            
        fig.update_layout(
            title="Current Flow Rates by Node",
            xaxis_title="Node",
            yaxis_title="Flow Rate (L/s)",
            height=400,
            showlegend=False
        )
        
        return fig
        
    def _render_node_status(self, nodes: List[Dict]):
        """Render node status list."""
        for node in nodes[:5]:  # Show top 5 nodes
            status_color = "🟢" if node.get('anomaly_count', 0) == 0 else "🟡"
            quality = node.get('quality_score', 1.0) * 100
            
            st.markdown(
                f"{status_color} **{node['node_name']}**  \n"
                f"Flow: {node.get('flow_rate', 0):.1f} L/s | "
                f"Pressure: {node.get('pressure', 0):.1f} bar | "
                f"Quality: {quality:.0f}%"
            )
            
    def _render_anomalies(self, time_range: str):
        """Render recent anomalies."""
        hours_map = {
            "6h": 6,
            "24h": 24,
            "3d": 72,
            "7d": 168,
            "30d": 720
        }
        hours = hours_map.get(time_range, 24)
        
        anomalies = self.api_client.get_anomalies(hours=hours)
        
        if not anomalies:
            st.info("No anomalies detected in the selected time range")
        else:
            # Show top 5 anomalies
            for anomaly in anomalies[:5]:
                severity_color = {
                    "critical": "🔴",
                    "warning": "🟡",
                    "info": "🔵"
                }.get(anomaly.get('severity', 'info'), "⚪")
                
                timestamp = datetime.fromisoformat(anomaly['timestamp'].replace('Z', '+00:00'))
                time_ago = datetime.now() - timestamp
                
                st.markdown(
                    f"{severity_color} **{anomaly.get('node_name', 'Unknown')}** - "
                    f"{anomaly.get('anomaly_type', 'Unknown type')}  \n"
                    f"{self._format_time_ago(time_ago)} ago | "
                    f"Value: {anomaly.get('actual_value', 0):.1f}"
                )
                
    def _render_system_health(self):
        """Render system health information."""
        status = self.api_client.get_system_status()
        
        if status:
            # Overall status
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌"
            }.get(status['status'], "❓")
            
            st.metric("System Status", f"{status_emoji} {status['status'].title()}")
            
            # Processing service
            if status['processing_service']['last_run']:
                last_run = datetime.fromisoformat(
                    status['processing_service']['last_run'].replace('Z', '+00:00')
                )
                time_since = datetime.now() - last_run
                st.text(f"Last processing: {self._format_time_ago(time_since)} ago")
                
            # Active models
            if status['active_models']:
                st.text(f"Active ML models: {len(status['active_models'])}")
                
            # Data freshness
            if status['data_freshness']['latest_data']:
                latest = datetime.fromisoformat(
                    status['data_freshness']['latest_data'].replace('Z', '+00:00')
                )
                freshness = datetime.now() - latest
                st.text(f"Data freshness: {self._format_time_ago(freshness)} old")
                
    def _format_time_ago(self, delta: timedelta) -> str:
        """Format timedelta as human-readable string."""
        if delta.days > 0:
            return f"{delta.days} days"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minutes"
        else:
            return f"{delta.seconds} seconds"
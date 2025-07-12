"""
Overview tab component using the Processing Services API.

This component displays system overview metrics fetched from the API,
eliminating the need for direct calculations.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List
import plotly.graph_objects as go
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
            st.error(
                "⚠️ Cannot connect to processing services. Please ensure they are running."
            )
            st.info("Start services with: `./scripts/start_processing_services.sh`")
            return

        # Get dashboard summary for efficiency
        summary = self.api_client.get_dashboard_summary()

        if not summary:
            st.warning(
                "No data available. The processing service may still be initializing."
            )
            return

        # Display header
        st.header("System Overview")

        # The time_range is already in API format (e.g., "24h", "7d", "365d")
        # No mapping needed
        api_time_range = time_range

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        # Get network metrics
        network_metrics = self.api_client.get_network_metrics(api_time_range)

        if network_metrics:
            with col1:
                total_nodes = len(summary["nodes"])
                if total_nodes > 0:
                    percentage = network_metrics["active_nodes"] / total_nodes * 100
                    delta_text = f"{percentage:.0f}%"
                else:
                    delta_text = "N/A"

                st.metric(
                    "Active Nodes",
                    f"{network_metrics['active_nodes']}/{total_nodes}",
                    delta_text,
                )

            with col2:
                total_flow = network_metrics.get("total_flow", 0)
                total_volume = network_metrics.get("total_volume", 0)
                st.metric(
                    "Total Flow",
                    f"{total_flow:.1f} L/s" if total_flow is not None else "N/A",
                    f"{total_volume:.0f} m³" if total_volume is not None else "N/A",
                )

            with col3:
                avg_pressure = network_metrics.get("avg_pressure", 0)
                st.metric(
                    "Avg Pressure",
                    f"{avg_pressure:.2f} bar" if avg_pressure is not None else "N/A",
                )

            with col4:
                efficiency = network_metrics.get("efficiency_percentage", 0)
                anomaly_count = network_metrics.get("anomaly_count", 0)
                st.metric(
                    "Network Efficiency",
                    f"{efficiency:.1f}%" if efficiency is not None else "N/A",
                    (
                        f"{anomaly_count} anomalies"
                        if anomaly_count is not None
                        else "N/A"
                    ),
                )

        # Create two columns for charts
        col1, col2 = st.columns([2, 1])

        with col1:
            # Real-time monitoring chart
            st.subheader("Real-time Flow Monitoring")
            flow_fig = self._create_flow_chart(summary["nodes"], selected_nodes)
            st.plotly_chart(flow_fig, use_container_width=True)

        with col2:
            # Node status
            st.subheader("Node Status")
            self._render_node_status(summary["nodes"])

        # Bottom row - anomalies and predictions
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Recent Anomalies")
            self._render_anomalies(api_time_range)

        with col2:
            st.subheader("System Health")
            self._render_system_health()

    def _create_flow_chart(
        self, nodes: List[Dict], selected_nodes: List[str]
    ) -> go.Figure:
        """Create flow monitoring chart."""
        fig = go.Figure()

        # Filter nodes based on selection
        if selected_nodes and selected_nodes != ["All Nodes"]:
            nodes = [n for n in nodes if n["node_name"] in selected_nodes]

        if not nodes:
            fig.add_annotation(
                text="No data available for selected nodes",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray"),
            )
        else:
            # Create simple bar chart of current flow rates
            node_names = [n["node_name"] for n in nodes]
            flow_rates = [
                n.get("flow_rate", 0) if n.get("flow_rate") is not None else 0
                for n in nodes
            ]

            fig.add_trace(
                go.Bar(
                    x=node_names,
                    y=flow_rates,
                    text=[
                        f"{fr:.1f} L/s" if fr is not None else "N/A"
                        for fr in flow_rates
                    ],
                    textposition="auto",
                    marker_color="lightblue",
                )
            )

        fig.update_layout(
            title="Current Flow Rates by Node",
            xaxis_title="Node",
            yaxis_title="Flow Rate (L/s)",
            height=400,
            showlegend=False,
        )

        return fig

    def _render_node_status(self, nodes: List[Dict]):
        """Render node status list."""
        for node in nodes[:5]:  # Show top 5 nodes
            status_color = "🟢" if node.get("anomaly_count", 0) == 0 else "🟡"
            quality_score = node.get("quality_score")
            quality = (quality_score * 100) if quality_score is not None else None

            flow = node.get("flow_rate", 0)
            pressure = node.get("pressure", 0)
            flow_str = f"{flow:.1f} L/s" if flow is not None else "N/A"
            pressure_str = f"{pressure:.1f} bar" if pressure is not None else "N/A"
            quality_str = f"{quality:.0f}%" if quality is not None else "N/A"

            st.markdown(
                f"{status_color} **{node['node_name']}**  \n"
                f"Flow: {flow_str} | Pressure: {pressure_str} | Quality: {quality_str}"
            )

    def _render_anomalies(self, time_range: str):
        """Render recent anomalies."""
        hours_map = {"6h": 6, "24h": 24, "3d": 72, "7d": 168, "30d": 720}
        hours = hours_map.get(time_range, 24)

        anomalies = self.api_client.get_anomalies(hours=hours)

        if not anomalies:
            st.info("No anomalies detected in the selected time range")
        else:
            # Show top 5 anomalies
            for anomaly in anomalies[:5]:
                severity_color = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(
                    anomaly.get("severity", "info"), "⚪"
                )

                timestamp = datetime.fromisoformat(
                    anomaly["timestamp"].replace("Z", "+00:00")
                )
                time_ago = datetime.now(timezone.utc) - timestamp

                actual_value = anomaly.get("actual_value", 0)
                value_str = f"{actual_value:.1f}" if actual_value is not None else "N/A"
                st.markdown(
                    f"{severity_color} **{anomaly.get('node_name', 'Unknown')}** - "
                    f"{anomaly.get('anomaly_type', 'Unknown type')}  \n"
                    f"{self._format_time_ago(time_ago)} ago | "
                    f"Value: {value_str}"
                )

    def _render_system_health(self):
        """Render system health information."""
        status = self.api_client.get_system_status()

        if status:
            # Overall status
            status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(
                status["status"], "❓"
            )

            st.metric("System Status", f"{status_emoji} {status['status'].title()}")

            # Processing service
            if status["processing_service"]["last_run"]:
                last_run = datetime.fromisoformat(
                    status["processing_service"]["last_run"].replace("Z", "+00:00")
                )
                time_since = datetime.now(timezone.utc) - last_run
                st.text(f"Last processing: {self._format_time_ago(time_since)} ago")

            # Active models
            if status["active_models"]:
                st.text(f"Active ML models: {len(status['active_models'])}")

            # Data freshness
            if status["data_freshness"]["latest_data"]:
                latest = datetime.fromisoformat(
                    status["data_freshness"]["latest_data"].replace("Z", "+00:00")
                )
                freshness = datetime.now(timezone.utc) - latest
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

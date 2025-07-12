"""
Overview tab component using Redis cache instead of Streamlit caching.

This component displays system overview metrics and real-time monitoring
data from the Redis cache for optimal performance.
"""

from datetime import datetime
from typing import List
import plotly.graph_objects as go
import streamlit as st

from src.infrastructure.cache.cache_initializer import get_cache_manager
from src.presentation.streamlit.utils.node_mappings import (
    ALL_NODE_MAPPINGS,
    get_node_display_name,
)


class OverviewTab:
    """Overview tab component using Redis cache."""

    def __init__(self):
        """Initialize the overview tab with Redis cache manager."""
        self.cache_manager = get_cache_manager()

    def render(self, time_range: str, selected_nodes: List[str]) -> None:
        """
        Render the overview tab content.

        Args:
            time_range: Selected time range
            selected_nodes: List of selected nodes
        """
        st.header("System Overview")

        # Map time range to cache key
        time_range_map = {
            "Last 6 Hours": "6h",
            "Last 24 Hours": "24h",
            "Last 3 Days": "3d",
            "Last Week": "7d",
            "Last Month": "30d",
            "Last Year": "30d",  # Use 30d data for year view
        }
        cache_time_range = time_range_map.get(time_range, "24h")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        # Get system metrics from cache
        system_metrics = self.cache_manager.get_system_metrics(cache_time_range)

        with col1:
            st.metric(
                label="Active Nodes",
                value=f"{int(system_metrics.get('active_nodes', 0))}",
                delta=None,
            )

        with col2:
            st.metric(
                label="Total Flow",
                value=f"{system_metrics.get('total_flow', 0):.0f} L/s",
                delta=None,
            )

        with col3:
            st.metric(
                label="Avg Pressure",
                value=f"{system_metrics.get('avg_pressure', 0):.1f} bar",
                delta=None,
            )

        with col4:
            # Calculate efficiency based on active nodes
            total_nodes = int(system_metrics.get("total_nodes", 1))
            active_nodes = int(system_metrics.get("active_nodes", 0))
            efficiency = (active_nodes / total_nodes * 100) if total_nodes > 0 else 0

            st.metric(
                label="System Efficiency",
                value=f"{efficiency:.1f}%",
                delta=None,
            )

        # Real-time monitoring chart
        st.subheader("Real-time Flow Monitoring")
        flow_chart = self._create_flow_chart(selected_nodes)
        st.plotly_chart(flow_chart, use_container_width=True)

        # Node status
        st.subheader("Node Status")
        self._render_node_status(selected_nodes)

        # System alerts
        st.subheader("System Alerts")
        self._render_system_alerts()

    def _create_flow_chart(self, selected_nodes: List[str]) -> go.Figure:
        """Create flow monitoring chart from cached time series data."""
        fig = go.Figure()

        # Get node IDs from selection
        from src.presentation.streamlit.utils.node_mappings import (
            get_node_ids_from_selection,
        )

        node_ids = get_node_ids_from_selection(selected_nodes)

        if not node_ids:
            return fig

        # Get time series data for each node
        for node_id in node_ids[:10]:  # Limit to 10 nodes for performance
            time_series = self.cache_manager.get_time_series(node_id)

            if time_series and time_series.get("timestamps"):
                display_name = get_node_display_name(node_id)

                fig.add_trace(
                    go.Scatter(
                        x=time_series["timestamps"],
                        y=time_series["flow_rates"],
                        mode="lines",
                        name=display_name,
                        line=dict(width=2),
                    )
                )

        fig.update_layout(
            title="Flow Rate Trends (L/s)",
            xaxis_title="Time",
            yaxis_title="Flow Rate (L/s)",
            height=400,
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        # Add range slider
        fig.update_xaxes(rangeslider_visible=True)

        return fig

    def _render_node_status(self, selected_nodes: List[str]) -> None:
        """Render node status cards using cached data."""
        # Get all available nodes if "All Nodes" is selected
        if "All Nodes" in selected_nodes:
            nodes = list(ALL_NODE_MAPPINGS.keys())
        else:
            # Filter out category headers
            nodes = [n for n in selected_nodes if not n.startswith("---")]

        # Display up to 4 nodes
        cols = st.columns(min(len(nodes), 4))

        for idx, node_name in enumerate(nodes[:4]):
            with cols[idx]:
                # Get node ID
                node_id = ALL_NODE_MAPPINGS.get(node_name)

                if node_id and not node_id.startswith("00000000"):
                    # Get latest reading from cache
                    latest = self.cache_manager.get_latest_reading(node_id)

                    if latest:
                        flow = latest.get("flow_rate", 0)
                        pressure = latest.get("pressure", 0)

                        # Determine status based on flow
                        if flow > 0:
                            status = "🟢 Online"
                        else:
                            status = "🟡 Low Flow"
                    else:
                        status = "⚫ No Data"
                        flow = 0
                        pressure = 0
                else:
                    # Original UUID nodes
                    status = "⚫ No Data (Original Node)"
                    flow = 0
                    pressure = 0

                st.markdown(
                    f"""
                    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                        <h4>{node_name}</h4>
                        <p>Status: {status}</p>
                        <p>Pressure: {pressure:.1f} bar</p>
                        <p>Flow: {flow:.1f} L/s</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    def _render_system_alerts(self) -> None:
        """Render system alerts from cached anomalies."""
        # Get recent anomalies from cache
        anomalies = self.cache_manager.get_recent_anomalies(limit=20)

        if anomalies:
            # Group by severity
            critical_alerts = []
            warning_alerts = []
            info_alerts = []

            for anomaly in anomalies:
                # Convert to alert format
                node_name = get_node_display_name(anomaly["node_id"])
                anomaly_type = anomaly["anomaly_type"]

                alert = {
                    "node": node_name,
                    "timestamp": datetime.fromisoformat(anomaly["timestamp"]).strftime(
                        "%H:%M"
                    ),
                    "flow": anomaly.get("flow_rate", 0),
                    "pressure": anomaly.get("pressure", 0),
                }

                if anomaly_type == "low_pressure":
                    alert["title"] = "Low Pressure Alert"
                    alert["description"] = (
                        f"Pressure dropped to {alert['pressure']:.1f} bar"
                    )
                    alert["severity"] = "critical"
                    critical_alerts.append(alert)
                elif anomaly_type == "high_flow":
                    alert["title"] = "Flow Spike Detected"
                    alert["description"] = (
                        f"Flow rate spiked to {alert['flow']:.1f} L/s"
                    )
                    alert["severity"] = "warning"
                    warning_alerts.append(alert)
                elif anomaly_type == "low_flow":
                    alert["title"] = "Low Flow Detected"
                    alert["description"] = (
                        f"Flow rate dropped to {alert['flow']:.1f} L/s"
                    )
                    alert["severity"] = "info"
                    info_alerts.append(alert)
                else:
                    alert["title"] = "Anomaly Detected"
                    alert["description"] = "Unusual reading detected"
                    alert["severity"] = "info"
                    info_alerts.append(alert)

            # Display alerts
            if critical_alerts:
                st.error("🚨 Critical Alerts")
                for alert in critical_alerts[:3]:
                    st.markdown(
                        f"""
                        <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 12px; margin: 8px 0; border-radius: 4px;">
                            <strong>{alert['title']}</strong><br>
                            <small>{alert['node']} • {alert['timestamp']}</small><br>
                            {alert['description']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if warning_alerts:
                st.warning("⚠️ Warning Alerts")
                for alert in warning_alerts[:3]:
                    st.markdown(
                        f"""
                        <div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 12px; margin: 8px 0; border-radius: 4px;">
                            <strong>{alert['title']}</strong><br>
                            <small>{alert['node']} • {alert['timestamp']}</small><br>
                            {alert['description']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if info_alerts and len(critical_alerts) + len(warning_alerts) < 5:
                st.info("ℹ️ Information Alerts")
                for alert in info_alerts[:2]:
                    st.markdown(
                        f"""
                        <div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 12px; margin: 8px 0; border-radius: 4px;">
                            <strong>{alert['title']}</strong><br>
                            <small>{alert['node']} • {alert['timestamp']}</small><br>
                            {alert['description']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Summary
            total_alerts = len(anomalies)
            st.caption(
                f"Total: {total_alerts} anomalies detected • "
                f"Critical: {len(critical_alerts)} • "
                f"Warning: {len(warning_alerts)} • "
                f"Info: {len(info_alerts)}"
            )
        else:
            st.success("✅ No active alerts. All systems operating normally.")

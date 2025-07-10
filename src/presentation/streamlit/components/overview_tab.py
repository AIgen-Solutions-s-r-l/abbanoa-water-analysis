"""
Overview tab component for the integrated dashboard.

This component displays system overview metrics and real-time monitoring
from the original dashboard.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.application.dto.analysis_results_dto import NetworkEfficiencyResultDTO
from src.application.use_cases.calculate_network_efficiency import (
    CalculateNetworkEfficiencyUseCase,
)
from src.infrastructure.di_container import Container
from src.presentation.streamlit.utils.data_optimizer import DataOptimizer, show_optimization_info
from src.presentation.streamlit.utils.node_mappings import get_node_ids_from_selection


class OverviewTab:
    """Overview tab for dashboard."""

    def __init__(self, calculate_efficiency_use_case: CalculateNetworkEfficiencyUseCase):
        """Initialize the overview tab with use case."""
        self.calculate_efficiency_use_case = calculate_efficiency_use_case
        # Initialize optimizer
        container = Container()
        self.sensor_repo = container.sensor_reading_repository()
        self.optimizer = DataOptimizer(self.sensor_repo)

    def render(self, time_range: str, selected_nodes: List[str]) -> None:
        """
        Render the overview tab.

        Args:
            time_range: Selected time range
            selected_nodes: List of selected nodes
        """
        st.header("📊 System Overview")
        
        # Show optimization info for large time ranges
        if time_range in ["Last Month", "Last Year"]:
            time_delta = self._get_time_delta(time_range)
            days = time_delta.days
            estimated_records = days * 24 * 12  # Rough estimate
            
            recommendations = self.optimizer.get_performance_recommendations(days, estimated_records)
            if recommendations:
                st.warning("⚡ **Performance Optimization**\n\n" + "\n".join(recommendations))

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
                delta=None,
            )
        
        with col2:
            st.metric(
                label="Total Flow (24h)",
                value=f"{efficiency_data.get('total_flow', 0):.0f} m³",
                delta=None,
            )
        
        with col3:
            st.metric(
                label="Avg Pressure",
                value=f"{efficiency_data.get('avg_pressure', 0):.1f} bar",
                delta=None,
            )
        
        with col4:
            st.metric(
                label="System Efficiency",
                value=f"{efficiency_data.get('efficiency', 0):.1f}%",
                delta=None,
            )
        
        # Real-time monitoring chart
        st.subheader("Real-time Flow Monitoring")
        
        # Get real flow data
        flow_data = self._get_real_flow_data(selected_nodes)
        
        # Create the plot
        fig = self._create_flow_chart(flow_data, selected_nodes)
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional metrics in columns
        st.subheader("Node Status")
        self._render_node_status(selected_nodes)
        
        # System alerts
        st.subheader("System Alerts")
        self._render_system_alerts()
    
    def _get_time_delta(self, time_range: str) -> timedelta:
        """Get time delta for the given time range."""
        time_deltas = {
            "Last 6 Hours": timedelta(hours=6),
            "Last 24 Hours": timedelta(hours=24),
            "Last 3 Days": timedelta(days=3),
            "Last Week": timedelta(days=7),
            "Last Month": timedelta(days=30),
            "Last Year": timedelta(days=365),
        }
        return time_deltas.get(time_range, timedelta(hours=24))

    def _create_flow_chart(
        self, flow_data: pd.DataFrame, selected_nodes: List[str]
    ) -> go.Figure:
        """Create the flow monitoring chart."""
        fig = go.Figure()

        # Add traces for each node
        for node in selected_nodes:
            if node in flow_data.columns and node != "timestamp":
                fig.add_trace(
                    go.Scatter(
                        x=flow_data["timestamp"],
                        y=flow_data[node],
                        mode="lines+markers",
                        name=node,
                        line=dict(width=2),
                        marker=dict(size=4),
                    )
                )

        fig.update_layout(
            title="Real-time Flow Monitoring",
            xaxis_title="Time",
            yaxis_title="Flow Rate (L/min)",
            hovermode="x unified",
            height=400,
        )

        return fig
    
    def _render_node_status(self, selected_nodes: List[str]) -> None:
        """Render node status cards."""
        from src.presentation.streamlit.utils.node_mappings import ALL_NODE_MAPPINGS
        
        # Get all available nodes if "All Nodes" is selected
        if "All Nodes" in selected_nodes:
            nodes = list(ALL_NODE_MAPPINGS.keys())
        else:
            # Filter out category headers
            nodes = [n for n in selected_nodes if not n.startswith("---")]
        
        # Get latest data for each node
        node_data = self._get_latest_node_data()
        
        cols = st.columns(len(nodes[:4]))
        
        for idx, node in enumerate(nodes[:4]):
            with cols[idx]:
                # Get data for this node
                if node in node_data:
                    data = node_data[node]
                    pressure = data["pressure"]
                    flow = data["flow"]
                    
                    # Check timestamp to determine status
                    if "timestamp" in data and data["timestamp"]:
                        # If we have recent data (within last day of available data)
                        from datetime import timezone
                        latest_ts = data["timestamp"]
                        if hasattr(latest_ts, 'replace'):
                            latest_ts = latest_ts.replace(tzinfo=timezone.utc)
                        
                        # For historical data, show as online if flow > 0
                        if flow > 0:
                            status = "🟢 Online"
                        else:
                            # Check if this is just a low-flow period
                            status = "🟡 Low Flow"
                    else:
                        status = "🔴 Offline" if flow == 0 else "🟢 Online"
                else:
                    # No data for original nodes is expected
                    if node in ["Sant'Anna", "Seneca", "Selargius Tank"]:
                        status = "⚫ No Data (Original Node)"
                    else:
                        status = "⚫ No Data"
                    pressure = 0.0
                    flow = 0.0
                
                st.markdown(
                    f"""
                <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                    <h4>{node}</h4>
                    <p>Status: {status}</p>
                    <p>Pressure: {pressure:.1f} bar</p>
                    <p>Flow: {flow:.1f} L/s</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
    
    @st.cache_data
    def _render_system_alerts(_self) -> None:
        """Render system alerts section with optimization."""
        # Get real-time alerts from sensor data
        alerts = self._get_system_alerts()

        if alerts:
            # Display alerts by severity
            critical_alerts = [a for a in alerts if a["severity"] == "critical"]
            warning_alerts = [a for a in alerts if a["severity"] == "warning"]
            info_alerts = [a for a in alerts if a["severity"] == "info"]

            if critical_alerts:
                for alert in critical_alerts:
                    st.error(f"🚨 **{alert['title']}**: {alert['description']}")

            if warning_alerts:
                for alert in warning_alerts:
                    st.warning(f"⚠️ **{alert['title']}**: {alert['description']}")

            if info_alerts:
                for alert in info_alerts:
                    st.info(f"ℹ️ **{alert['title']}**: {alert['description']}")
        else:
            st.success("✅ No active alerts. All systems operating normally.")

    @st.cache_data
    def _get_system_alerts(_self) -> List[dict]:
        """Analyze real sensor data to detect system alerts with optimization."""
        alerts = []

        try:
            # Use optimized data fetching for alerts
            from uuid import UUID
            from datetime import datetime, timedelta
            
            # Check last 24 hours for alerts
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            # Primary station check
            primary_id = UUID("00000000-0000-0000-0000-000000000001")
            
            # Use optimizer for better performance
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                readings, _ = loop.run_until_complete(
                    self.optimizer.get_optimized_data(primary_id, start_time, end_time)
                )
            finally:
                loop.close()

            if readings:
                # Check for anomalies
                anomaly_count = sum(1 for r in readings if r.is_anomaly)
                if anomaly_count > len(readings) * 0.1:  # More than 10% anomalies
                    alerts.append({
                        "severity": "warning",
                        "title": "High Anomaly Rate",
                        "description": f"Detected {anomaly_count} anomalies in the last 24 hours"
                    })

                # Check flow rates
                flow_rates = [r.flow_rate.value for r in readings if r.flow_rate]
                if flow_rates:
                    avg_flow = sum(flow_rates) / len(flow_rates)
                    if avg_flow < 50:  # Below normal threshold
                        alerts.append({
                            "severity": "warning",
                            "title": "Low Flow Rate",
                            "description": f"Average flow rate ({avg_flow:.1f} L/min) below normal threshold"
                        })

        except Exception as e:
            alerts.append({
                "severity": "info",
                "title": "System Check",
                "description": f"Unable to analyze sensor data for alerts: {str(e)[:100]}..."
            })

        return alerts

    @st.cache_data
    def _get_efficiency_data(_self, time_range: str) -> Optional[pd.DataFrame]:
        """Get efficiency data with optimization."""
        try:
            time_delta = _self._get_time_delta(time_range)
            end_time = datetime.now()
            start_time = end_time - time_delta

            # Node mapping
            node_mapping = {
                "Primary Station": UUID("00000000-0000-0000-0000-000000000001"),
                "Secondary Station": UUID("00000000-0000-0000-0000-000000000002"),
                "Distribution A": UUID("00000000-0000-0000-0000-000000000003"),
                "Distribution B": UUID("00000000-0000-0000-0000-000000000004"),
            }

            all_data = []
            optimization_info = None

            for node_name, node_id in node_mapping.items():
                # Use data optimizer for large time ranges
                if time_delta.days > 7:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        readings, opt_info = loop.run_until_complete(
                            self.optimizer.get_optimized_data(node_id, start_time, end_time)
                        )
                        if not optimization_info:
                            optimization_info = opt_info
                    finally:
                        loop.close()
                else:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        readings = loop.run_until_complete(
                            self.sensor_repo.get_by_node_id(node_id, start_time, end_time)
                        )
                    finally:
                        loop.close()

                # Convert to DataFrame format
                for reading in readings:
                    flow_val = reading.flow_rate.value if reading.flow_rate else 0
                    pressure_val = reading.pressure.value if reading.pressure else 0
                    
                    all_data.append({
                        "timestamp": reading.timestamp,
                        "node_name": node_name,
                        "flow_rate": flow_val,
                        "pressure": pressure_val,
                        "efficiency": min(100, max(0, (flow_val / 100) * 100)) if flow_val > 0 else 0,
                        "is_anomaly": reading.is_anomaly
                    })

            if not all_data:
                return None

            # Show optimization info if available
            if optimization_info:
                show_optimization_info(optimization_info)

            return pd.DataFrame(all_data)

        except Exception as e:
            st.error(f"Error fetching efficiency data: {str(e)}")
            return None

    @st.cache_data
    def _get_real_flow_data(_self, selected_nodes: List[str]) -> pd.DataFrame:
        """Get real flow data with optimization."""
        # This method would be similar to _get_efficiency_data
        # but focused on flow data for the selected nodes
        return self._get_efficiency_data("Last 24 Hours")  # Default to 24 hours for real-time view

    @st.cache_data
    def _get_latest_node_data(_self) -> Dict[str, Any]:
        """Get latest node data with optimization."""
        try:
            # Get latest data from primary station
            primary_id = UUID("00000000-0000-0000-0000-000000000001")
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)  # Last hour
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                readings = loop.run_until_complete(
                    self.sensor_repo.get_by_node_id(primary_id, start_time, end_time)
                )
            finally:
                loop.close()

            if readings:
                latest = readings[-1]  # Get most recent reading
                return {
                    "flow_rate": latest.flow_rate.value if latest.flow_rate else 0,
                    "pressure": latest.pressure.value if latest.pressure else 0,
                    "temperature": latest.temperature.value if latest.temperature else 0,
                    "quality_score": latest.quality_score or 0,
                    "timestamp": latest.timestamp
                }
            else:
                return {"flow_rate": 0, "pressure": 0, "temperature": 0, "quality_score": 0}

        except Exception as e:
            st.error(f"Error fetching latest node data: {str(e)}")
            return {"flow_rate": 0, "pressure": 0, "temperature": 0, "quality_score": 0}

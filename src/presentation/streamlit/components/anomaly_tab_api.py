"""
Anomaly detection tab using the Processing Services API.

This component displays anomalies detected by the ML models.
"""

from datetime import datetime
from typing import List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.presentation.streamlit.utils.api_client import get_api_client


class AnomalyTab:
    """Anomaly detection tab using API."""

    def __init__(self):
        """Initialize with API client."""
        self.api_client = get_api_client()

    def render(self, time_range: str, selected_nodes: List[str]) -> None:
        """Render the anomaly detection tab."""
        st.header("Anomaly Detection")

        # Convert time range to hours
        hours_map = {
            "Last 6 Hours": 6,
            "Last 24 Hours": 24,
            "Last 3 Days": 72,
            "Last Week": 168,
            "Last Month": 720,
        }
        hours = hours_map.get(time_range, 24)

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            severity_filter = st.selectbox(
                "Severity", ["All", "critical", "warning", "info"], index=0
            )

        with col2:
            # Filter by selected nodes
            node_filter = None
            if selected_nodes and selected_nodes != ["All Nodes"]:
                node_filter = st.selectbox("Node", ["All"] + selected_nodes, index=0)

        # Get anomalies
        anomalies = self.api_client.get_anomalies(
            hours=hours,
            severity=severity_filter if severity_filter != "All" else None,
            node_id=node_filter if node_filter and node_filter != "All" else None,
        )

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        total_anomalies = len(anomalies)
        critical_count = sum(1 for a in anomalies if a.get("severity") == "critical")
        warning_count = sum(1 for a in anomalies if a.get("severity") == "warning")
        info_count = sum(1 for a in anomalies if a.get("severity") == "info")

        with col1:
            st.metric("Total Anomalies", total_anomalies)

        with col2:
            st.metric("Critical", critical_count, delta_color="inverse")

        with col3:
            st.metric("Warnings", warning_count, delta_color="inverse")

        with col4:
            st.metric("Info", info_count)

        # Anomaly timeline
        if anomalies:
            st.subheader("Anomaly Timeline")
            fig_timeline = self._create_timeline_chart(anomalies)
            st.plotly_chart(fig_timeline, use_container_width=True)

            # Anomaly distribution
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("By Type")
                fig_type = self._create_type_distribution(anomalies)
                st.plotly_chart(fig_type, use_container_width=True)

            with col2:
                st.subheader("By Node")
                fig_node = self._create_node_distribution(anomalies)
                st.plotly_chart(fig_node, use_container_width=True)

            # Detailed anomaly list
            st.subheader("Anomaly Details")
            self._render_anomaly_list(anomalies)

        else:
            st.success("✅ No anomalies detected in the selected time range")

            # Show system health
            st.subheader("System Health Summary")

            # Get data quality for nodes
            if selected_nodes and selected_nodes != ["All Nodes"]:
                for node in selected_nodes[:5]:  # Show top 5
                    quality = self.api_client.get_data_quality(node)
                    if quality:
                        quality_score = quality.get("overall_quality_score", 1.0) * 100
                        st.progress(quality_score / 100)
                        st.text(f"{node}: {quality_score:.1f}% data quality")

    def _create_timeline_chart(self, anomalies: List[dict]) -> go.Figure:
        """Create anomaly timeline chart."""
        # Convert to DataFrame
        df = pd.DataFrame(anomalies)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Count by hour
        df["hour"] = df["timestamp"].dt.floor("H")
        hourly_counts = (
            df.groupby(["hour", "severity"]).size().reset_index(name="count")
        )

        fig = go.Figure()

        for severity in ["critical", "warning", "info"]:
            severity_data = hourly_counts[hourly_counts["severity"] == severity]

            color_map = {"critical": "red", "warning": "orange", "info": "blue"}

            fig.add_trace(
                go.Bar(
                    x=severity_data["hour"],
                    y=severity_data["count"],
                    name=severity.capitalize(),
                    marker_color=color_map[severity],
                )
            )

        fig.update_layout(
            title="Anomalies Over Time",
            xaxis_title="Time",
            yaxis_title="Count",
            barmode="stack",
            height=400,
        )

        return fig

    def _create_type_distribution(self, anomalies: List[dict]) -> go.Figure:
        """Create anomaly type distribution chart."""
        type_counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.get("anomaly_type", "Unknown")
            type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=0.3,
                )
            ]
        )

        fig.update_layout(height=300, showlegend=True)

        return fig

    def _create_node_distribution(self, anomalies: List[dict]) -> go.Figure:
        """Create anomaly distribution by node."""
        node_counts = {}
        for anomaly in anomalies:
            node = anomaly.get("node_name", "Unknown")
            node_counts[node] = node_counts.get(node, 0) + 1

        # Sort by count and take top 10
        sorted_nodes = sorted(node_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=[n[0] for n in sorted_nodes],
                    y=[n[1] for n in sorted_nodes],
                    marker_color="lightcoral",
                )
            ]
        )

        fig.update_layout(xaxis_title="Node", yaxis_title="Anomaly Count", height=300)

        return fig

    def _render_anomaly_list(self, anomalies: List[dict]):
        """Render detailed anomaly list."""
        # Convert to DataFrame for easier display
        df = pd.DataFrame(anomalies)

        # Format timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")

        # Select columns to display
        display_columns = [
            "timestamp",
            "node_name",
            "anomaly_type",
            "severity",
            "measurement_type",
            "actual_value",
            "expected_value",
        ]

        # Filter columns that exist
        display_columns = [col for col in display_columns if col in df.columns]

        # Apply severity coloring
        def severity_color(severity):
            colors = {
                "critical": "background-color: #ffcccc",
                "warning": "background-color: #fff3cd",
                "info": "background-color: #cce5ff",
            }
            return colors.get(severity, "")

        # Display with styling
        if "severity" in df.columns:
            styled_df = df[display_columns].style.applymap(
                lambda x: (
                    severity_color(x)
                    if df.columns[df.columns.get_loc("severity")] == "severity"
                    else ""
                ),
                subset=["severity"],
            )
        else:
            styled_df = df[display_columns]

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Anomaly Report",
            data=csv,
            file_name=f"anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

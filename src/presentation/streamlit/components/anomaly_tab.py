"""
Anomaly detection tab component for the integrated dashboard.

This component displays network anomalies and alerts from the monitoring system.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class AnomalyTab:
    """Anomaly detection tab component."""
    
    def __init__(self):
        """Initialize the anomaly tab."""
        pass
    
    def render(self, time_range: str) -> None:
        """
        Render the anomaly detection tab.
        
        Args:
            time_range: Selected time range
        """
        st.header("🔍 Anomaly Detection")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Anomalies Detected",
                value="7",
                delta="3 new today",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                label="Critical Alerts",
                value="2",
                delta="1 resolved"
            )
        
        with col3:
            st.metric(
                label="Nodes Affected",
                value="3/12",
                delta="25%"
            )
        
        with col4:
            st.metric(
                label="Avg Resolution Time",
                value="45 min",
                delta="-15 min"
            )
        
        # Anomaly timeline
        st.subheader("Anomaly Timeline")
        self._render_anomaly_timeline(time_range)
        
        # Anomaly distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Anomaly Types Distribution")
            self._render_anomaly_types_chart()
        
        with col2:
            st.subheader("Affected Nodes")
            self._render_affected_nodes_chart()
        
        # Detailed anomaly list
        st.subheader("Recent Anomalies")
        self._render_anomaly_list()
        
        # Anomaly patterns
        st.subheader("Anomaly Patterns Analysis")
        self._render_anomaly_patterns()
    
    def _render_anomaly_timeline(self, time_range: str) -> None:
        """Render anomaly timeline visualization."""
        # Generate sample anomaly data
        periods, freq = self._get_time_params(time_range)
        time_data = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
        
        # Create anomaly events
        anomalies = []
        for i in range(len(time_data)):
            if np.random.random() < 0.1:  # 10% chance of anomaly
                anomaly_type = np.random.choice(['Pressure Drop', 'Flow Spike', 'Sensor Error', 'Leak Detection'])
                severity = np.random.choice(['Low', 'Medium', 'High'], p=[0.5, 0.35, 0.15])
                anomalies.append({
                    'timestamp': time_data[i],
                    'type': anomaly_type,
                    'severity': severity,
                    'value': np.random.uniform(1, 10)
                })
        
        if anomalies:
            df = pd.DataFrame(anomalies)
            
            # Create scatter plot
            fig = px.scatter(
                df,
                x='timestamp',
                y='type',
                size='value',
                color='severity',
                color_discrete_map={'Low': '#ffc107', 'Medium': '#ff7f0e', 'High': '#dc3545'},
                title='Anomaly Events Timeline'
            )
            
            fig.update_layout(
                height=300,
                showlegend=True,
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No anomalies detected in the selected time range")
    
    def _render_anomaly_types_chart(self) -> None:
        """Render pie chart of anomaly types."""
        data = pd.DataFrame({
            'Type': ['Pressure Drop', 'Flow Spike', 'Sensor Error', 'Leak Detection', 'Other'],
            'Count': [23, 18, 12, 8, 5]
        })
        
        fig = px.pie(
            data,
            values='Count',
            names='Type',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=350)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_affected_nodes_chart(self) -> None:
        """Render bar chart of affected nodes."""
        data = pd.DataFrame({
            'Node': ['Sant\'Anna', 'Seneca', 'Selargius Tank', 'External Supply'],
            'Anomalies': [8, 5, 3, 2]
        })
        
        fig = px.bar(
            data,
            x='Anomalies',
            y='Node',
            orientation='h',
            color='Anomalies',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_anomaly_list(self) -> None:
        """Render detailed list of recent anomalies."""
        anomalies = [
            {
                'Time': '10:30:45',
                'Node': 'Seneca',
                'Type': 'Pressure Drop',
                'Severity': '🔴 High',
                'Status': '⚠️ Active',
                'Description': 'Pressure dropped below 3.5 bar threshold'
            },
            {
                'Time': '09:15:22',
                'Node': 'Sant\'Anna',
                'Type': 'Flow Spike',
                'Severity': '🟡 Medium',
                'Status': '✅ Resolved',
                'Description': 'Unusual flow increase detected (>20%)'
            },
            {
                'Time': '08:45:10',
                'Node': 'External Supply',
                'Type': 'Sensor Error',
                'Severity': '🟡 Medium',
                'Status': '🔄 Under Investigation',
                'Description': 'Inconsistent readings from pressure sensor'
            }
        ]
        
        df = pd.DataFrame(anomalies)
        
        # Display as a formatted table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Time': st.column_config.TextColumn('Time', width='small'),
                'Node': st.column_config.TextColumn('Node', width='medium'),
                'Type': st.column_config.TextColumn('Type', width='medium'),
                'Severity': st.column_config.TextColumn('Severity', width='small'),
                'Status': st.column_config.TextColumn('Status', width='medium'),
                'Description': st.column_config.TextColumn('Description', width='large')
            }
        )
    
    def _render_anomaly_patterns(self) -> None:
        """Render anomaly patterns analysis."""
        # Create subplot figure
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Hourly Pattern', 'Daily Pattern')
        )
        
        # Hourly pattern
        hours = list(range(24))
        hourly_counts = [np.random.poisson(3) if 8 <= h <= 18 else np.random.poisson(1) for h in hours]
        
        fig.add_trace(
            go.Bar(x=hours, y=hourly_counts, name='Hourly', marker_color='#1f77b4'),
            row=1, col=1
        )
        
        # Daily pattern
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        daily_counts = [np.random.poisson(5) for _ in days]
        
        fig.add_trace(
            go.Bar(x=days, y=daily_counts, name='Daily', marker_color='#ff7f0e'),
            row=1, col=2
        )
        
        fig.update_layout(
            height=300,
            showlegend=False,
            title_text="Anomaly Occurrence Patterns"
        )
        
        fig.update_xaxes(title_text="Hour of Day", row=1, col=1)
        fig.update_xaxes(title_text="Day of Week", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_time_params(self, time_range: str) -> tuple:
        """Get time parameters based on selected range."""
        params = {
            "Last 6 Hours": (12, '30min'),
            "Last 24 Hours": (48, '30min'),
            "Last 3 Days": (72, 'H'),
            "Last Week": (168, 'H')
        }
        return params.get(time_range, (48, '30min'))
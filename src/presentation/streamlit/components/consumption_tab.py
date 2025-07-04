"""
Consumption patterns tab component for the integrated dashboard.

This component analyzes and displays water consumption patterns across the network.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List


class ConsumptionTab:
    """Consumption patterns analysis tab."""
    
    def __init__(self):
        """Initialize the consumption tab."""
        pass
    
    def render(self, time_range: str, selected_nodes: List[str]) -> None:
        """
        Render the consumption patterns tab.
        
        Args:
            time_range: Selected time range
            selected_nodes: List of selected nodes
        """
        st.header("📈 Consumption Patterns Analysis")
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Consumption",
                value="12,456 m³",
                delta="+8.2% vs last period"
            )
        
        with col2:
            st.metric(
                label="Peak Hour",
                value="08:00",
                delta="Same as usual"
            )
        
        with col3:
            st.metric(
                label="Min Hour",
                value="03:00",
                delta="1 hour earlier"
            )
        
        with col4:
            st.metric(
                label="Avg Daily",
                value="1,780 m³",
                delta="+5.3%"
            )
        
        # Consumption trends
        st.subheader("Consumption Trends")
        self._render_consumption_trends(time_range, selected_nodes)
        
        # Pattern analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Daily Pattern")
            self._render_daily_pattern()
        
        with col2:
            st.subheader("Weekly Pattern")
            self._render_weekly_pattern()
        
        # Peak analysis
        st.subheader("Peak Consumption Analysis")
        self._render_peak_analysis(selected_nodes)
        
        # Consumption heatmap
        st.subheader("Consumption Heatmap")
        self._render_consumption_heatmap()
        
        # Efficiency metrics
        st.subheader("Consumption Efficiency")
        self._render_efficiency_metrics()
    
    def _render_consumption_trends(self, time_range: str, selected_nodes: List[str]) -> None:
        """Render consumption trends chart."""
        # Generate time series data
        periods, freq = self._get_time_params(time_range)
        time_data = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
        
        # Generate consumption data
        data = {'timestamp': time_data}
        
        nodes = ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"] if "All Nodes" in selected_nodes else selected_nodes
        
        for node in nodes:
            # Create realistic consumption pattern
            base = np.random.uniform(80, 120)
            daily_pattern = np.array([self._get_hourly_factor(t.hour) for t in time_data])
            trend = np.linspace(0, 10, len(time_data))
            noise = np.random.normal(0, 5, len(time_data))
            
            data[node] = base * daily_pattern + trend + noise
        
        df = pd.DataFrame(data)
        
        # Create line chart
        fig = px.line(
            df,
            x='timestamp',
            y=[col for col in df.columns if col != 'timestamp'],
            title='Water Consumption Trends',
            labels={'value': 'Consumption (m³/h)', 'timestamp': 'Time'}
        )
        
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
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_daily_pattern(self) -> None:
        """Render average daily consumption pattern."""
        hours = list(range(24))
        consumption = [self._get_hourly_factor(h) * 100 for h in hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours,
            y=consumption,
            mode='lines+markers',
            name='Average',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))
        
        # Add peak hours annotation
        peak_hour = consumption.index(max(consumption))
        fig.add_annotation(
            x=peak_hour,
            y=max(consumption),
            text=f"Peak: {peak_hour}:00",
            showarrow=True,
            arrowhead=2
        )
        
        fig.update_layout(
            height=350,
            xaxis_title="Hour of Day",
            yaxis_title="Consumption (m³/h)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_weekly_pattern(self) -> None:
        """Render weekly consumption pattern."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        consumption = [100, 98, 102, 105, 103, 85, 75]  # Typical weekly pattern
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=days,
            y=consumption,
            marker_color=['#1f77b4' if c >= 100 else '#ff7f0e' for c in consumption],
            text=[f'{c}%' for c in consumption],
            textposition='outside'
        ))
        
        fig.update_layout(
            height=350,
            xaxis_title="Day of Week",
            yaxis_title="Relative Consumption (%)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_peak_analysis(self, selected_nodes: List[str]) -> None:
        """Render peak consumption analysis."""
        nodes = ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"] if "All Nodes" in selected_nodes else selected_nodes
        
        # Create peak data
        peak_data = []
        for node in nodes[:4]:  # Limit to 4 nodes
            morning_peak = np.random.uniform(110, 130)
            evening_peak = np.random.uniform(100, 120)
            night_min = np.random.uniform(40, 60)
            
            peak_data.append({
                'Node': node,
                'Morning Peak (6-9)': morning_peak,
                'Evening Peak (18-21)': evening_peak,
                'Night Minimum (2-5)': night_min
            })
        
        df = pd.DataFrame(peak_data)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        for col in ['Morning Peak (6-9)', 'Evening Peak (18-21)', 'Night Minimum (2-5)']:
            fig.add_trace(go.Bar(
                name=col,
                x=df['Node'],
                y=df[col],
                text=[f'{v:.0f}' for v in df[col]],
                textposition='outside'
            ))
        
        fig.update_layout(
            height=350,
            barmode='group',
            xaxis_title="Node",
            yaxis_title="Consumption (m³/h)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_consumption_heatmap(self) -> None:
        """Render consumption heatmap by hour and day."""
        # Generate heatmap data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = list(range(24))
        
        # Create realistic consumption patterns
        z_data = []
        for day_idx, day in enumerate(days):
            day_data = []
            for hour in hours:
                # Lower consumption on weekends
                weekend_factor = 0.7 if day_idx >= 5 else 1.0
                # Hourly pattern
                hour_factor = self._get_hourly_factor(hour)
                # Add some randomness
                value = 100 * weekend_factor * hour_factor + np.random.uniform(-10, 10)
                day_data.append(value)
            z_data.append(day_data)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=hours,
            y=days,
            colorscale='Blues',
            text=[[f'{val:.0f}' for val in row] for row in z_data],
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            height=300,
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            title="Water Consumption Heatmap (m³/h)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_efficiency_metrics(self) -> None:
        """Render consumption efficiency metrics."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Non-revenue water
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=8.5,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Non-Revenue Water (%)"},
                delta={'reference': 10, 'decreasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 20]},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 5], 'color': "lightgreen"},
                        {'range': [5, 10], 'color': "yellow"},
                        {'range': [10, 20], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 15
                    }
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Per capita consumption
            fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=142,
                number={'suffix': " L/day"},
                title={'text': "Per Capita Consumption"},
                delta={'reference': 150, 'decreasing': {'color': "green"}}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # System efficiency
            fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=91.5,
                number={'suffix': "%"},
                title={'text': "Distribution Efficiency"},
                delta={'reference': 90, 'increasing': {'color': "green"}}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
    
    def _get_hourly_factor(self, hour: int) -> float:
        """Get consumption factor for given hour."""
        # Typical residential consumption pattern
        if 6 <= hour <= 9:  # Morning peak
            return 1.2 + 0.1 * (hour - 6)
        elif 18 <= hour <= 21:  # Evening peak
            return 1.1 + 0.05 * (hour - 18)
        elif 0 <= hour <= 5:  # Night minimum
            return 0.5 + 0.05 * hour
        else:  # Daytime normal
            return 1.0
    
    def _get_time_params(self, time_range: str) -> tuple:
        """Get time parameters based on selected range."""
        params = {
            "Last 6 Hours": (12, '30min'),
            "Last 24 Hours": (48, '30min'),
            "Last 3 Days": (72, 'H'),
            "Last Week": (168, 'H')
        }
        return params.get(time_range, (48, '30min'))
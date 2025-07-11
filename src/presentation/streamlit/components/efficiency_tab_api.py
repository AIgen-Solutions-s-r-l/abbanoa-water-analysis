"""
Efficiency tab component using the Processing Services API.

This component displays network efficiency metrics from pre-computed data.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.presentation.streamlit.utils.api_client import get_api_client


class EfficiencyTab:
    """Efficiency tab using API data."""
    
    def __init__(self):
        """Initialize with API client."""
        self.api_client = get_api_client()
        
    def render(self, time_range: str) -> None:
        """Render the efficiency tab."""
        st.header("Network Efficiency Analysis")
        
        # The time_range is already in API format (e.g., "24h", "7d", "365d")
        # No mapping needed
        api_time_range = time_range
        
        # Get network metrics
        metrics = self.api_client.get_network_metrics(api_time_range)
        efficiency_data = self.api_client.get_network_efficiency()
        
        if not metrics:
            st.warning("No efficiency data available")
            return
            
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            efficiency = efficiency_data.get('efficiency_percentage', 95.0) if efficiency_data else 95.0
            st.metric(
                "Network Efficiency",
                f"{efficiency:.1f}%",
                f"{100 - efficiency:.1f}% loss"
            )
            
        with col2:
            total_input = efficiency_data.get('total_input_volume', 0) if efficiency_data else 0
            st.metric(
                "Total Input",
                f"{total_input:,.0f} m³",
                "Input volume"
            )
            
        with col3:
            total_output = efficiency_data.get('total_output_volume', 0) if efficiency_data else 0
            st.metric(
                "Total Output", 
                f"{total_output:,.0f} m³",
                "Output volume"
            )
            
        with col4:
            loss = total_input - total_output
            loss_percent = (loss / total_input * 100) if total_input > 0 else 0
            st.metric(
                "Water Loss",
                f"{loss:,.0f} m³",
                f"{loss_percent:.1f}% of input"
            )
            
        # Create efficiency trend chart
        st.subheader("Efficiency Trend")
        
        # For now, create a simple visualization
        # In production, this would fetch historical efficiency data
        fig = go.Figure()
        
        # Sample data - replace with actual historical data
        hours = list(range(24))
        efficiency_values = [95 + (i % 3) - 1 for i in hours]
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=efficiency_values,
            mode='lines+markers',
            name='Efficiency %',
            line=dict(color='green', width=2)
        ))
        
        # Add target line
        fig.add_hline(
            y=95, 
            line_dash="dash", 
            line_color="red",
            annotation_text="Target: 95%"
        )
        
        fig.update_layout(
            title="24-Hour Efficiency Trend",
            xaxis_title="Hours Ago",
            yaxis_title="Efficiency %",
            yaxis_range=[90, 100],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Zone efficiency breakdown
        if efficiency_data and 'zone_metrics' in efficiency_data:
            st.subheader("Zone Efficiency Breakdown")
            
            zone_data = efficiency_data['zone_metrics']
            if zone_data:
                # Create zone efficiency chart
                zones = list(zone_data.keys())
                efficiencies = [z.get('efficiency', 0) for z in zone_data.values()]
                
                fig_zones = go.Figure(data=[
                    go.Bar(
                        x=zones,
                        y=efficiencies,
                        text=[f"{e:.1f}%" for e in efficiencies],
                        textposition='auto',
                        marker_color=['green' if e >= 95 else 'orange' for e in efficiencies]
                    )
                ])
                
                fig_zones.update_layout(
                    title="Efficiency by Zone",
                    xaxis_title="Zone",
                    yaxis_title="Efficiency %",
                    height=400
                )
                
                st.plotly_chart(fig_zones, use_container_width=True)
        
        # Recommendations
        st.subheader("Efficiency Recommendations")
        
        if efficiency < 95:
            st.warning("⚠️ Network efficiency is below target")
            
            # Check for high loss areas
            if efficiency_data and efficiency_data.get('total_anomalies', 0) > 0:
                st.info(
                    f"🔍 {efficiency_data['total_anomalies']} anomalies detected. "
                    "Review anomaly tab for details."
                )
                
            st.info(
                "💡 Consider:\n"
                "- Checking for leaks in low-efficiency zones\n"
                "- Reviewing pressure settings\n"
                "- Inspecting nodes with high anomaly counts"
            )
        else:
            st.success("✅ Network efficiency is meeting target")
            
        # Additional insights
        with st.expander("Detailed Metrics"):
            if efficiency_data:
                st.json(efficiency_data)
            else:
                st.info("No detailed metrics available")
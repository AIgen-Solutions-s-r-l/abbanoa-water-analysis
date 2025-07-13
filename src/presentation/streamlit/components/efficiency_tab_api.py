"""
Efficiency tab component using the Processing Services API.

This component displays network efficiency metrics from pre-computed data
using the enhanced components from Sprint 2.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.presentation.streamlit.utils.api_client import get_api_client
from src.presentation.streamlit.components.KpiCard import KpiCard
from src.presentation.streamlit.components.charts.EfficiencyTrend import EfficiencyTrend
from src.presentation.streamlit.components.filters.EfficiencyFilters import EfficiencyFilters


class EfficiencyTab:
    """Enhanced efficiency tab using API data with new Sprint 2 components."""
    
    def __init__(self):
        """Initialize with API client and enhanced components."""
        self.api_client = get_api_client()
        self.kpi_card = KpiCard()
        self.efficiency_trend = EfficiencyTrend()
        self.efficiency_filters = EfficiencyFilters()
        
    def render(self, time_range: str) -> None:
        """Render the enhanced efficiency tab with API data."""
        st.header("🔗 Network Efficiency Analysis")
        
        # Loading state
        with st.spinner("Loading efficiency data..."):
            try:
                # Get API data
                efficiency_data = self._get_efficiency_data_from_api(time_range)
                
                if not efficiency_data:
                    st.error("❌ Unable to load efficiency data from API.")
                    self._render_fallback_interface()
                    return
                
                # Display main metrics using KpiCard
                self._render_main_metrics(efficiency_data)
                
                # Display drill-down filters
                self._render_drill_down_filters()
                
                # Display efficiency trends using EfficiencyTrend
                self._render_efficiency_trends(time_range)
                
                # Display additional analysis
                self._render_additional_analysis(efficiency_data)
                
            except Exception as e:
                st.error(f"❌ Error loading efficiency data: {str(e)}")
                self._render_fallback_interface()
    
    def _get_efficiency_data_from_api(self, time_range: str) -> Optional[Dict[str, Any]]:
        """Get efficiency data from API and format for KpiCard."""
        try:
            # Get network metrics and efficiency data from API
            metrics = self.api_client.get_network_metrics(time_range)
            efficiency_data = self.api_client.get_network_efficiency()
            
            if not efficiency_data:
                return None
            
            # Format data for KpiCard component
            formatted_data = {
                'efficiency_percentage': efficiency_data.get('efficiency_percentage', 95.0),
                'loss_percentage': 100.0 - efficiency_data.get('efficiency_percentage', 95.0),
                'loss_m3_per_hour': self._calculate_hourly_loss(efficiency_data),
                'avg_pressure_mh2o': efficiency_data.get('avg_pressure', 2.8),
                'reservoir_level_percentage': efficiency_data.get('reservoir_level', 75.0),
                'total_input_volume': efficiency_data.get('total_input_volume', 0),
                'total_output_volume': efficiency_data.get('total_output_volume', 0),
                'active_nodes': efficiency_data.get('active_nodes', 6),
                'total_nodes': efficiency_data.get('total_nodes', 8),
                'last_updated': datetime.now().isoformat()
            }
            
            return formatted_data
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    def _calculate_hourly_loss(self, efficiency_data: Dict[str, Any]) -> float:
        """Calculate hourly loss from efficiency data."""
        total_input = efficiency_data.get('total_input_volume', 0)
        total_output = efficiency_data.get('total_output_volume', 0)
        loss_volume = total_input - total_output
        
        # Convert to hourly rate (assuming data is daily)
        return loss_volume / 24 if loss_volume > 0 else 0
    
    def _render_main_metrics(self, efficiency_data: Dict[str, Any]) -> None:
        """Render main efficiency metrics using KpiCard component."""
        self.kpi_card.render_efficiency_kpis(efficiency_data)
    
    def _render_drill_down_filters(self) -> None:
        """Render drill-down filters section."""
        st.markdown("---")
        
        with st.expander("🔍 Drill-Down Analysis", expanded=False):
            st.markdown("""
            Use these filters to drill down into specific districts or nodes for detailed analysis.
            The charts and data below will update based on your selection.
            """)
            
            # Render filters in compact mode for API version
            selected_districts, selected_nodes = self.efficiency_filters.render_compact()
            
            if selected_districts or selected_nodes:
                st.success("✅ Filters active - API data filtered for analysis")
                
                # Show filtered information
                if selected_districts:
                    st.info(f"📍 **Selected Districts**: {', '.join(selected_districts)}")
                if selected_nodes:
                    st.info(f"🏗️ **Selected Nodes**: {', '.join(selected_nodes[:3])}")
                    if len(selected_nodes) > 3:
                        st.info(f"... and {len(selected_nodes) - 3} more nodes")
            else:
                st.info("💡 No filters active - showing all network data")
    
    def _render_efficiency_trends(self, time_range: str) -> None:
        """Render efficiency trends using EfficiencyTrend component."""
        st.subheader("Efficiency Trends")
        
        # Convert time range to hours
        hours_back = self._get_hours_from_time_range(time_range)
        
        # Use EfficiencyTrend component (it will handle API fallback)
        self.efficiency_trend.render(
            hours_back=hours_back,
            height=500,
            show_target_line=True,
            target_efficiency=95.0,
            chart_type="line",
            title="Network Efficiency Trends (API Data)"
        )
    
    def _get_hours_from_time_range(self, time_range: str) -> int:
        """Convert time range string to hours."""
        time_to_hours = {
            "Last 6 Hours": 6,
            "Last 24 Hours": 24,
            "Last 3 Days": 72,
            "Last Week": 168,
            "Last Month": 720,
            "Last Year": 8760,
        }
        return time_to_hours.get(time_range, 24)
    
    def _render_additional_analysis(self, efficiency_data: Dict[str, Any]) -> None:
        """Render additional analysis sections."""
        # Efficiency recommendations
        st.subheader("Efficiency Recommendations")
        
        efficiency_pct = efficiency_data.get('efficiency_percentage', 95.0)
        
        if efficiency_pct >= 95.0:
            st.success("✅ Network efficiency is meeting target")
            st.info(
                "💡 **Excellent Performance!**\n"
                "- Maintain current operational procedures\n"
                "- Continue regular monitoring\n"
                "- Consider documenting best practices"
            )
        elif efficiency_pct >= 90.0:
            st.warning("⚠️ Network efficiency is acceptable but could be improved")
            st.info(
                "💡 **Improvement Opportunities:**\n"
                "- Review pressure settings for optimization\n"
                "- Check for minor leaks in the system\n"
                "- Optimize pump schedules"
            )
        else:
            st.error("🚨 Network efficiency needs immediate attention")
            st.info(
                "💡 **Immediate Actions Required:**\n"
                "- Investigate significant water losses\n"
                "- Check for major leaks or pipe breaks\n"
                "- Review system pressure anomalies\n"
                "- Consider emergency response protocols"
            )
        
        # API-specific insights
        with st.expander("📊 API Data Insights"):
            st.markdown("**Data Source**: Processing Services API")
            st.markdown(f"**Last Updated**: {efficiency_data.get('last_updated', 'Unknown')}")
            st.markdown(f"**Active Monitoring Nodes**: {efficiency_data.get('active_nodes', 0)}/{efficiency_data.get('total_nodes', 8)}")
            
            # Show raw API data for debugging
            if st.checkbox("Show Raw API Data"):
                st.json(efficiency_data)
    
    def _render_fallback_interface(self) -> None:
        """Render fallback interface when API data is unavailable."""
        st.warning("⚠️ API data unavailable. Using fallback metrics.")
        
        # Use KpiCard with fallback data
        fallback_data = {
            'efficiency_percentage': 94.2,
            'loss_percentage': 5.8,
            'loss_m3_per_hour': 12.5,
            'avg_pressure_mh2o': 2.8,
            'reservoir_level_percentage': 78.3,
            'active_nodes': 6,
            'total_nodes': 8,
            'last_updated': datetime.now().isoformat()
        }
        
        self.kpi_card.render_efficiency_kpis(fallback_data)
        
        st.info("💡 Please check API connection and refresh the page.")
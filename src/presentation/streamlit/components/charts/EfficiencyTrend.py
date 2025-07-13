"""
EfficiencyTrend chart component for displaying network efficiency trends.

This component creates a reusable Plotly chart that shows efficiency trends
with a 95% target line and detailed tooltips for m³ and % values.
"""

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.presentation.streamlit.utils.data_fetcher import DataFetcher


class EfficiencyTrend:
    """
    Reusable efficiency trend chart component.
    
    Features:
    - Line/area chart with efficiency percentages
    - 95% target line indicator
    - Rich tooltips with m³ and % values
    - Responsive design
    - Customizable time ranges
    """
    
    def __init__(self, data_fetcher: Optional[DataFetcher] = None):
        """
        Initialize the EfficiencyTrend component.
        
        Args:
            data_fetcher: Optional DataFetcher instance. If None, creates a new one.
        """
        self.data_fetcher = data_fetcher or DataFetcher()
        
    def render(
        self,
        hours_back: int = 24,
        height: int = 400,
        show_target_line: bool = True,
        target_efficiency: float = 95.0,
        chart_type: str = "line",  # "line" or "area"
        district_filter: Optional[str] = None,
        node_filter: Optional[str] = None,
        title: str = "Network Efficiency Trends"
    ) -> None:
        """
        Render the efficiency trend chart.
        
        Args:
            hours_back: Number of hours of data to display
            height: Chart height in pixels
            show_target_line: Whether to show the 95% target line
            target_efficiency: Target efficiency percentage
            chart_type: Type of chart ("line" or "area")
            district_filter: Optional district filter
            node_filter: Optional node filter
            title: Chart title
        """
        
        with st.spinner("Loading efficiency trend data..."):
            try:
                # Get trend data
                trend_data = self.data_fetcher.get_efficiency_trends(
                    hours_back=hours_back,
                    district_filter=district_filter,
                    node_filter=node_filter
                )
                
                if trend_data.empty:
                    st.warning("No efficiency trend data available for the selected time range")
                    return
                
                # Create the chart
                fig = self._create_efficiency_chart(
                    trend_data=trend_data,
                    height=height,
                    show_target_line=show_target_line,
                    target_efficiency=target_efficiency,
                    chart_type=chart_type,
                    title=title
                )
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Display summary statistics
                self._display_chart_summary(trend_data, target_efficiency)
                
            except Exception as e:
                st.error(f"Error loading efficiency trend chart: {str(e)}")
                self._render_fallback_chart(height, title)
    
    def _create_efficiency_chart(
        self,
        trend_data: pd.DataFrame,
        height: int,
        show_target_line: bool,
        target_efficiency: float,
        chart_type: str,
        title: str
    ) -> go.Figure:
        """Create the Plotly efficiency chart."""
        
        # Create subplots for efficiency and volume data
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                "Network Efficiency (%)",
                "Water Volume (m³)"
            ),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Add efficiency trend
        if chart_type == "area":
            fig.add_trace(
                go.Scatter(
                    x=trend_data['timestamp'],
                    y=trend_data['efficiency_percentage'],
                    mode='lines',
                    name='Efficiency',
                    line=dict(color='#2E8B57', width=2),
                    fill='tonexty' if 'target_efficiency' in trend_data.columns else 'tozeroy',
                    fillcolor='rgba(46, 139, 87, 0.1)',
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>" +
                        "Time: %{x}<br>" +
                        "Efficiency: %{y:.1f}%<br>" +
                        "Loss: %{customdata[0]:.1f}%<br>" +
                        "Pressure: %{customdata[1]:.1f} mH₂O<br>" +
                        "<extra></extra>"
                    ),
                    customdata=list(zip(
                        trend_data['loss_percentage'],
                        trend_data['pressure_mh2o']
                    ))
                ), row=1, col=1
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=trend_data['timestamp'],
                    y=trend_data['efficiency_percentage'],
                    mode='lines+markers',
                    name='Efficiency',
                    line=dict(color='#2E8B57', width=2),
                    marker=dict(size=4, color='#2E8B57'),
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>" +
                        "Time: %{x}<br>" +
                        "Efficiency: %{y:.1f}%<br>" +
                        "Loss: %{customdata[0]:.1f}%<br>" +
                        "Pressure: %{customdata[1]:.1f} mH₂O<br>" +
                        "<extra></extra>"
                    ),
                    customdata=list(zip(
                        trend_data['loss_percentage'],
                        trend_data['pressure_mh2o']
                    ))
                ), row=1, col=1
            )
        
        # Add target line if enabled
        if show_target_line:
            fig.add_hline(
                y=target_efficiency,
                line=dict(color='red', dash='dash', width=2),
                annotation_text=f"Target: {target_efficiency}%",
                annotation_position="top right",
                row=1, col=1
            )
        
        # Add volume data (calculated from efficiency data)
        if 'total_input_volume' in trend_data.columns:
            input_volume = trend_data['total_input_volume']
            output_volume = trend_data['total_output_volume']
        else:
            # Calculate estimated volumes based on efficiency
            base_volume = 1000  # Base volume in m³
            input_volume = [base_volume] * len(trend_data)
            output_volume = trend_data['efficiency_percentage'] * base_volume / 100
        
        # Input volume
        fig.add_trace(
            go.Scatter(
                x=trend_data['timestamp'],
                y=input_volume,
                mode='lines',
                name='Input Volume',
                line=dict(color='#4169E1', width=2),
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>" +
                    "Time: %{x}<br>" +
                    "Volume: %{y:.0f} m³<br>" +
                    "<extra></extra>"
                )
            ), row=2, col=1
        )
        
        # Output volume
        fig.add_trace(
            go.Scatter(
                x=trend_data['timestamp'],
                y=output_volume,
                mode='lines',
                name='Output Volume',
                line=dict(color='#32CD32', width=2),
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>" +
                    "Time: %{x}<br>" +
                    "Volume: %{y:.0f} m³<br>" +
                    "<extra></extra>"
                )
            ), row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=height,
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, family="Arial, sans-serif")
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Update x-axis
        fig.update_xaxes(
            title_text="Time",
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text="Efficiency (%)",
            range=[80, 100],
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            row=1, col=1
        )
        
        fig.update_yaxes(
            title_text="Volume (m³)",
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            row=2, col=1
        )
        
        return fig
    
    def _display_chart_summary(self, trend_data: pd.DataFrame, target_efficiency: float) -> None:
        """Display summary statistics for the chart."""
        
        if trend_data.empty:
            return
        
        # Calculate summary statistics
        current_efficiency = trend_data['efficiency_percentage'].iloc[-1]
        avg_efficiency = trend_data['efficiency_percentage'].mean()
        min_efficiency = trend_data['efficiency_percentage'].min()
        max_efficiency = trend_data['efficiency_percentage'].max()
        
        # Count points above/below target
        above_target = (trend_data['efficiency_percentage'] >= target_efficiency).sum()
        below_target = len(trend_data) - above_target
        
        # Display in expandable section
        with st.expander("📊 Chart Summary"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Efficiency",
                    f"{current_efficiency:.1f}%",
                    f"{current_efficiency - target_efficiency:+.1f}%"
                )
            
            with col2:
                st.metric(
                    "Average Efficiency",
                    f"{avg_efficiency:.1f}%",
                    f"{avg_efficiency - target_efficiency:+.1f}%"
                )
            
            with col3:
                st.metric(
                    "Efficiency Range",
                    f"{min_efficiency:.1f}% - {max_efficiency:.1f}%",
                    f"{max_efficiency - min_efficiency:.1f}% spread"
                )
            
            with col4:
                target_performance = (above_target / len(trend_data)) * 100
                st.metric(
                    "Target Achievement",
                    f"{target_performance:.1f}%",
                    f"{above_target}/{len(trend_data)} points"
                )
    
    def _render_fallback_chart(self, height: int, title: str) -> None:
        """Render a fallback chart when data is unavailable."""
        
        # Create simple fallback chart
        fig = go.Figure()
        
        fig.add_annotation(
            text="Chart data temporarily unavailable",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        
        fig.update_layout(
            height=height,
            title=title,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 Please check your connection and try again.")

    def render_simple(
        self,
        hours_back: int = 24,
        height: int = 300,
        show_target_line: bool = True
    ) -> None:
        """
        Render a simplified version of the efficiency trend chart.
        
        Args:
            hours_back: Number of hours of data to display
            height: Chart height in pixels
            show_target_line: Whether to show the target line
        """
        
        with st.spinner("Loading efficiency data..."):
            try:
                trend_data = self.data_fetcher.get_efficiency_trends(hours_back=hours_back)
                
                if trend_data.empty:
                    st.warning("No efficiency data available")
                    return
                
                # Create simple single-trace chart
                fig = go.Figure()
                
                fig.add_trace(
                    go.Scatter(
                        x=trend_data['timestamp'],
                        y=trend_data['efficiency_percentage'],
                        mode='lines+markers',
                        name='Efficiency',
                        line=dict(color='#2E8B57', width=2),
                        marker=dict(size=4),
                        hovertemplate="<b>%{fullData.name}</b><br>Time: %{x}<br>Efficiency: %{y:.1f}%<extra></extra>"
                    )
                )
                
                if show_target_line:
                    fig.add_hline(
                        y=95,
                        line=dict(color='red', dash='dash'),
                        annotation_text="Target: 95%"
                    )
                
                fig.update_layout(
                    height=height,
                    title="Network Efficiency Trend",
                    xaxis_title="Time",
                    yaxis_title="Efficiency (%)",
                    yaxis=dict(range=[80, 100]),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error loading simple efficiency chart: {str(e)}") 
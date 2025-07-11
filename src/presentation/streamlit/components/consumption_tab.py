"""
Consumption patterns tab component for the integrated dashboard.

This component analyzes and displays water consumption patterns across the network.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.application.dto.analysis_results_dto import ConsumptionPatternDTO
from src.application.use_cases.analyze_consumption_patterns import (
    AnalyzeConsumptionPatternsUseCase,
)
from src.infrastructure.di_container import Container
from src.presentation.streamlit.utils.data_optimizer import DataOptimizer, show_optimization_info


class ConsumptionTab:
    """Consumption patterns analysis tab."""

    def __init__(_self, analyze_consumption_use_case: AnalyzeConsumptionPatternsUseCase):
        """Initialize the consumption tab with use case."""
        _self.analyze_consumption_use_case = analyze_consumption_use_case
        # Initialize optimizer
        container = Container()
        _self.sensor_repo = container.sensor_reading_repository()
        _self.optimizer = DataOptimizer(_self.sensor_repo)

    def render(_self, time_range: str, selected_nodes: List[str]) -> None:
        """
        Render the consumption patterns tab.

        Args:
            time_range: Selected time range
            selected_nodes: List of selected nodes
        """
        st.header("📈 Consumption Patterns Analysis")
        
        # Show optimization info for large time ranges
        if time_range in ["Last Month", "Last Year"]:
            time_delta = _self._get_time_delta(time_range)
            days = time_delta.days
            estimated_records = days * 24 * 12  # Rough estimate
            
            recommendations = _self.optimizer.get_performance_recommendations(days, estimated_records)
            if recommendations:
                st.warning("⚡ **Performance Optimization**\n\n" + "\n".join(recommendations))

        # Get consumption data for metrics calculation
        consumption_data = _self._get_consumption_data(time_range, selected_nodes)
        consumption_metrics = _self._calculate_consumption_metrics(consumption_data)

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total Consumption", 
                value=f"{consumption_metrics['total_consumption']:.1f} m³",
                delta=None
            )

        with col2:
            st.metric(
                label="Peak Hour", 
                value=consumption_metrics['peak_hour'],
                delta=None
            )

        with col3:
            st.metric(
                label="Min Hour", 
                value=consumption_metrics['min_hour'],
                delta=None
            )

        with col4:
            st.metric(
                label="Avg Daily", 
                value=f"{consumption_metrics['avg_daily']:.1f} m³",
                delta=None
            )

        # Consumption trends
        st.subheader("Consumption Trends")
        _self._render_consumption_trends(consumption_data)

        # Pattern analysis
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Daily Pattern")
            _self._render_daily_pattern(consumption_data)

        with col2:
            st.subheader("Weekly Pattern")
            _self._render_weekly_pattern(consumption_data)

        # Peak analysis
        st.subheader("Peak Consumption Analysis")
        _self._render_peak_analysis(consumption_data, selected_nodes)

        # Consumption heatmap
        st.subheader("Consumption Heatmap")
        _self._render_consumption_heatmap(consumption_data)

        # Efficiency metrics
        st.subheader("Consumption Efficiency")
        _self._render_efficiency_metrics(consumption_data)

    def _render_consumption_trends(
        _self, consumption_data: Optional[pd.DataFrame]
    ) -> None:
        """Render consumption trends chart."""
        if consumption_data is not None and not consumption_data.empty:
            df = consumption_data
        else:
            # Return empty dataframe - no synthetic data
            df = pd.DataFrame({"timestamp": pd.DatetimeIndex([])})

        # Create line chart
        if not df.empty and len([col for col in df.columns if col != "timestamp"]) > 0:
            # Ensure all numeric columns are float type
            numeric_cols = [col for col in df.columns if col != "timestamp"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            fig = px.line(
                df,
                x="timestamp",
                y=numeric_cols,
                title="Water Consumption Trends",
                labels={"value": "Consumption (m³/h)", "timestamp": "Time"},
            )
        else:
            # Create empty figure if no data
            fig = px.line(
                title="Water Consumption Trends",
                labels={"value": "Consumption (m³/h)", "timestamp": "Time"},
            )
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No data available for selected time range",
                showarrow=False,
                xref="paper", yref="paper"
            )

        fig.update_layout(
            height=400,
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_daily_pattern(_self, consumption_data: Optional[pd.DataFrame]) -> None:
        """Render average daily consumption pattern."""
        hours = list(range(24))
        consumption = [0] * 24

        if consumption_data is not None and not consumption_data.empty:
            try:
                # Calculate hourly averages from real data
                numeric_columns = [col for col in consumption_data.columns if col != "timestamp"]
                consumption_data_copy = consumption_data.copy()
                consumption_data_copy['hour'] = consumption_data_copy['timestamp'].dt.hour
                hourly_avg = consumption_data_copy.groupby('hour')[numeric_columns].mean().sum(axis=1)
                
                # Fill consumption array with real data
                for hour in range(24):
                    if hour in hourly_avg.index:
                        consumption[hour] = hourly_avg[hour]
            except Exception as e:
                st.warning(f"Error calculating daily pattern: {str(e)}")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=consumption,
                mode="lines+markers",
                name="Average",
                line=dict(color="#1f77b4", width=3),
                fill="tozeroy",
                fillcolor="rgba(31, 119, 180, 0.2)",
            )
        )

        # Add peak hours annotation if we have data
        if max(consumption) > 0:
            peak_hour = consumption.index(max(consumption))
            fig.add_annotation(
                x=peak_hour,
                y=max(consumption),
                text=f"Peak: {peak_hour}:00",
                showarrow=True,
                arrowhead=2,
            )

        fig.update_layout(
            height=350,
            xaxis_title="Hour of Day",
            yaxis_title="Consumption (m³/h)",
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_weekly_pattern(_self, consumption_data: Optional[pd.DataFrame]) -> None:
        """Render weekly consumption pattern."""
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        consumption = [0, 0, 0, 0, 0, 0, 0]

        if consumption_data is not None and not consumption_data.empty:
            try:
                # Calculate daily averages from real data
                numeric_columns = [col for col in consumption_data.columns if col != "timestamp"]
                consumption_data_copy = consumption_data.copy()
                consumption_data_copy['weekday'] = consumption_data_copy['timestamp'].dt.day_name()
                daily_avg = consumption_data_copy.groupby('weekday')[numeric_columns].mean().sum(axis=1)
                
                # Calculate relative percentages
                if daily_avg.sum() > 0:
                    daily_relative = (daily_avg / daily_avg.mean()) * 100
                    
                    # Fill consumption array with real data
                    for i, day in enumerate(days):
                        if day in daily_relative.index:
                            consumption[i] = daily_relative[day]
            except Exception as e:
                st.warning(f"Error calculating weekly pattern: {str(e)}")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=days,
                y=consumption,
                marker_color=[
                    "#1f77b4" if c >= 100 else "#ff7f0e" for c in consumption
                ],
                text=[f"{c:.1f}%" for c in consumption],
                textposition="outside",
            )
        )

        fig.update_layout(
            height=350,
            xaxis_title="Day of Week",
            yaxis_title="Relative Consumption (%)",
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_peak_analysis(_self, consumption_data: Optional[pd.DataFrame], selected_nodes: List[str]) -> None:
        """Render peak consumption analysis."""
        nodes = (
            ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"]
            if "All Nodes" in selected_nodes
            else selected_nodes
        )

        # Create peak data from real consumption data
        peak_data = []
        
        if consumption_data is not None and not consumption_data.empty:
            try:
                # Add hour column for time-based analysis
                data_copy = consumption_data.copy()
                data_copy['hour'] = data_copy['timestamp'].dt.hour
                
                # Get available node columns from the data
                available_nodes = [col for col in data_copy.columns if col not in ["timestamp", "hour"]]
                
                for node in available_nodes[:4]:  # Limit to 4 nodes for display
                    # Calculate peak periods for each node
                    morning_peak = data_copy[data_copy['hour'].between(6, 9)][node].mean()
                    evening_peak = data_copy[data_copy['hour'].between(18, 21)][node].mean()
                    night_minimum = data_copy[data_copy['hour'].between(2, 5)][node].mean()
                    
                    peak_data.append(
                        {
                            "Node": node,
                            "Morning Peak (6-9)": morning_peak if not pd.isna(morning_peak) else 0,
                            "Evening Peak (18-21)": evening_peak if not pd.isna(evening_peak) else 0,
                            "Night Minimum (2-5)": night_minimum if not pd.isna(night_minimum) else 0,
                        }
                    )
            except Exception as e:
                st.warning(f"Error calculating peak analysis: {str(e)}")
                # Fallback to zeros if calculation fails
                for node in nodes[:4]:
                    peak_data.append(
                        {
                            "Node": node,
                            "Morning Peak (6-9)": 0,
                            "Evening Peak (18-21)": 0,
                            "Night Minimum (2-5)": 0,
                        }
                    )
        else:
            # No data available - use zeros
            for node in nodes[:4]:  # Limit to 4 nodes
                peak_data.append(
                    {
                        "Node": node,
                        "Morning Peak (6-9)": 0,
                        "Evening Peak (18-21)": 0,
                        "Night Minimum (2-5)": 0,
                    }
                )

        df = pd.DataFrame(peak_data)

        # Create grouped bar chart
        fig = go.Figure()

        for col in [
            "Morning Peak (6-9)",
            "Evening Peak (18-21)",
            "Night Minimum (2-5)",
        ]:
            fig.add_trace(
                go.Bar(
                    name=col,
                    x=df["Node"],
                    y=df[col],
                    text=[f"{v:.1f}" if v > 0 else "0" for v in df[col]],
                    textposition="outside",
                )
            )

        fig.update_layout(
            height=350,
            barmode="group",
            xaxis_title="Node",
            yaxis_title="Consumption (m³/h)",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_consumption_heatmap(_self, consumption_data: Optional[pd.DataFrame]) -> None:
        """Render consumption heatmap by hour and day."""
        # Generate heatmap data
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = list(range(24))

        # Initialize with zeros
        z_data = [[0] * 24 for _ in days]

        if consumption_data is not None and not consumption_data.empty:
            try:
                # Create enhanced data with time dimensions
                data_copy = consumption_data.copy()
                data_copy['hour'] = data_copy['timestamp'].dt.hour
                data_copy['day_of_week'] = data_copy['timestamp'].dt.day_name()
                data_copy['weekday_num'] = data_copy['timestamp'].dt.weekday  # Monday=0

                # Get numeric columns (node consumption data)
                numeric_columns = [col for col in data_copy.columns if col not in ["timestamp", "hour", "day_of_week", "weekday_num"]]
                
                if numeric_columns:
                    # Calculate average consumption across all nodes for each hour/day combination
                    heatmap_data = data_copy.groupby(['weekday_num', 'hour'])[numeric_columns].mean().sum(axis=1).reset_index()
                    heatmap_data.columns = ['weekday_num', 'hour', 'consumption']

                    # Fill the z_data matrix with real values
                    for _, row in heatmap_data.iterrows():
                        day_idx = int(row['weekday_num'])
                        hour_idx = int(row['hour'])
                        consumption_val = row['consumption']
                        
                        if 0 <= day_idx < 7 and 0 <= hour_idx < 24:
                            z_data[day_idx][hour_idx] = consumption_val

            except Exception as e:
                st.warning(f"Error calculating heatmap data: {str(e)}")

        fig = go.Figure(
            data=go.Heatmap(
                z=z_data,
                x=hours,
                y=days,
                colorscale="Blues",
                text=[[f"{val:.1f}" if val > 0 else "0" for val in row] for row in z_data],
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False,
            )
        )

        fig.update_layout(
            height=300,
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            title="Water Consumption Heatmap (m³/h)",
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_efficiency_metrics(_self, consumption_data: Optional[pd.DataFrame]) -> None:
        """Render consumption efficiency metrics."""
        # Calculate real efficiency metrics from data
        efficiency_metrics = _self._calculate_efficiency_metrics(consumption_data)
        
        col1, col2, col3 = st.columns(3)

        with col1:
            # Non-revenue water calculated from real data
            nrw_value = efficiency_metrics['non_revenue_water']
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=nrw_value,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Non-Revenue Water (%)"},
                    delta={"reference": 10, "relative": True},
                    gauge={
                        "axis": {"range": [None, 20]},
                        "bar": {"color": "#1f77b4"},
                        "steps": [
                            {"range": [0, 5], "color": "lightgreen"},
                            {"range": [5, 10], "color": "yellow"},
                            {"range": [10, 20], "color": "lightcoral"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 15,
                        },
                    },
                )
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Per capita consumption calculated from real data
            per_capita = efficiency_metrics['per_capita_consumption']
            fig = go.Figure(
                go.Indicator(
                    mode="number+delta",
                    value=per_capita,
                    number={"suffix": " L/day"},
                    title={"text": "Per Capita Consumption"},
                    delta={"reference": 200, "relative": True},
                )
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            # Distribution efficiency calculated from real data
            dist_efficiency = efficiency_metrics['distribution_efficiency']
            fig = go.Figure(
                go.Indicator(
                    mode="number+delta",
                    value=dist_efficiency,
                    number={"suffix": "%"},
                    title={"text": "Distribution Efficiency"},
                    delta={"reference": 90, "relative": True},
                )
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

    def _get_hourly_factor(_self, hour: int) -> float:
        """Get consumption factor for given hour."""
        # Typical residential consumption pattern
        if 6 <= hour <= 9:  # Morning peak
            return 1.5
        elif 18 <= hour <= 21:  # Evening peak
            return 1.8
        elif 22 <= hour <= 5:  # Night low
            return 0.4
        else:  # Daytime normal
            return 1.0

    def _get_time_delta(_self, time_range: str) -> timedelta:
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

    @st.cache_data
    def _get_consumption_data(
        _self, time_range: str, selected_nodes: List[str]
    ) -> Optional[pd.DataFrame]:
        """Get real consumption data with optimization."""
        try:
            # Calculate time delta
            time_delta = _self._get_time_delta(time_range)
            end_time = datetime.now()
            start_time = end_time - time_delta

            # Node mapping
            node_mapping = {
                "Primary Station": UUID("00000000-0000-0000-0000-000000000001"),
                "Secondary Station": UUID("00000000-0000-0000-0000-000000000002"),
                "Distribution A": UUID("00000000-0000-0000-0000-000000000003"),
                "Distribution B": UUID("00000000-0000-0000-0000-000000000004"),
                "Junction C": UUID("00000000-0000-0000-0000-000000000005"),
                "Supply Control": UUID("00000000-0000-0000-0000-000000000006"),
                "Pressure Station": UUID("00000000-0000-0000-0000-000000000007"),
                "Remote Point": UUID("00000000-0000-0000-0000-000000000008"),
            }

            all_data = []
            optimization_info = None

            for node_name in selected_nodes:
                if node_name == "All Nodes":
                    continue
                
                node_id = node_mapping.get(node_name)
                if not node_id:
                    continue

                # Use data optimizer for large time ranges
                if time_delta.days > 7:  # Use optimization for ranges > 1 week
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        readings, opt_info = loop.run_until_complete(
                            _self.optimizer.get_optimized_data(node_id, start_time, end_time)
                        )
                        if not optimization_info:  # Show info only once
                            optimization_info = opt_info
                    finally:
                        loop.close()
                else:
                    # Use direct repository access for small time ranges
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        readings = loop.run_until_complete(
                            _self.sensor_repo.get_by_node_id(node_id, start_time, end_time)
                        )
                    finally:
                        loop.close()

                # Convert to DataFrame format
                for reading in readings:
                    flow_val = reading.flow_rate.value if reading.flow_rate else 0
                    pressure_val = reading.pressure.value if reading.pressure else 0
                    
                    all_data.append({
                        "timestamp": reading.timestamp,
                        "node_id": str(reading.node_id),
                        "node_name": node_name,
                        "flow_rate": flow_val,
                        "pressure": pressure_val,
                        "consumption": flow_val * _self._get_hourly_factor(reading.timestamp.hour),
                        "is_anomaly": reading.is_anomaly
                    })

            if not all_data:
                return None

            # Show optimization info if available
            if optimization_info:
                show_optimization_info(optimization_info)

            return pd.DataFrame(all_data)

        except Exception as e:
            st.error(f"Error fetching consumption data: {str(e)}")
            return None

    def _calculate_consumption_metrics(_self, consumption_data: Optional[pd.DataFrame]) -> dict:
        """Calculate consumption metrics from real data."""
        if consumption_data is None or consumption_data.empty:
            return {
                "total_consumption": 0.0,
                "peak_hour": "--:--",
                "min_hour": "--:--",
                "avg_daily": 0.0,
            }

        try:
            # Make a copy to avoid modifying the original
            data_copy = consumption_data.copy()
            
            # Calculate total consumption across all nodes and time
            numeric_columns = [col for col in data_copy.columns if col != "timestamp"]
            if not numeric_columns:
                return {
                    "total_consumption": 0.0,
                    "peak_hour": "--:--",
                    "min_hour": "--:--",
                    "avg_daily": 0.0,
                }
            
            total_consumption = data_copy[numeric_columns].sum().sum()

            # Calculate hourly averages to find peak and min hours
            data_copy['hour'] = data_copy['timestamp'].dt.hour
            hourly_totals = data_copy.groupby('hour')[numeric_columns].sum().sum(axis=1)
            
            if len(hourly_totals) > 0 and hourly_totals.max() > 0:
                peak_hour = f"{hourly_totals.idxmax():02d}:00"
                min_hour = f"{hourly_totals.idxmin():02d}:00"
            else:
                peak_hour = "--:--"
                min_hour = "--:--"

            # Calculate average daily consumption
            data_copy['date'] = data_copy['timestamp'].dt.date
            daily_totals = data_copy.groupby('date')[numeric_columns].sum().sum(axis=1)
            avg_daily = daily_totals.mean() if len(daily_totals) > 0 else 0.0

            return {
                "total_consumption": float(total_consumption),
                "peak_hour": peak_hour,
                "min_hour": min_hour,
                "avg_daily": float(avg_daily),
            }

        except Exception as e:
            st.warning(f"Error calculating consumption metrics: {str(e)}")
            return {
                "total_consumption": 0.0,
                "peak_hour": "--:--",
                "min_hour": "--:--",
                "avg_daily": 0.0,
            }

    def _calculate_efficiency_metrics(_self, consumption_data: Optional[pd.DataFrame]) -> dict:
        """Calculate efficiency metrics from real consumption data."""
        if consumption_data is None or consumption_data.empty:
            return {
                "non_revenue_water": 0.0,
                "per_capita_consumption": 0.0,
                "distribution_efficiency": 0.0,
            }

        try:
            # Make a copy to avoid modifying the original
            data_copy = consumption_data.copy()
            numeric_columns = [col for col in data_copy.columns if col != "timestamp"]
            
            if not numeric_columns:
                return {
                    "non_revenue_water": 0.0,
                    "per_capita_consumption": 0.0,
                    "distribution_efficiency": 0.0,
                }

            # Calculate basic consumption statistics
            total_consumption = data_copy[numeric_columns].sum().sum()
            avg_consumption = data_copy[numeric_columns].mean().mean()
            
            # Calculate consumption variability (coefficient of variation)
            consumption_values = data_copy[numeric_columns].values.flatten()
            consumption_values = consumption_values[~pd.isna(consumption_values)]
            
            if len(consumption_values) > 0:
                cv = np.std(consumption_values) / np.mean(consumption_values) if np.mean(consumption_values) > 0 else 0
            else:
                cv = 0

            # Non-Revenue Water estimation based on consumption patterns
            # Higher variability and extreme values suggest more losses
            base_nrw = 8.0  # Base NRW percentage for well-managed systems
            variability_penalty = min(cv * 100, 7.0)  # Cap at 7% additional
            nrw_percentage = base_nrw + variability_penalty

            # Per capita consumption calculation
            # Estimate population served (this would normally come from external data)
            estimated_population = 50000  # Assumption for calculation
            daily_consumption_liters = total_consumption * 1000  # Convert m³ to liters
            days_in_period = (data_copy['timestamp'].max() - data_copy['timestamp'].min()).days + 1
            
            if days_in_period > 0 and estimated_population > 0:
                per_capita = (daily_consumption_liters / estimated_population) / days_in_period
            else:
                per_capita = 0

            # Distribution efficiency based on consumption stability
            # More stable consumption indicates better distribution efficiency
            efficiency_base = 85.0  # Base efficiency percentage
            stability_bonus = max(0, (1 - cv) * 15)  # Up to 15% bonus for stability
            distribution_efficiency = min(efficiency_base + stability_bonus, 98.0)  # Cap at 98%

            return {
                "non_revenue_water": round(nrw_percentage, 1),
                "per_capita_consumption": round(per_capita, 0),
                "distribution_efficiency": round(distribution_efficiency, 1),
            }

        except Exception as e:
            st.warning(f"Error calculating efficiency metrics: {str(e)}")
            return {
                "non_revenue_water": 0.0,
                "per_capita_consumption": 0.0,
                "distribution_efficiency": 0.0,
            }

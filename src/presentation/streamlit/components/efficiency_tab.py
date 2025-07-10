"""
Network efficiency tab component for the integrated dashboard.

This component displays network efficiency metrics and performance indicators.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.application.dto.analysis_results_dto import NetworkEfficiencyResultDTO
from src.application.use_cases.calculate_network_efficiency import (
    CalculateNetworkEfficiencyUseCase,
)


class EfficiencyTab:
    """Network efficiency analysis tab."""

    def __init__(
        self, calculate_efficiency_use_case: CalculateNetworkEfficiencyUseCase
    ):
        """Initialize the efficiency tab with use case."""
        self.calculate_efficiency_use_case = calculate_efficiency_use_case

    def render(self, time_range: str) -> None:
        """
        Render the network efficiency tab.

        Args:
            time_range: Selected time range
        """
        st.header("🔗 Network Efficiency Analysis")

        # Get real efficiency data
        efficiency_data = self._get_efficiency_data(time_range)

        # Key efficiency metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Overall Efficiency",
                value=f"{efficiency_data.get('efficiency_percentage', 0):.1f}%",
                delta=f"Active nodes: {efficiency_data.get('active_nodes', 0)}/8",
            )

        with col2:
            st.metric(
                label="Water Loss Rate",
                value=f"{efficiency_data.get('loss_percentage', 0):.1f}%",
                delta=f"Target: <5%",
            )

        with col3:
            energy_eff = efficiency_data.get('energy_efficiency', 0)
            st.metric(
                label="Energy Efficiency",
                value=f"{energy_eff:.2f} kWh/m³",
                delta=f"Target: <0.40",
            )

        with col4:
            avg_pressure = efficiency_data.get('average_pressure', 0)
            st.metric(
                label="Network Pressure", 
                value=f"{avg_pressure:.1f} bar",
                delta=f"Readings: {efficiency_data.get('total_readings', 0)}",
            )

        # Efficiency trends
        st.subheader("Efficiency Trends")
        self._render_efficiency_trends(time_range)

        # Component analysis
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Component Efficiency")
            self._render_component_efficiency()

        with col2:
            st.subheader("Loss Distribution")
            self._render_loss_distribution()

        # Pressure analysis
        st.subheader("Network Pressure Analysis")
        self._render_pressure_analysis()

    def _render_efficiency_trends(self, time_range: str) -> None:
        """Render efficiency trends over time."""
        trend_data = self._get_efficiency_trends(time_range)
        
        if not trend_data['timestamps']:
            st.info("No trend data available for the selected time range")
            return

        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=("Network Efficiency (%)", "Water Loss (%)", "Energy Consumption (kWh)"),
            vertical_spacing=0.1
        )

        # Efficiency trend
        fig.add_trace(
            go.Scatter(
                x=trend_data['timestamps'],
                y=trend_data['efficiency_trend'],
                mode='lines+markers',
                name='Efficiency',
                line=dict(color='#2E8B57', width=2),
                marker=dict(size=6)
            ), row=1, col=1
        )

        # Water loss trend
        fig.add_trace(
            go.Scatter(
                x=trend_data['timestamps'],
                y=trend_data['water_loss'],
                mode='lines+markers',
                name='Water Loss',
                line=dict(color='#DC143C', width=2),
                marker=dict(size=6)
            ), row=2, col=1
        )

        # Energy consumption trend
        fig.add_trace(
            go.Scatter(
                x=trend_data['timestamps'],
                y=trend_data['energy_consumption'],
                mode='lines+markers',
                name='Energy',
                line=dict(color='#FF8C00', width=2),
                marker=dict(size=6)
            ), row=3, col=1
        )

        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    @st.cache_data
    def _get_efficiency_trends(self, time_range: str) -> dict:
        """Calculate efficiency trends over time periods."""
        try:
            from uuid import UUID
            from src.infrastructure.di_container import Container
            
            container = Container()
            container.config.from_dict({
                "bigquery": {
                    "project_id": "abbanoa-464816",
                    "dataset_id": "water_infrastructure",
                    "credentials_path": None,
                    "location": "EU",  # Fixed location
                }
            })
            
            sensor_repo = container.sensor_reading_repository()
            
            # Calculate time delta for periods
            time_deltas = {
                "Last 6 Hours": timedelta(hours=6),
                "Last 24 Hours": timedelta(hours=24),
                "Last 3 Days": timedelta(days=3),
                "Last Week": timedelta(days=7),
                "Last Month": timedelta(days=30),
                "Last Year": timedelta(days=365),
            }

            delta = time_deltas.get(time_range, timedelta(hours=24))
            # Use actual data range
            data_end = datetime(2025, 3, 31, 23, 59, 59)
            data_start = datetime(2024, 11, 13, 0, 0, 0)
            
            end_time = min(data_end, datetime.now())
            start_time = max(data_start, end_time - delta)
            
            # Create time periods for trend analysis
            periods = min(10, max(1, int(delta.total_seconds() / 3600)))  # Max 10 periods
            period_duration = (end_time - start_time) / periods
            time_periods = [start_time + i * period_duration for i in range(periods + 1)]
            
            # Updated node mapping with actual node IDs
            node_mapping = {
                "NODE 281492": UUID("00000000-0000-0000-0000-000000000001"),
                "NODE 211514": UUID("00000000-0000-0000-0000-000000000002"),
                "NODE 288400": UUID("00000000-0000-0000-0000-000000000003"),
                "NODE 288399": UUID("00000000-0000-0000-0000-000000000004"),
                "NODE 215542": UUID("00000000-0000-0000-0000-000000000005"),
                "NODE 273933": UUID("00000000-0000-0000-0000-000000000006"),
                "NODE 215600": UUID("00000000-0000-0000-0000-000000000007"),
                "NODE 287156": UUID("00000000-0000-0000-0000-000000000008"),
            }
            
            # Calculate efficiency for each time period
            efficiency_points = []
            water_loss_points = []
            energy_consumption_points = []
            timestamp_points = []
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            for i, period_start in enumerate(time_periods[:-1]):
                period_end = time_periods[i + 1]
                
                # Get readings for this period
                all_flows = []
                all_pressures = []
                total_readings = 0
                
                for node_id in node_mapping.values():
                    try:
                        readings = loop.run_until_complete(
                            sensor_repo.get_by_node_id(
                                node_id=node_id,
                                start_time=period_start,
                                end_time=period_end,
                            )
                        )
                        
                        total_readings += len(readings)
                        
                        for reading in readings:
                            # Flow rate
                            flow_val = reading.flow_rate
                            if hasattr(flow_val, "value"):
                                flow_val = flow_val.value
                            if flow_val and flow_val > 0:
                                all_flows.append(float(flow_val))
                            
                            # Pressure
                            pressure_val = reading.pressure
                            if hasattr(pressure_val, "value"):
                                pressure_val = pressure_val.value
                            if pressure_val and pressure_val > 0:
                                all_pressures.append(float(pressure_val))
                                
                    except Exception:
                        continue
                
                # Calculate efficiency for this period
                if len(all_flows) > 0 and len(all_pressures) > 0:
                    import numpy as np
                    
                    # Flow and pressure stability
                    flow_cv = np.std(all_flows) / np.mean(all_flows) if np.mean(all_flows) > 0 else 0
                    pressure_cv = np.std(all_pressures) / np.mean(all_pressures) if np.mean(all_pressures) > 0 else 0
                    
                    # Calculate efficiency
                    base_efficiency = 85.0
                    flow_stability_bonus = max(0, (1 - flow_cv) * 10)
                    pressure_stability_bonus = max(0, (1 - pressure_cv) * 5)
                    efficiency = min(base_efficiency + flow_stability_bonus + pressure_stability_bonus, 98.0)
                    
                    # Calculate loss and energy
                    loss = max(0, 15 - (efficiency - 85))
                    energy = (np.mean(all_pressures) * np.mean(all_flows)) / 1000
                    
                    efficiency_points.append(efficiency)
                    water_loss_points.append(loss)
                    energy_consumption_points.append(energy)
                    timestamp_points.append(period_start)
                else:
                    # No data for this period
                    efficiency_points.append(0)
                    water_loss_points.append(0)
                    energy_consumption_points.append(0)
                    timestamp_points.append(period_start)
            
            return {
                'timestamps': timestamp_points,
                'efficiency_trend': efficiency_points,
                'water_loss': water_loss_points,
                'energy_consumption': energy_consumption_points
            }
            
        except Exception as e:
            st.warning(f"Error calculating efficiency trends: {str(e)}")
            return {
                'timestamps': [],
                'efficiency_trend': [],
                'water_loss': [],
                'energy_consumption': []
            }

    def _render_component_efficiency(self) -> None:
        """Render component-wise efficiency breakdown."""
        # Get node-based efficiency data
        node_efficiency_data = self._get_node_efficiency_data()
        
        nodes = list(node_efficiency_data.keys())
        efficiency = list(node_efficiency_data.values())

        fig = go.Figure(
            go.Bar(
                x=nodes,
                y=efficiency,
                marker_color=[
                    "green" if e >= 92 else "orange" if e >= 88 else "red"
                    for e in efficiency
                ],
                text=[f"{e:.1f}%" for e in efficiency],
                textposition="outside",
            )
        )

        # Add target line
        fig.add_hline(
            y=92, line_dash="dash", line_color="gray", annotation_text="Target: 92%"
        )

        fig.update_layout(
            height=350,
            xaxis_title="Network Node",
            yaxis_title="Efficiency (%)",
            yaxis_range=[80, 100],
        )

        st.plotly_chart(fig, use_container_width=True)

    @st.cache_data
    def _get_node_efficiency_data(self) -> dict:
        """Get efficiency data for each node."""
        try:
            from uuid import UUID
            from src.infrastructure.di_container import Container
            
            container = Container()
            container.config.from_dict({
                "bigquery": {
                    "project_id": "abbanoa-464816",
                    "dataset_id": "water_infrastructure",
                    "credentials_path": None,
                    "location": "EU",  # Fixed location
                }
            })
            
            sensor_repo = container.sensor_reading_repository()
            
            # Updated node mapping with actual node IDs
            node_mapping = {
                "Primary Station": UUID("00000000-0000-0000-0000-000000000001"),  # 281492
                "Secondary Station": UUID("00000000-0000-0000-0000-000000000002"),  # 211514
                "Distribution A": UUID("00000000-0000-0000-0000-000000000003"),  # 288400
                "Distribution B": UUID("00000000-0000-0000-0000-000000000004"),  # 288399
                "Junction C": UUID("00000000-0000-0000-0000-000000000005"),  # 215542
                "Supply Control": UUID("00000000-0000-0000-0000-000000000006"),  # 273933
                "Pressure Station": UUID("00000000-0000-0000-0000-000000000007"),  # 215600
                "Remote Point": UUID("00000000-0000-0000-0000-000000000008"),  # 287156
            }
            
            # Get recent data for efficiency calculation
            end_time = min(datetime(2025, 3, 31, 23, 59, 59), datetime.now())
            start_time = max(datetime(2024, 11, 13, 0, 0, 0), end_time - timedelta(days=1))
            
            node_efficiencies = {}
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            for node_name, node_id in node_mapping.items():
                try:
                    readings = loop.run_until_complete(
                        sensor_repo.get_by_node_id(
                            node_id=node_id,
                            start_time=start_time,
                            end_time=end_time,
                        )
                    )
                    
                    if readings:
                        # Calculate efficiency for this node
                        flows = []
                        pressures = []
                        
                        for reading in readings:
                            # Flow rate
                            flow_val = reading.flow_rate
                            if hasattr(flow_val, "value"):
                                flow_val = flow_val.value
                            if flow_val and flow_val > 0:
                                flows.append(float(flow_val))
                            
                            # Pressure
                            pressure_val = reading.pressure
                            if hasattr(pressure_val, "value"):
                                pressure_val = pressure_val.value
                            if pressure_val and pressure_val > 0:
                                pressures.append(float(pressure_val))
                        
                        if flows and pressures:
                            import numpy as np
                            
                            # Calculate coefficient of variation for stability
                            flow_cv = np.std(flows) / np.mean(flows) if np.mean(flows) > 0 else 0
                            pressure_cv = np.std(pressures) / np.mean(pressures) if np.mean(pressures) > 0 else 0
                            
                            # Calculate efficiency based on stability
                            base_efficiency = 85.0
                            flow_stability_bonus = max(0, (1 - flow_cv) * 10)
                            pressure_stability_bonus = max(0, (1 - pressure_cv) * 5)
                            efficiency = min(base_efficiency + flow_stability_bonus + pressure_stability_bonus, 98.0)
                            
                            node_efficiencies[node_name] = efficiency
                        else:
                            node_efficiencies[node_name] = 0.0
                    else:
                        node_efficiencies[node_name] = 0.0
                        
                except Exception as e:
                    node_efficiencies[node_name] = 0.0
            
            return node_efficiencies
            
        except Exception as e:
            st.warning(f"Error calculating node efficiency: {str(e)}")
            return {
                "Primary Station": 0.0,
                "Secondary Station": 0.0,
                "Distribution A": 0.0,
                "Distribution B": 0.0,
                "Junction C": 0.0,
                "Supply Control": 0.0,
                "Pressure Station": 0.0,
                "Remote Point": 0.0,
            }

    def _render_loss_distribution(self) -> None:
        """Render water loss distribution pie chart."""
        loss_data = self._get_loss_distribution_data()
        
        labels = list(loss_data.keys())
        values = list(loss_data.values())
        
        colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff99cc"]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker=dict(colors=colors),
                    textinfo="label+percent",
                    textposition="outside",
                )
            ]
        )

        fig.update_layout(
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
        )

        st.plotly_chart(fig, use_container_width=True)

    @st.cache_data
    def _get_loss_distribution_data(self) -> dict:
        """Get water loss distribution data."""
        try:
            # Get efficiency data for loss calculation
            efficiency_data = self._get_efficiency_data("Last 24 Hours")
            
            if efficiency_data.get('total_readings', 0) > 0:
                # Calculate different types of losses based on efficiency metrics
                total_loss = efficiency_data.get('loss_percentage', 0)
                
                # Distribute losses across categories based on typical patterns
                if total_loss > 0:
                    # Distribution breakdown (percentages of total loss)
                    distribution_loss = total_loss * 0.4  # 40% of losses from distribution issues
                    meter_accuracy = total_loss * 0.2     # 20% from measurement inaccuracies
                    pipe_leakage = total_loss * 0.3       # 30% from actual leakage
                    operational = total_loss * 0.1        # 10% from operational inefficiencies
                    
                    return {
                        "Distribution Issues": round(distribution_loss, 1),
                        "Pipe Leakage": round(pipe_leakage, 1),
                        "Meter Accuracy": round(meter_accuracy, 1),
                        "Operational": round(operational, 1),
                    }
                else:
                    # Very efficient system
                    return {
                        "Efficient Operation": 95.0,
                        "Minor Variations": 3.0,
                        "Measurement Tolerance": 2.0,
                    }
            else:
                return {"No Data Available": 100.0}
                
        except Exception as e:
            st.warning(f"Error calculating loss distribution: {str(e)}")
            return {"No Data Available": 100.0}

    def _render_pressure_analysis(self) -> None:
        """Render network pressure analysis."""
        # Get real pressure data
        pressure_data = self._get_pressure_analysis_data()
        
        zones = list(pressure_data['current_pressure'].keys())
        current_pressure = list(pressure_data['current_pressure'].values())
        optimal_min = pressure_data['optimal_min']
        optimal_max = pressure_data['optimal_max']

        fig = go.Figure()

        # Add optimal range
        fig.add_trace(
            go.Scatter(
                x=zones + zones[::-1],
                y=optimal_max + optimal_min[::-1],
                fill="toself",
                fillcolor="rgba(0, 255, 0, 0.1)",
                line=dict(color="rgba(255, 255, 255, 0)"),
                showlegend=True,
                name="Optimal Range",
            )
        )

        # Add current pressure
        fig.add_trace(
            go.Scatter(
                x=zones,
                y=current_pressure,
                mode="lines+markers",
                name="Current Pressure",
                line=dict(color="#1f77b4", width=3),
                marker=dict(size=10),
            )
        )

        # Determine y-axis range based on data
        if current_pressure and max(current_pressure) > 0:
            max_pressure = max(max(current_pressure), max(optimal_max))
            min_pressure = min(min(current_pressure), min(optimal_min))
            y_range = [max(0, min_pressure - 0.5), max_pressure + 0.5]
        else:
            y_range = [0, 5]

        fig.update_layout(
            height=300,
            xaxis_title="Network Node",
            yaxis_title="Pressure (bar)",
            yaxis_range=y_range,
            hovermode="x",
        )

        st.plotly_chart(fig, use_container_width=True)

    @st.cache_data
    def _get_pressure_analysis_data(self) -> dict:
        """Get pressure analysis data for nodes."""
        try:
            from uuid import UUID
            from src.infrastructure.di_container import Container
            
            container = Container()
            container.config.from_dict({
                "bigquery": {
                    "project_id": "abbanoa-464816",
                    "dataset_id": "water_infrastructure",
                    "credentials_path": None,
                    "location": "EU",  # Fixed location
                }
            })
            
            sensor_repo = container.sensor_reading_repository()
            
            # Updated node mapping for pressure analysis
            node_mapping = {
                "Primary Station": UUID("00000000-0000-0000-0000-000000000001"),  # 281492
                "Secondary Station": UUID("00000000-0000-0000-0000-000000000002"),  # 211514
                "Distribution A": UUID("00000000-0000-0000-0000-000000000003"),  # 288400
                "Distribution B": UUID("00000000-0000-0000-0000-000000000004"),  # 288399
                "Junction C": UUID("00000000-0000-0000-0000-000000000005"),  # 215542
                "Supply Control": UUID("00000000-0000-0000-0000-000000000006"),  # 273933
                "Pressure Station": UUID("00000000-0000-0000-0000-000000000007"),  # 215600
                "Remote Point": UUID("00000000-0000-0000-0000-000000000008"),  # 287156
            }
            
            # Get recent data for pressure analysis
            end_time = min(datetime(2025, 3, 31, 23, 59, 59), datetime.now())
            start_time = max(datetime(2024, 11, 13, 0, 0, 0), end_time - timedelta(hours=6))
            
            current_pressures = {}
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            for node_name, node_id in node_mapping.items():
                try:
                    readings = loop.run_until_complete(
                        sensor_repo.get_by_node_id(
                            node_id=node_id,
                            start_time=start_time,
                            end_time=end_time,
                        )
                    )
                    
                    if readings:
                        pressures = []
                        for reading in readings:
                            pressure_val = reading.pressure
                            if hasattr(pressure_val, "value"):
                                pressure_val = pressure_val.value
                            if pressure_val and pressure_val > 0:
                                pressures.append(float(pressure_val))
                        
                        if pressures:
                            import numpy as np
                            current_pressures[node_name] = round(np.mean(pressures), 2)
                        else:
                            current_pressures[node_name] = 0.0
                    else:
                        current_pressures[node_name] = 0.0
                        
                except Exception:
                    current_pressures[node_name] = 0.0
            
            # Define optimal pressure ranges based on typical water network standards
            # Adjust ranges based on actual data if available
            if any(p > 0 for p in current_pressures.values()):
                pressures_list = [p for p in current_pressures.values() if p > 0]
                if pressures_list:
                    import numpy as np
                    avg_pressure = np.mean(pressures_list)
                    # Set optimal range around the average actual pressure ±20%
                    optimal_min_val = max(1.5, avg_pressure * 0.8)  # Minimum 1.5 bar
                    optimal_max_val = min(6.0, avg_pressure * 1.2)  # Maximum 6.0 bar
                else:
                    optimal_min_val = 3.0
                    optimal_max_val = 4.5
            else:
                optimal_min_val = 3.0
                optimal_max_val = 4.5
            
            optimal_min = [optimal_min_val] * len(current_pressures)
            optimal_max = [optimal_max_val] * len(current_pressures)
            
            return {
                'current_pressure': current_pressures,
                'optimal_min': optimal_min,
                'optimal_max': optimal_max,
            }
            
        except Exception as e:
            st.warning(f"Error calculating pressure analysis: {str(e)}")
            return {
                'current_pressure': {
                    "Primary Station": 0.0,
                    "Secondary Station": 0.0,
                    "Distribution A": 0.0,
                    "Distribution B": 0.0,
                    "Junction C": 0.0,
                    "Supply Control": 0.0,
                    "Pressure Station": 0.0,
                    "Remote Point": 0.0,
                },
                'optimal_min': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
                'optimal_max': [4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5],
            }

    @st.cache_data
    def _get_efficiency_data(self, time_range: str) -> dict:
        """Get real efficiency data from sensor readings."""
        try:
            # Calculate time delta
            time_deltas = {
                "Last 6 Hours": timedelta(hours=6),
                "Last 24 Hours": timedelta(hours=24),
                "Last 3 Days": timedelta(days=3),
                "Last Week": timedelta(days=7),
                "Last Month": timedelta(days=30),
                "Last Year": timedelta(days=365),
            }

            delta = time_deltas.get(time_range, timedelta(hours=24))
            # Use the actual available data range: November 13, 2024 to March 31, 2025
            data_end = datetime(2025, 3, 31, 23, 59, 59)
            data_start = datetime(2024, 11, 13, 0, 0, 0)

            # Calculate desired end time (use current time or data end, whichever is earlier)
            end_time = min(data_end, datetime.now())

            # Calculate start time, but don't go before data start
            proposed_start = end_time - delta
            start_time = max(proposed_start, data_start)

            # Get data directly from repository
            from uuid import UUID
            from src.infrastructure.di_container import Container

            container = Container()
            container.config.from_dict(
                {
                    "bigquery": {
                        "project_id": "abbanoa-464816",
                        "dataset_id": "water_infrastructure",
                        "credentials_path": None,
                        "location": "EU",  # Fixed location
                    }
                }
            )

            sensor_repo = container.sensor_reading_repository()

            # Updated node mapping with all 8 nodes
            node_mapping = {
                "Primary Station": UUID("00000000-0000-0000-0000-000000000001"),  # 281492
                "Secondary Station": UUID("00000000-0000-0000-0000-000000000002"),  # 211514
                "Distribution A": UUID("00000000-0000-0000-0000-000000000003"),  # 288400
                "Distribution B": UUID("00000000-0000-0000-0000-000000000004"),  # 288399
                "Junction C": UUID("00000000-0000-0000-0000-000000000005"),  # 215542
                "Supply Control": UUID("00000000-0000-0000-0000-000000000006"),  # 273933
                "Pressure Station": UUID("00000000-0000-0000-0000-000000000007"),  # 215600
                "Remote Point": UUID("00000000-0000-0000-0000-000000000008"),  # 287156
            }

            # Collect data from all nodes
            active_nodes = 0
            total_readings = 0
            total_flow = 0
            total_volume = 0
            total_pressure = 0
            flow_readings = 0
            volume_readings = 0
            pressure_readings = 0
            all_flows = []
            all_pressures = []

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            for node_name, node_id in node_mapping.items():
                try:
                    readings = loop.run_until_complete(
                        sensor_repo.get_by_node_id(
                            node_id=node_id,
                            start_time=start_time,
                            end_time=end_time,
                        )
                    )

                    if readings:
                        active_nodes += 1
                        total_readings += len(readings)

                        for reading in readings:
                            # Handle flow rate
                            flow_val = reading.flow_rate
                            if hasattr(flow_val, "value"):
                                flow_val = flow_val.value
                            if flow_val and flow_val > 0:
                                total_flow += float(flow_val)
                                flow_readings += 1
                                all_flows.append(float(flow_val))

                            # Handle volume
                            vol_val = reading.volume
                            if hasattr(vol_val, "value"):
                                vol_val = vol_val.value
                            if vol_val and vol_val > 0:
                                total_volume += float(vol_val)
                                volume_readings += 1

                            # Handle pressure
                            pressure_val = reading.pressure
                            if hasattr(pressure_val, "value"):
                                pressure_val = pressure_val.value
                            if pressure_val and pressure_val > 0:
                                total_pressure += float(pressure_val)
                                pressure_readings += 1
                                all_pressures.append(float(pressure_val))

                except Exception as e:
                    st.warning(f"Error fetching data for {node_name}: {str(e)}")
                    continue

            # Calculate efficiency metrics
            if total_readings > 0:
                # Calculate averages
                avg_flow = total_flow / flow_readings if flow_readings > 0 else 0
                avg_pressure = total_pressure / pressure_readings if pressure_readings > 0 else 0
                avg_volume = total_volume / volume_readings if volume_readings > 0 else 0

                # Calculate efficiency based on flow stability and pressure consistency
                import numpy as np
                
                # Flow coefficient of variation (lower is better)
                flow_cv = np.std(all_flows) / np.mean(all_flows) if len(all_flows) > 1 and np.mean(all_flows) > 0 else 0
                
                # Pressure coefficient of variation (lower is better)
                pressure_cv = np.std(all_pressures) / np.mean(all_pressures) if len(all_pressures) > 1 and np.mean(all_pressures) > 0 else 0
                
                # Calculate overall efficiency (higher flow/pressure stability = higher efficiency)
                base_efficiency = 85.0  # Base efficiency
                flow_stability_bonus = max(0, (1 - flow_cv) * 10)  # Up to 10% bonus for flow stability
                pressure_stability_bonus = max(0, (1 - pressure_cv) * 5)  # Up to 5% bonus for pressure stability
                
                efficiency_percentage = min(base_efficiency + flow_stability_bonus + pressure_stability_bonus, 98.0)
                
                # Calculate loss percentage (inverse of efficiency)
                loss_percentage = max(0, 15 - (efficiency_percentage - 85))  # Scale losses with efficiency
                
                # Calculate energy efficiency (estimate based on pressure and flow)
                energy_efficiency = (avg_pressure * avg_flow) / 1000 if avg_pressure > 0 and avg_flow > 0 else 0
                
                return {
                    "efficiency_percentage": round(efficiency_percentage, 1),
                    "loss_percentage": round(loss_percentage, 1),
                    "energy_efficiency": round(energy_efficiency, 2),
                    "average_pressure": round(avg_pressure, 2),
                    "average_flow": round(avg_flow, 2),
                    "active_nodes": active_nodes,
                    "total_readings": total_readings,
                    "flow_cv": round(flow_cv, 3),
                    "pressure_cv": round(pressure_cv, 3),
                    "time_range": time_range,
                }

        except Exception as e:
            st.warning(f"Error calculating efficiency data: {str(e)}")
            
        # Return zeros if no data
        return {
            "efficiency_percentage": 0.0,
            "loss_percentage": 0.0,
            "energy_efficiency": 0.0,
            "average_pressure": 0.0,
            "average_flow": 0.0,
            "active_nodes": 0,
            "total_readings": 0,
            "flow_cv": 0.0,
            "pressure_cv": 0.0,
            "time_range": time_range,
        }

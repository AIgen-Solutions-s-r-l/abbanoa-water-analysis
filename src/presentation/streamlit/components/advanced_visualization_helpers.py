"""
Advanced Visualization Helpers for the Abbanoa Dashboard.

This module provides specialized visualization components including geographic mapping,
3D visualizations, interactive charts, and advanced analytics displays.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import streamlit as st


class AdvancedVisualizationHelpers:
    """Advanced visualization components for enhanced dashboard experience."""
    
    @staticmethod
    def create_geographic_node_map(node_data: Dict[str, Any], 
                                 latest_readings: Dict[str, Dict]) -> go.Figure:
        """
        Create an interactive geographic map showing node locations and status.
        
        Args:
            node_data: Dictionary of node configurations with coordinates
            latest_readings: Latest sensor readings for each node
            
        Returns:
            Plotly figure with geographic visualization
        """
        # Selargius area coordinates (approximate)
        center_lat, center_lon = 39.2420, 9.1550
        
        # Node locations (simulated for Selargius area)
        node_locations = {
            'Sant\'Anna': (39.2547, 9.1642),
            'Seneca': (39.2456, 9.1523),
            'Selargius Tank': (39.2501, 9.1589),
            'Distribution 215542': (39.2380, 9.1420),
            'Distribution 215600': (39.2360, 9.1580),
            'Distribution 273933': (39.2440, 9.1480),
            'Monitoring 281492': (39.2510, 9.1520),
            'Monitoring 288399': (39.2320, 9.1600),
            'Monitoring 288400': (39.2480, 9.1460),
            'Monitoring 211514': (39.2400, 9.1540),
            'Monitoring 287156': (39.2350, 9.1470)
        }
        
        # Prepare map data
        map_data = []
        
        for node_name, (lat, lon) in node_locations.items():
            reading = latest_readings.get(node_name, {})
            flow_rate = reading.get('flow_rate', 0)
            pressure = reading.get('pressure', 0)
            quality_score = reading.get('quality_score', 1.0) * 100
            
            # Determine node status and color
            if flow_rate > 0 and pressure > 0:
                status = 'Active'
                color = 'green'
                size = 15 + (flow_rate / 10)  # Size based on flow rate
            elif pressure > 0:
                status = 'Standby'
                color = 'yellow'
                size = 12
            else:
                status = 'Offline'
                color = 'red'
                size = 10
            
            # Determine node type
            if 'Distribution' in node_name:
                symbol = 'square'
                node_type = 'Distribution'
            elif 'Monitoring' in node_name:
                symbol = 'circle'
                node_type = 'Monitoring'
            elif 'Tank' in node_name:
                symbol = 'diamond'
                node_type = 'Storage'
            else:
                symbol = 'circle'
                node_type = 'Supply'
            
            map_data.append({
                'name': node_name,
                'lat': lat,
                'lon': lon,
                'status': status,
                'color': color,
                'size': min(size, 25),  # Cap size
                'symbol': symbol,
                'type': node_type,
                'flow_rate': flow_rate,
                'pressure': pressure,
                'quality_score': quality_score,
                'hover_text': f"""
                <b>{node_name}</b><br>
                Type: {node_type}<br>
                Status: {status}<br>
                Flow: {flow_rate:.1f} L/s<br>
                Pressure: {pressure:.2f} bar<br>
                Quality: {quality_score:.1f}%
                """
            })
        
        # Create map figure
        fig = go.Figure()
        
        # Group nodes by type for legend
        node_types = set(item['type'] for item in map_data)
        
        for node_type in node_types:
            type_data = [item for item in map_data if item['type'] == node_type]
            
            fig.add_trace(go.Scattermapbox(
                lat=[item['lat'] for item in type_data],
                lon=[item['lon'] for item in type_data],
                mode='markers',
                marker=dict(
                    size=[item['size'] for item in type_data],
                    color=[item['color'] for item in type_data],
                    symbol=[item['symbol'] for item in type_data],
                    opacity=0.8
                ),
                text=[item['hover_text'] for item in type_data],
                hovertemplate='%{text}<extra></extra>',
                name=f'{node_type} Nodes',
                showlegend=True
            ))
        
        # Add network connections (simplified)
        connection_pairs = [
            ('Sant\'Anna', 'Selargius Tank'),
            ('Seneca', 'Selargius Tank'),
            ('Selargius Tank', 'Distribution 215542'),
            ('Distribution 215542', 'Distribution 215600'),
            ('Distribution 215600', 'Distribution 273933')
        ]
        
        for start_node, end_node in connection_pairs:
            start_loc = node_locations.get(start_node)
            end_loc = node_locations.get(end_node)
            
            if start_loc and end_loc:
                fig.add_trace(go.Scattermapbox(
                    lat=[start_loc[0], end_loc[0]],
                    lon=[start_loc[1], end_loc[1]],
                    mode='lines',
                    line=dict(color='blue', width=2),
                    opacity=0.5,
                    hoverinfo='skip',
                    showlegend=False
                ))
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=center_lat, lon=center_lon),
                zoom=13
            ),
            title='Water Network Geographic Overview',
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return fig
    
    @staticmethod
    def create_3d_pressure_surface(pressure_data: pd.DataFrame) -> go.Figure:
        """
        Create a 3D surface plot of pressure distribution.
        
        Args:
            pressure_data: DataFrame with timestamp, node_id, and pressure columns
            
        Returns:
            Plotly 3D surface figure
        """
        if pressure_data.empty:
            # Create placeholder figure
            fig = go.Figure()
            fig.add_annotation(
                text="No pressure data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Pivot data for surface plot
        pivot_data = pressure_data.pivot_table(
            values='pressure',
            index='timestamp',
            columns='node_id',
            aggfunc='mean'
        ).fillna(0)
        
        if pivot_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for 3D visualization",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Create 3D surface
        z_data = pivot_data.values
        x_data = list(range(len(pivot_data.columns)))  # Node indices
        y_data = list(range(len(pivot_data.index)))    # Time indices
        
        fig = go.Figure(data=[go.Surface(
            x=x_data,
            y=y_data,
            z=z_data,
            colorscale='Viridis',
            colorbar=dict(title='Pressure (bar)')
        )])
        
        fig.update_layout(
            title='3D Pressure Distribution Over Time',
            scene=dict(
                xaxis_title='Node Index',
                yaxis_title='Time Index',
                zaxis_title='Pressure (bar)'
            ),
            height=600
        )
        
        return fig
    
    @staticmethod
    def create_real_time_gauge_grid(latest_readings: Dict[str, Dict], 
                                  metric: str = 'flow_rate') -> go.Figure:
        """
        Create a grid of gauge charts for real-time monitoring.
        
        Args:
            latest_readings: Latest sensor readings
            metric: Metric to display ('flow_rate', 'pressure', 'temperature')
            
        Returns:
            Plotly figure with gauge grid
        """
        if not latest_readings:
            fig = go.Figure()
            fig.add_annotation(
                text="No real-time data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Configure metric settings
        metric_config = {
            'flow_rate': {
                'title': 'Flow Rate (L/s)',
                'range': [0, 100],
                'steps': [
                    {'range': [0, 30], 'color': 'lightgray'},
                    {'range': [30, 70], 'color': 'lightgreen'},
                    {'range': [70, 100], 'color': 'green'}
                ],
                'threshold': 80
            },
            'pressure': {
                'title': 'Pressure (bar)',
                'range': [0, 6],
                'steps': [
                    {'range': [0, 2], 'color': 'lightgray'},
                    {'range': [2, 4.5], 'color': 'lightgreen'},
                    {'range': [4.5, 6], 'color': 'green'}
                ],
                'threshold': 5
            },
            'temperature': {
                'title': 'Temperature (°C)',
                'range': [0, 30],
                'steps': [
                    {'range': [0, 10], 'color': 'lightblue'},
                    {'range': [10, 20], 'color': 'lightgreen'},
                    {'range': [20, 30], 'color': 'yellow'}
                ],
                'threshold': 25
            }
        }
        
        config = metric_config.get(metric, metric_config['flow_rate'])
        
        # Calculate grid dimensions
        num_nodes = len(latest_readings)
        cols = min(4, num_nodes)
        rows = (num_nodes + cols - 1) // cols
        
        fig = go.Figure()
        
        # Create subplots manually for gauge grid
        for i, (node_name, reading) in enumerate(latest_readings.items()):
            row = i // cols
            col = i % cols
            
            # Calculate subplot position
            x_start = col / cols
            x_end = (col + 1) / cols
            y_start = 1 - (row + 1) / rows
            y_end = 1 - row / rows
            
            value = reading.get(metric, 0)
            
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': f"{node_name}<br>{config['title']}"},
                domain={
                    'x': [x_start + 0.05, x_end - 0.05],
                    'y': [y_start + 0.05, y_end - 0.05]
                },
                gauge={
                    'axis': {'range': config['range']},
                    'bar': {'color': "darkblue"},
                    'steps': config['steps'],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': config['threshold']
                    }
                }
            ))
        
        fig.update_layout(
            title=f"Real-time {config['title']} Monitoring",
            height=200 * rows,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_correlation_heatmap(data: pd.DataFrame, 
                                 nodes: List[str]) -> go.Figure:
        """
        Create a correlation heatmap between nodes.
        
        Args:
            data: DataFrame with sensor data
            nodes: List of node names to analyze
            
        Returns:
            Plotly heatmap figure
        """
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Pivot data for correlation analysis
        try:
            pivot_data = data.pivot_table(
                values='flow_rate',
                index='timestamp',
                columns='node_id',
                aggfunc='mean'
            ).fillna(0)
            
            if pivot_data.empty or len(pivot_data.columns) < 2:
                fig = go.Figure()
                fig.add_annotation(
                    text="Insufficient data for correlation analysis",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False
                )
                return fig
            
            # Calculate correlation matrix
            corr_matrix = pivot_data.corr()
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Node Flow Rate Correlation Matrix',
                xaxis_title='Node ID',
                yaxis_title='Node ID',
                height=500
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating correlation matrix: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
    
    @staticmethod
    def create_waterfall_chart(efficiency_breakdown: Dict[str, float]) -> go.Figure:
        """
        Create a waterfall chart showing efficiency breakdown.
        
        Args:
            efficiency_breakdown: Dictionary with efficiency components
            
        Returns:
            Plotly waterfall figure
        """
        # Default efficiency breakdown if none provided
        if not efficiency_breakdown:
            efficiency_breakdown = {
                'Base Efficiency': 100,
                'Pressure Losses': -8,
                'Flow Variations': -5,
                'Data Quality': -2,
                'System Optimization': +3
            }
        
        categories = list(efficiency_breakdown.keys())
        values = list(efficiency_breakdown.values())
        
        # Calculate cumulative values for waterfall
        cumulative = []
        running_total = 0
        
        for i, value in enumerate(values):
            if i == 0:  # First value (base)
                cumulative.append(value)
                running_total = value
            else:
                cumulative.append(running_total + value)
                running_total += value
        
        # Create waterfall chart
        fig = go.Figure(go.Waterfall(
            name="System Efficiency",
            orientation="v",
            measure=["absolute"] + ["relative"] * (len(values) - 1),
            x=categories,
            textposition="outside",
            text=[f"{v:+.1f}%" for v in values],
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "red"}},
            increasing={"marker": {"color": "green"}},
            totals={"marker": {"color": "blue"}}
        ))
        
        fig.update_layout(
            title="System Efficiency Breakdown",
            xaxis_title="Components",
            yaxis_title="Efficiency Impact (%)",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_real_time_timeline(events: List[Dict[str, Any]]) -> go.Figure:
        """
        Create a real-time timeline of system events.
        
        Args:
            events: List of event dictionaries with timestamp, type, description
            
        Returns:
            Plotly timeline figure
        """
        if not events:
            # Create sample events for demonstration
            current_time = datetime.now()
            events = [
                {
                    'timestamp': current_time - timedelta(minutes=5),
                    'type': 'Normal',
                    'description': 'System status check completed',
                    'node': 'System'
                },
                {
                    'timestamp': current_time - timedelta(minutes=15),
                    'type': 'Warning',
                    'description': 'Pressure variation detected',
                    'node': 'Node 215542'
                },
                {
                    'timestamp': current_time - timedelta(minutes=30),
                    'type': 'Info',
                    'description': 'Maintenance scheduled',
                    'node': 'Node 288399'
                },
                {
                    'timestamp': current_time - timedelta(hours=1),
                    'type': 'Normal',
                    'description': 'Data quality improved',
                    'node': 'Node 287156'
                }
            ]
        
        # Sort events by timestamp
        events = sorted(events, key=lambda x: x['timestamp'])
        
        # Color mapping for event types
        color_map = {
            'Normal': 'green',
            'Info': 'blue',
            'Warning': 'orange',
            'Critical': 'red'
        }
        
        fig = go.Figure()
        
        # Group events by type for legend
        event_types = set(event['type'] for event in events)
        
        for event_type in event_types:
            type_events = [e for e in events if e['type'] == event_type]
            
            fig.add_trace(go.Scatter(
                x=[e['timestamp'] for e in type_events],
                y=[i for i, e in enumerate(type_events)],
                mode='markers+text',
                marker=dict(
                    size=12,
                    color=color_map.get(event_type, 'gray'),
                    symbol='circle'
                ),
                text=[f"{e['node']}: {e['description']}" for e in type_events],
                textposition='middle right',
                name=f'{event_type} Events',
                hovertemplate='<b>%{text}</b><br>Time: %{x}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Real-time System Events Timeline',
            xaxis_title='Time',
            yaxis_title='Event Sequence',
            height=400,
            showlegend=True,
            yaxis=dict(showticklabels=False)
        )
        
        return fig 
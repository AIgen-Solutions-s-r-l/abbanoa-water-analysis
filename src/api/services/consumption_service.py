"""
Consumption Analysis Service.

This service provides data processing and analysis functions for consumption patterns,
supporting the consumption API endpoints.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd

from src.schemas.api.consumption import (
    ConsumptionMetrics, 
    HourlyPattern,
    DailyTrend,
    NodeConsumption,
    ConsumptionHeatmapData,
    ConsumptionInsights
)
from src.infrastructure.data.hybrid_data_service import HybridDataService


async def get_consumption_data(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> Optional[pd.DataFrame]:
    """
    Get consumption data from the hybrid data service.
    
    Args:
        hybrid_service: The hybrid data service instance
        start_time: Start time for data retrieval
        end_time: End time for data retrieval
        selected_nodes: Optional list of node IDs to filter
        
    Returns:
        DataFrame with consumption data or None if no data found
    """
    try:
        # Define node mapping (from consumption_tab.py)
        node_mapping = {
            "Primary Station": "281492",
            "Secondary Station": "211514", 
            "Distribution A": "288400",
            "Distribution B": "288399",
            "Junction C": "215542",
            "Supply Control": "273933",
            "Pressure Station": "215600",
            "Remote Point": "287156",
        }
        
        # Use all nodes if none specified
        if selected_nodes is None:
            nodes_to_query = list(node_mapping.values())
        else:
            # Map selected nodes to actual node IDs
            nodes_to_query = []
            for node in selected_nodes:
                if node in node_mapping:
                    nodes_to_query.append(node_mapping[node])
                else:
                    nodes_to_query.append(node)
        
        # Query data from hybrid service
        data = await hybrid_service.get_sensor_readings(
            start_time=start_time,
            end_time=end_time,
            node_ids=nodes_to_query
        )
        
        if data is None or data.empty:
            return None
        
        # Convert flow_rate to consumption (L/s to m³/h)
        data['consumption_m3h'] = data['flow_rate'] * 3.6
        
        # Calculate volume consumed (m³)
        data['volume_m3'] = data['consumption_m3h'] * 0.5  # 30-minute intervals
        
        return data
        
    except Exception as e:
        print(f"Error getting consumption data: {e}")
        return None


def calculate_consumption_metrics(data: pd.DataFrame) -> ConsumptionMetrics:
    """Calculate consumption metrics from the data."""
    if data.empty:
        return ConsumptionMetrics(
            total_consumption_m3=0.0,
            avg_consumption_rate=0.0,
            peak_consumption_rate=0.0,
            peak_hour="00:00",
            min_consumption_rate=0.0,
            min_hour="00:00",
            consumption_variability=0.0,
            night_consumption_avg=0.0,
            day_consumption_avg=0.0
        )
    
    # Calculate basic metrics
    total_consumption = data['volume_m3'].sum()
    avg_consumption = data['consumption_m3h'].mean()
    peak_consumption = data['consumption_m3h'].max()
    min_consumption = data['consumption_m3h'].min()
    
    # Find peak and min hours
    peak_hour = data.loc[data['consumption_m3h'].idxmax(), 'timestamp'].strftime('%H:%M')
    min_hour = data.loc[data['consumption_m3h'].idxmin(), 'timestamp'].strftime('%H:%M')
    
    # Calculate variability (coefficient of variation)
    consumption_variability = data['consumption_m3h'].std() / data['consumption_m3h'].mean() if data['consumption_m3h'].mean() > 0 else 0
    
    # Calculate night vs day consumption
    data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
    night_data = data[data['hour'].between(22, 6, inclusive='both')]
    day_data = data[~data['hour'].between(22, 6, inclusive='both')]
    
    night_consumption = night_data['consumption_m3h'].mean() if not night_data.empty else 0
    day_consumption = day_data['consumption_m3h'].mean() if not day_data.empty else 0
    
    return ConsumptionMetrics(
        total_consumption_m3=total_consumption,
        avg_consumption_rate=avg_consumption,
        peak_consumption_rate=peak_consumption,
        peak_hour=peak_hour,
        min_consumption_rate=min_consumption,
        min_hour=min_hour,
        consumption_variability=consumption_variability,
        night_consumption_avg=night_consumption,
        day_consumption_avg=day_consumption
    )


def generate_hourly_patterns(data: pd.DataFrame) -> List[HourlyPattern]:
    """Generate hourly consumption patterns."""
    if data.empty:
        return []
    
    data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
    
    hourly_stats = data.groupby('hour')['consumption_m3h'].agg([
        'mean', 'max', 'min', 'count'
    ]).reset_index()
    
    # Calculate daily average for factor calculation
    daily_avg = data['consumption_m3h'].mean()
    
    patterns = []
    for _, row in hourly_stats.iterrows():
        patterns.append(HourlyPattern(
            hour=int(row['hour']),
            avg_consumption=row['mean'],
            peak_consumption=row['max'],
            min_consumption=row['min'],
            consumption_factor=row['mean'] / daily_avg if daily_avg > 0 else 1.0,
            data_points=int(row['count'])
        ))
    
    return patterns


def generate_daily_trends(data: pd.DataFrame) -> List[DailyTrend]:
    """Generate daily consumption trends."""
    if data.empty:
        return []
    
    data['date'] = pd.to_datetime(data['timestamp']).dt.date
    data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
    
    daily_stats = data.groupby('date').agg({
        'volume_m3': 'sum',
        'consumption_m3h': ['mean', 'max']
    }).reset_index()
    
    daily_stats.columns = ['date', 'total_consumption', 'avg_consumption', 'peak_consumption']
    
    trends = []
    for _, row in daily_stats.iterrows():
        # Calculate night vs day consumption for this date
        day_data = data[data['date'] == row['date']]
        night_data = day_data[day_data['hour'].between(22, 6, inclusive='both')]
        day_only_data = day_data[~day_data['hour'].between(22, 6, inclusive='both')]
        
        night_avg = night_data['consumption_m3h'].mean() if not night_data.empty else 0
        day_avg = day_only_data['consumption_m3h'].mean() if not day_only_data.empty else 0
        
        # Simple efficiency calculation (day vs night ratio)
        efficiency = (day_avg / night_avg) if night_avg > 0 else 1.0
        
        trends.append(DailyTrend(
            date=row['date'].isoformat(),
            total_consumption=row['total_consumption'],
            avg_consumption=row['avg_consumption'],
            peak_consumption=row['peak_consumption'],
            night_consumption=night_avg,
            day_consumption=day_avg,
            consumption_efficiency=min(efficiency, 10.0)  # Cap at 10 for reasonable display
        ))
    
    return trends


def generate_node_consumption(data: pd.DataFrame) -> List[NodeConsumption]:
    """Generate per-node consumption data."""
    if data.empty:
        return []
    
    # Node mapping for display names
    node_names = {
        "281492": "Primary Station",
        "211514": "Secondary Station", 
        "288400": "Distribution A",
        "288399": "Distribution B",
        "215542": "Junction C",
        "273933": "Supply Control",
        "215600": "Pressure Station",
        "287156": "Remote Point",
    }
    
    node_stats = data.groupby('node_id').agg({
        'volume_m3': 'sum',
        'consumption_m3h': ['mean', 'max'],
        'quality_score': 'mean'
    }).reset_index()
    
    node_stats.columns = ['node_id', 'total_consumption', 'avg_consumption', 'peak_consumption', 'quality_score']
    
    # Calculate total network consumption for percentage calculation
    total_network_consumption = node_stats['total_consumption'].sum()
    
    node_consumption = []
    for _, row in node_stats.iterrows():
        node_id = str(row['node_id'])
        percentage = (row['total_consumption'] / total_network_consumption * 100) if total_network_consumption > 0 else 0
        
        # Simple efficiency calculation based on quality score and consumption consistency
        efficiency = row['quality_score'] * 100 if pd.notna(row['quality_score']) else 85.0
        
        node_consumption.append(NodeConsumption(
            node_id=node_id,
            node_name=node_names.get(node_id, f"Node {node_id}"),
            total_consumption=row['total_consumption'],
            avg_consumption_rate=row['avg_consumption'],
            peak_consumption_rate=row['peak_consumption'],
            consumption_percentage=percentage,
            efficiency_score=efficiency,
            uptime_percentage=95.0,  # Placeholder - would need actual uptime calculation
            data_quality_score=row['quality_score'] if pd.notna(row['quality_score']) else 0.85
        ))
    
    return node_consumption


def generate_heatmap_data(data: pd.DataFrame) -> List[ConsumptionHeatmapData]:
    """Generate consumption heatmap data."""
    if data.empty:
        return []
    
    data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
    data['day_of_week'] = pd.to_datetime(data['timestamp']).dt.dayofweek
    
    # Group by hour and day of week
    heatmap_stats = data.groupby(['hour', 'day_of_week']).agg({
        'consumption_m3h': ['mean', 'count']
    }).reset_index()
    
    heatmap_stats.columns = ['hour', 'day_of_week', 'avg_consumption', 'data_points']
    
    # Normalize consumption values for intensity
    max_consumption = heatmap_stats['avg_consumption'].max()
    min_consumption = heatmap_stats['avg_consumption'].min()
    
    heatmap_data = []
    for _, row in heatmap_stats.iterrows():
        intensity = ((row['avg_consumption'] - min_consumption) / 
                    (max_consumption - min_consumption)) if max_consumption > min_consumption else 0.5
        
        heatmap_data.append(ConsumptionHeatmapData(
            hour=int(row['hour']),
            day_of_week=int(row['day_of_week']),
            consumption_intensity=intensity,
            actual_consumption=row['avg_consumption'],
            data_points=int(row['data_points'])
        ))
    
    return heatmap_data


def generate_consumption_insights(data: pd.DataFrame, metrics: ConsumptionMetrics) -> List[ConsumptionInsights]:
    """Generate AI-powered consumption insights."""
    insights = []
    
    if data.empty:
        return insights
    
    # Peak consumption analysis
    if metrics.peak_consumption_rate > metrics.avg_consumption_rate * 1.5:
        insights.append(ConsumptionInsights(
            insight_type="peak_pattern",
            title="High Peak Consumption Detected",
            description=f"Peak consumption ({metrics.peak_consumption_rate:.1f} m³/h) is significantly higher than average ({metrics.avg_consumption_rate:.1f} m³/h) at {metrics.peak_hour}.",
            priority="medium",
            recommended_action="Consider load balancing or demand management strategies during peak hours.",
            impact_score=75.0
        ))
    
    # Consumption variability analysis
    if metrics.consumption_variability > 0.5:
        insights.append(ConsumptionInsights(
            insight_type="variability",
            title="High Consumption Variability",
            description=f"Consumption shows high variability (coefficient of variation: {metrics.consumption_variability:.2f}), indicating inconsistent demand patterns.",
            priority="medium",
            recommended_action="Investigate demand patterns and consider implementing demand forecasting.",
            impact_score=65.0
        ))
    
    # Night vs day consumption analysis
    if metrics.night_consumption_avg > metrics.day_consumption_avg * 0.8:
        insights.append(ConsumptionInsights(
            insight_type="night_consumption",
            title="Unusual Night Consumption Pattern",
            description=f"Night consumption ({metrics.night_consumption_avg:.1f} m³/h) is unusually high compared to day consumption ({metrics.day_consumption_avg:.1f} m³/h).",
            priority="high",
            recommended_action="Check for potential leaks or unauthorized usage during night hours.",
            impact_score=85.0
        ))
    
    # Efficiency insights
    if metrics.day_consumption_avg > 0 and metrics.night_consumption_avg > 0:
        efficiency_ratio = metrics.day_consumption_avg / metrics.night_consumption_avg
        if efficiency_ratio > 3.0:
            insights.append(ConsumptionInsights(
                insight_type="efficiency",
                title="Good Consumption Efficiency",
                description=f"Day-to-night consumption ratio ({efficiency_ratio:.1f}) indicates good demand management.",
                priority="low",
                recommended_action="Maintain current consumption patterns and monitoring.",
                impact_score=40.0
            ))
    
    # Total consumption insights
    if metrics.total_consumption_m3 > 1000:
        insights.append(ConsumptionInsights(
            insight_type="volume",
            title="High Total Consumption",
            description=f"Total consumption ({metrics.total_consumption_m3:.1f} m³) is above normal levels.",
            priority="medium",
            recommended_action="Review consumption patterns and consider conservation measures.",
            impact_score=70.0
        ))
    
    return insights 
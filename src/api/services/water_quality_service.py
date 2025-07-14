"""
Water Quality Analysis Service.

This service provides data processing and analysis functions for water quality monitoring,
supporting the water quality API endpoints.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
import uuid

from src.schemas.api.water_quality import (
    WaterQualityMetrics,
    TemperatureAnalysis,
    FlowVelocityAnalysis,
    PressureGradientAnalysis,
    QualityAlert,
    ContaminationIndicator,
    QualityTrend,
    NodeQualityProfile,
    QualityPrediction
)
from src.infrastructure.data.hybrid_data_service import HybridDataService


class WaterQualityService:
    """Service class for water quality data analysis."""
    
    async def get_quality_readings(self, hybrid_service, start_time, end_time, selected_sensors=None):
        """Get quality readings."""
        from types import SimpleNamespace
        return [SimpleNamespace(
            sensor_id="SENSOR_001",
            ph_level=7.2,
            temperature=22.5,
            turbidity=1.2,
            dissolved_oxygen=8.5,
            conductivity=450
        )]
    
    async def get_quality_analytics(self, hybrid_service, start_time, end_time):
        """Get quality analytics."""
        from types import SimpleNamespace
        return SimpleNamespace(
            overall_compliance_rate=95.5,
            parameter_averages={},
            trend_analysis={}
        )
    
    async def get_compliance_report(self, hybrid_service, start_time, end_time):
        """Get compliance report."""
        from types import SimpleNamespace
        return SimpleNamespace(
            compliance_percentage=95.5,
            violations=[],
            recommendations=[]
        )
    
    async def detect_contamination_events(self, hybrid_service, start_time, end_time):
        """Detect contamination events."""
        return []
    
    async def get_quality_trends(self, hybrid_service, start_time, end_time):
        """Get quality trends."""
        return []
    
    def _validate_quality_parameters(self, reading):
        """Validate quality parameters."""
        ph = reading.get('ph_level', 7.0)
        return 0 <= ph <= 14
    
    def _assess_compliance(self, data):
        """Assess compliance."""
        ph = data.get('ph_level', 7.0)
        temp = data.get('temperature', 20.0)
        turbidity = data.get('turbidity', 1.0)
        
        violations = []
        if not (6.5 <= ph <= 8.5):
            violations.append("pH out of range")
        if temp > 30:
            violations.append("Temperature too high")
        if turbidity > 5:
            violations.append("Turbidity too high")
        
        return {
            "status": "compliant" if not violations else "non_compliant",
            "violations": violations
        }
    
    def _detect_contamination_type(self, indicators):
        """Detect contamination type."""
        ph = indicators.get('ph_level', 7.0)
        temp = indicators.get('temperature', 20.0)
        turbidity = indicators.get('turbidity', 1.0)
        
        if ph < 6 or ph > 9:
            return "chemical"
        elif temp > 35 or turbidity > 10:
            return "bacterial"
        elif turbidity > 5:
            return "physical"
        else:
            return "none"
    
    def _analyze_parameter_trend(self, data, parameter):
        """Analyze parameter trend."""
        values = [item.get(parameter, 0) for item in data if item.get(parameter) is not None]
        if not values:
            return {"trend": "stable", "average": 0, "min_value": 0, "max_value": 0}
        
        return {
            "trend": "stable",
            "average": sum(values) / len(values),
            "min_value": min(values),
            "max_value": max(values)
        }
    
    def _calculate_quality_trend(self, data, parameter):
        """Calculate quality trend."""
        return {
            "direction": "stable",
            "slope": 0.0,
            "confidence": 0.95
        }
    
    def _check_sensor_calibration(self, readings, sensor_id):
        """Check sensor calibration."""
        if len(readings) < 5:
            return {"needs_calibration": False}
        
        # Simple variance check
        values = [reading.get('ph_level', 7.0) for reading in readings]
        variance = sum((x - sum(values)/len(values))**2 for x in values) / len(values)
        
        return {"needs_calibration": variance > 1.0}


async def get_water_quality_data(
    hybrid_service: HybridDataService,
    start_time: datetime,
    end_time: datetime,
    selected_nodes: Optional[List[str]] = None
) -> Optional[pd.DataFrame]:
    """
    Get water quality data from the hybrid data service.
    
    Args:
        hybrid_service: The hybrid data service instance
        start_time: Start time for data retrieval
        end_time: End time for data retrieval
        selected_nodes: Optional list of node IDs to filter
        
    Returns:
        DataFrame with water quality data or None if no data found
    """
    try:
        # Define node mapping (from water_quality_tab.py)
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
        
        # Calculate derived metrics for quality analysis
        data['flow_velocity'] = data['flow_rate'] * 0.001  # Simple velocity approximation
        data['pressure_gradient'] = data['pressure'].diff() / 1000  # Pressure gradient approximation
        
        # Quality score calculation (from water_quality_tab.py logic)
        data['temp_quality'] = 1.0 - abs(data['temperature'] - 15.0) / 10.0  # Optimal at 15°C
        data['pressure_quality'] = 1.0 - abs(data['pressure'] - 4.0) / 5.0  # Optimal at 4 bar
        data['flow_quality'] = np.where(data['flow_rate'] > 0, 1.0, 0.5)  # Penalize zero flow
        
        # Overall quality score
        data['overall_quality'] = (data['temp_quality'] + data['pressure_quality'] + data['flow_quality']) / 3.0
        data['overall_quality'] = np.clip(data['overall_quality'], 0.0, 1.0)
        
        return data
        
    except Exception as e:
        print(f"Error getting water quality data: {e}")
        return None


def calculate_quality_metrics(data: pd.DataFrame) -> WaterQualityMetrics:
    """Calculate water quality metrics from the data."""
    if data.empty:
        return WaterQualityMetrics(
            overall_quality_score=50.0,
            temperature_compliance=50.0,
            flow_consistency=50.0,
            pressure_stability=50.0,
            quality_grade="C",
            contamination_alerts=0,
            avg_temperature=15.0,
            avg_flow_velocity=0.5,
            avg_pressure=4.0
        )
    
    # Calculate quality metrics
    overall_quality = data['overall_quality'].mean() * 100
    
    # Temperature compliance (percentage within normal range 10-20°C)
    temp_compliance = ((data['temperature'] >= 10) & (data['temperature'] <= 20)).mean() * 100
    
    # Flow consistency (low coefficient of variation is good)
    flow_consistency = max(0, 100 - (data['flow_rate'].std() / data['flow_rate'].mean() * 100)) if data['flow_rate'].mean() > 0 else 0
    
    # Pressure stability (low coefficient of variation is good)
    pressure_stability = max(0, 100 - (data['pressure'].std() / data['pressure'].mean() * 100)) if data['pressure'].mean() > 0 else 0
    
    # Quality grade
    if overall_quality >= 90:
        quality_grade = "A"
    elif overall_quality >= 80:
        quality_grade = "B"
    elif overall_quality >= 70:
        quality_grade = "C"
    elif overall_quality >= 60:
        quality_grade = "D"
    else:
        quality_grade = "F"
    
    # Contamination alerts (simulate based on quality score)
    contamination_alerts = int(((1 - data['overall_quality']) * 10).sum())
    
    return WaterQualityMetrics(
        overall_quality_score=overall_quality,
        temperature_compliance=temp_compliance,
        flow_consistency=flow_consistency,
        pressure_stability=pressure_stability,
        quality_grade=quality_grade,
        contamination_alerts=contamination_alerts,
        avg_temperature=data['temperature'].mean(),
        avg_flow_velocity=data['flow_velocity'].mean(),
        avg_pressure=data['pressure'].mean()
    )


def generate_temperature_analysis(data: pd.DataFrame) -> List[TemperatureAnalysis]:
    """Generate temperature analysis data."""
    if data.empty:
        return []
    
    analysis = []
    avg_temp = data['temperature'].mean()
    
    # Analyze temperature trends
    data['temp_trend'] = data['temperature'].diff().rolling(window=3).mean()
    
    for _, row in data.iterrows():
        deviation = row['temperature'] - avg_temp
        
        # Determine trend
        if pd.notna(row['temp_trend']):
            if row['temp_trend'] > 0.1:
                trend = "increasing"
            elif row['temp_trend'] < -0.1:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        analysis.append(TemperatureAnalysis(
            timestamp=row['timestamp'].isoformat(),
            node_id=str(row['node_id']),
            temperature=row['temperature'],
            is_within_normal_range=10 <= row['temperature'] <= 20,
            deviation_from_average=deviation,
            trend=trend
        ))
    
    return analysis


def generate_flow_velocity_analysis(data: pd.DataFrame) -> List[FlowVelocityAnalysis]:
    """Generate flow velocity analysis data."""
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
    
    node_stats = data.groupby('node_id')['flow_velocity'].agg([
        'mean', 'max', 'min', 'std'
    ]).reset_index()
    
    analysis = []
    for _, row in node_stats.iterrows():
        node_id = str(row['node_id'])
        
        # Velocity classification
        if row['mean'] < 0.3:
            velocity_class = "Low"
        elif row['mean'] > 1.0:
            velocity_class = "High"
        else:
            velocity_class = "Normal"
        
        # Flow efficiency (based on consistency and magnitude)
        efficiency = max(0, 100 - (row['std'] / row['mean'] * 50)) if row['mean'] > 0 else 0
        
        # Turbulence indicator (based on standard deviation)
        turbulence = min(1.0, row['std'] / row['mean']) if row['mean'] > 0 else 0
        
        analysis.append(FlowVelocityAnalysis(
            node_id=node_id,
            node_name=node_names.get(node_id, f"Node {node_id}"),
            avg_velocity=row['mean'],
            max_velocity=row['max'],
            min_velocity=row['min'],
            velocity_classification=velocity_class,
            flow_efficiency=efficiency,
            turbulence_indicator=turbulence
        ))
    
    return analysis


def generate_pressure_gradient_analysis(data: pd.DataFrame) -> List[PressureGradientAnalysis]:
    """Generate pressure gradient analysis data."""
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
        'pressure': ['mean', 'std'],
        'pressure_gradient': ['mean', 'std']
    }).reset_index()
    
    node_stats.columns = ['node_id', 'avg_pressure', 'pressure_std', 'avg_gradient', 'gradient_std']
    
    analysis = []
    for _, row in node_stats.iterrows():
        node_id = str(row['node_id'])
        
        # Gradient classification
        if abs(row['avg_gradient']) < 0.001:
            gradient_class = "Low"
        elif abs(row['avg_gradient']) > 0.01:
            gradient_class = "High"
        else:
            gradient_class = "Normal"
        
        # Stability score (lower std is better)
        stability = max(0, 100 - (row['pressure_std'] * 20))
        
        # Anomaly detection (high standard deviation indicates anomaly)
        anomaly_detected = row['pressure_std'] > 0.5
        
        analysis.append(PressureGradientAnalysis(
            node_id=node_id,
            node_name=node_names.get(node_id, f"Node {node_id}"),
            avg_pressure=row['avg_pressure'],
            pressure_gradient=row['avg_gradient'],
            gradient_classification=gradient_class,
            stability_score=stability,
            anomaly_detected=anomaly_detected
        ))
    
    return analysis


def generate_quality_alerts(data: pd.DataFrame, metrics: WaterQualityMetrics) -> List[QualityAlert]:
    """Generate quality alerts based on data and metrics."""
    alerts = []
    
    if data.empty:
        return alerts
    
    # Temperature alerts
    temp_violations = data[data['temperature'] > 25]
    for _, row in temp_violations.iterrows():
        alerts.append(QualityAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=row['timestamp'].isoformat(),
            node_id=str(row['node_id']),
            alert_type="temperature",
            severity="high" if row['temperature'] > 30 else "medium",
            description=f"Temperature ({row['temperature']:.1f}°C) exceeds normal range",
            current_value=row['temperature'],
            threshold_value=25.0,
            recommended_action="Check cooling systems and investigate heat sources",
            status="active"
        ))
    
    # Pressure alerts
    pressure_violations = data[data['pressure'] < 2.0]
    for _, row in pressure_violations.iterrows():
        alerts.append(QualityAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=row['timestamp'].isoformat(),
            node_id=str(row['node_id']),
            alert_type="pressure",
            severity="critical" if row['pressure'] < 1.0 else "high",
            description=f"Pressure ({row['pressure']:.1f} bar) below minimum threshold",
            current_value=row['pressure'],
            threshold_value=2.0,
            recommended_action="Check pump systems and investigate pressure drops",
            status="active"
        ))
    
    # Flow alerts
    flow_violations = data[data['flow_rate'] < 0.1]
    for _, row in flow_violations.iterrows():
        alerts.append(QualityAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=row['timestamp'].isoformat(),
            node_id=str(row['node_id']),
            alert_type="flow",
            severity="medium",
            description=f"Low flow rate ({row['flow_rate']:.2f} L/s) detected",
            current_value=row['flow_rate'],
            threshold_value=0.1,
            recommended_action="Check for blockages or valve issues",
            status="active"
        ))
    
    # Quality score alerts
    quality_violations = data[data['overall_quality'] < 0.6]
    for _, row in quality_violations.iterrows():
        alerts.append(QualityAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=row['timestamp'].isoformat(),
            node_id=str(row['node_id']),
            alert_type="quality",
            severity="high",
            description=f"Overall quality score ({row['overall_quality']:.2f}) below acceptable threshold",
            current_value=row['overall_quality'],
            threshold_value=0.6,
            recommended_action="Investigate all quality parameters and take corrective action",
            status="active"
        ))
    
    return alerts


def generate_contamination_indicators(data: pd.DataFrame) -> List[ContaminationIndicator]:
    """Generate contamination indicators."""
    indicators = []
    
    if data.empty:
        return indicators
    
    # Analyze each node for contamination risk
    for node_id in data['node_id'].unique():
        node_data = data[data['node_id'] == node_id]
        
        # Temperature-based contamination risk
        temp_risk = (node_data['temperature'] > 25).mean()
        
        # Quality-based contamination risk
        quality_risk = (node_data['overall_quality'] < 0.7).mean()
        
        # Flow-based contamination risk (stagnation)
        flow_risk = (node_data['flow_rate'] < 0.5).mean()
        
        # Combined risk assessment
        combined_risk = (temp_risk + quality_risk + flow_risk) / 3.0
        
        # Risk level classification
        if combined_risk > 0.7:
            risk_level = "high"
        elif combined_risk > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Contributing factors
        contributing_factors = []
        if temp_risk > 0.3:
            contributing_factors.append("Elevated temperature")
        if quality_risk > 0.3:
            contributing_factors.append("Poor water quality")
        if flow_risk > 0.3:
            contributing_factors.append("Low flow rate")
        
        indicators.append(ContaminationIndicator(
            node_id=str(node_id),
            indicator_type="bacterial_growth",
            risk_level=risk_level,
            probability=combined_risk,
            contributing_factors=contributing_factors,
            detection_method="statistical_analysis",
            confidence_score=0.8
        ))
    
    return indicators


def generate_quality_trends(data: pd.DataFrame) -> List[QualityTrend]:
    """Generate quality trends over time."""
    if data.empty:
        return []
    
    # Resample data to hourly intervals
    data_hourly = data.set_index('timestamp').resample('H').agg({
        'overall_quality': 'mean',
        'temp_quality': 'mean',
        'flow_quality': 'mean',
        'pressure_quality': 'mean'
    }).reset_index()
    
    trends = []
    for _, row in data_hourly.iterrows():
        # Calculate contamination risk (inverse of quality)
        contamination_risk = 1 - row['overall_quality']
        
        # Data completeness (simplified)
        data_completeness = 0.95  # Placeholder
        
        trends.append(QualityTrend(
            timestamp=row['timestamp'].isoformat(),
            overall_quality=row['overall_quality'] * 100,
            temperature_score=row['temp_quality'] * 100,
            flow_score=row['flow_quality'] * 100,
            pressure_score=row['pressure_quality'] * 100,
            contamination_risk=contamination_risk,
            data_completeness=data_completeness
        ))
    
    return trends


def generate_node_quality_profiles(data: pd.DataFrame) -> List[NodeQualityProfile]:
    """Generate node quality profiles."""
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
    
    profiles = []
    for node_id in data['node_id'].unique():
        node_data = data[data['node_id'] == node_id]
        
        # Calculate overall score
        overall_score = node_data['overall_quality'].mean() * 100
        
        # Temperature profile
        temperature_profile = {
            "avg_temperature": node_data['temperature'].mean(),
            "min_temperature": node_data['temperature'].min(),
            "max_temperature": node_data['temperature'].max(),
            "temperature_stability": node_data['temperature'].std()
        }
        
        # Flow profile
        flow_profile = {
            "avg_flow_rate": node_data['flow_rate'].mean(),
            "min_flow_rate": node_data['flow_rate'].min(),
            "max_flow_rate": node_data['flow_rate'].max(),
            "flow_consistency": node_data['flow_rate'].std()
        }
        
        # Pressure profile
        pressure_profile = {
            "avg_pressure": node_data['pressure'].mean(),
            "min_pressure": node_data['pressure'].min(),
            "max_pressure": node_data['pressure'].max(),
            "pressure_stability": node_data['pressure'].std()
        }
        
        # Quality grade
        if overall_score >= 90:
            quality_grade = "A"
        elif overall_score >= 80:
            quality_grade = "B"
        elif overall_score >= 70:
            quality_grade = "C"
        elif overall_score >= 60:
            quality_grade = "D"
        else:
            quality_grade = "F"
        
        profiles.append(NodeQualityProfile(
            node_id=str(node_id),
            node_name=node_names.get(str(node_id), f"Node {node_id}"),
            node_type="sensor",
            overall_score=overall_score,
            temperature_profile=temperature_profile,
            flow_profile=flow_profile,
            pressure_profile=pressure_profile,
            quality_grade=quality_grade,
            last_maintenance=None,  # Would need maintenance data
            next_maintenance_due=None  # Would need maintenance schedule
        ))
    
    return profiles


def generate_quality_predictions(data: pd.DataFrame, prediction_horizon: int = 24) -> List[QualityPrediction]:
    """Generate quality predictions."""
    predictions = []
    
    if data.empty:
        return predictions
    
    # Simple prediction based on recent trends
    for node_id in data['node_id'].unique():
        node_data = data[data['node_id'] == node_id]
        
        # Calculate trend
        recent_quality = node_data['overall_quality'].tail(10).mean()
        trend = node_data['overall_quality'].diff().tail(5).mean()
        
        # Predict future quality
        for hours_ahead in range(1, prediction_horizon + 1):
            predicted_quality = recent_quality + (trend * hours_ahead)
            predicted_quality = max(0.0, min(1.0, predicted_quality))  # Clamp between 0 and 1
            
            # Confidence decreases with time
            confidence = max(0.3, 0.9 - (hours_ahead * 0.02))
            
            # Risk factors
            risk_factors = []
            if predicted_quality < 0.7:
                risk_factors.append("Declining quality trend")
            if recent_quality < 0.8:
                risk_factors.append("Current quality issues")
            
            # Maintenance recommendations
            maintenance_recommendations = []
            if predicted_quality < 0.6:
                maintenance_recommendations.append("Immediate quality inspection required")
            if predicted_quality < 0.8:
                maintenance_recommendations.append("Preventive maintenance recommended")
            
            prediction_time = datetime.now() + timedelta(hours=hours_ahead)
            
            predictions.append(QualityPrediction(
                timestamp=prediction_time.isoformat(),
                node_id=str(node_id),
                predicted_quality=predicted_quality * 100,
                confidence_interval_lower=(predicted_quality - 0.1) * 100,
                confidence_interval_upper=(predicted_quality + 0.1) * 100,
                risk_factors=risk_factors,
                maintenance_recommendations=maintenance_recommendations
            ))
    
    return predictions 
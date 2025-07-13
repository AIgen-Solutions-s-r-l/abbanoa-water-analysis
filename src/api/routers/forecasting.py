"""
Advanced Forecasting API Router.

This router provides comprehensive endpoints for advanced forecasting and prediction,
replicating all functionality from the Streamlit forecast tab.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Query, HTTPException
import numpy as np
import pandas as pd

from src.schemas.api.forecasting import (
    ForecastResponse,
    ForecastPoint,
    NetworkForecast,
    ForecastComparison,
    ForecastPerformance,
    ForecastCalibration,
    ForecastExplanation,
    ForecastModel,
    ForecastScenario,
    ForecastValidation,
    AnomalyForecast,
    ForecastAlert,
    ErrorResponse
)
from src.infrastructure.data.hybrid_data_service import get_hybrid_data_service
from src.api.services.forecasting_service import (
    get_forecasting_data,
    generate_forecast_points,
    generate_seasonal_patterns,
    generate_forecast_scenarios,
    generate_forecast_validation,
    generate_anomaly_forecasts,
    generate_forecast_alerts,
    generate_forecast_explanations,
    calculate_forecast_performance,
    calibrate_forecast_model,
    generate_network_forecast
)

router = APIRouter(prefix="/api/v1/forecast", tags=["forecasting"])


@router.get("/node/{node_id}", response_model=ForecastResponse)
async def get_node_forecast(
    node_id: str,
    metric_type: str = Query("flow_rate", description="Metric to forecast: flow_rate, pressure, temperature"),
    forecast_horizon: str = Query("24h", description="Forecast horizon: 1h, 6h, 12h, 24h, 7d, 30d"),
    include_scenarios: bool = Query(True, description="Include forecast scenarios"),
    include_anomalies: bool = Query(True, description="Include anomaly forecasts"),
    include_alerts: bool = Query(True, description="Include forecast alerts"),
    model_type: str = Query("auto", description="Model type: auto, arima, lstm, prophet")
):
    """
    Get comprehensive forecast for a specific node.
    
    This endpoint provides detailed forecasting including multiple scenarios,
    anomaly detection, and performance metrics.
    """
    try:
        # Get hybrid data service
        hybrid_service = await get_hybrid_data_service()
        
        # Parse forecast horizon
        horizon_hours = _parse_forecast_horizon(forecast_horizon)
        
        # Get historical data for forecasting
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)  # 30 days of historical data
        
        historical_data = await get_forecasting_data(
            hybrid_service, start_time, end_time, [node_id], metric_type
        )
        
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail="No historical data found for forecasting")
        
        # Generate forecast points
        forecast_points = await generate_forecast_points(
            historical_data, node_id, metric_type, horizon_hours, model_type
        )
        
        # Generate seasonal patterns
        seasonal_patterns = generate_seasonal_patterns(historical_data, metric_type)
        
        # Get model information
        model_info = _get_model_info(model_type, historical_data)
        
        # Generate scenarios if requested
        scenarios = []
        if include_scenarios:
            scenarios = generate_forecast_scenarios(historical_data, forecast_points, metric_type)
        
        # Generate validation metrics
        validation_metrics = generate_forecast_validation(historical_data, model_type)
        
        # Generate anomaly forecasts if requested
        anomaly_forecasts = []
        if include_anomalies:
            anomaly_forecasts = generate_anomaly_forecasts(historical_data, forecast_points)
        
        # Generate forecast alerts if requested
        alerts = []
        if include_alerts:
            alerts = generate_forecast_alerts(forecast_points, historical_data, metric_type)
        
        # Generate influencing factors
        influencing_factors = _generate_influencing_factors(historical_data, metric_type)
        
        # Get node name
        node_name = _get_node_name(node_id)
        
        return ForecastResponse(
            node_id=node_id,
            node_name=node_name,
            metric_type=metric_type,
            forecast_horizon=forecast_horizon,
            forecast_points=forecast_points,
            seasonal_patterns=seasonal_patterns,
            model_info=model_info,
            scenarios=scenarios,
            validation_metrics=validation_metrics,
            anomaly_forecasts=anomaly_forecasts,
            alerts=alerts,
            influencing_factors=influencing_factors,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network", response_model=NetworkForecast)
async def get_network_forecast(
    metric_type: str = Query("flow_rate", description="Metric to forecast: flow_rate, pressure, temperature"),
    forecast_horizon: str = Query("24h", description="Forecast horizon: 1h, 6h, 12h, 24h, 7d, 30d"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    include_correlation: bool = Query(True, description="Include node correlation analysis"),
    model_type: str = Query("auto", description="Model type: auto, arima, lstm, prophet")
):
    """
    Get network-wide forecast combining all nodes.
    
    This endpoint provides system-wide forecasting with node correlation analysis
    and capacity utilization predictions.
    """
    try:
        # Get hybrid data service
        hybrid_service = await get_hybrid_data_service()
        
        # Parse forecast horizon
        horizon_hours = _parse_forecast_horizon(forecast_horizon)
        
        # Get historical data for all nodes
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        historical_data = await get_forecasting_data(
            hybrid_service, start_time, end_time, selected_nodes, metric_type
        )
        
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail="No historical data found for network forecasting")
        
        # Generate network forecast
        network_forecast = await generate_network_forecast(
            historical_data, metric_type, horizon_hours, model_type
        )
        
        # Generate individual node forecasts
        node_forecasts = []
        for node_id in historical_data['node_id'].unique():
            node_data = historical_data[historical_data['node_id'] == node_id]
            if not node_data.empty:
                try:
                    forecast_points = await generate_forecast_points(
                        node_data, str(node_id), metric_type, horizon_hours, model_type
                    )
                    seasonal_patterns = generate_seasonal_patterns(node_data, metric_type)
                    model_info = _get_model_info(model_type, node_data)
                    
                    node_forecast = ForecastResponse(
                        node_id=str(node_id),
                        node_name=_get_node_name(str(node_id)),
                        metric_type=metric_type,
                        forecast_horizon=forecast_horizon,
                        forecast_points=forecast_points,
                        seasonal_patterns=seasonal_patterns,
                        model_info=model_info,
                        scenarios=[],
                        validation_metrics=generate_forecast_validation(node_data, model_type),
                        anomaly_forecasts=[],
                        alerts=[],
                        influencing_factors=[],
                        generated_at=datetime.now().isoformat()
                    )
                    node_forecasts.append(node_forecast)
                except Exception as e:
                    print(f"Error generating forecast for node {node_id}: {e}")
                    continue
        
        # Generate correlation matrix if requested
        correlation_matrix = {}
        if include_correlation:
            correlation_matrix = _calculate_node_correlation(historical_data)
        
        # Generate system risks
        system_risks = _identify_system_risks(historical_data, network_forecast)
        
        # Calculate capacity utilization
        capacity_utilization = _calculate_capacity_utilization(network_forecast, historical_data)
        
        return NetworkForecast(
            metric_type=metric_type,
            forecast_horizon=forecast_horizon,
            network_forecast=network_forecast,
            node_forecasts=node_forecasts,
            correlation_matrix=correlation_matrix,
            system_risks=system_risks,
            capacity_utilization=capacity_utilization
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison/{node_id}", response_model=ForecastComparison)
async def get_forecast_comparison(
    node_id: str,
    metric_type: str = Query("flow_rate", description="Metric to compare"),
    forecast_horizon: str = Query("24h", description="Forecast horizon"),
    model_type: str = Query("auto", description="Model type")
):
    """
    Compare current forecast with previous forecast for accuracy assessment.
    """
    try:
        hybrid_service = await get_hybrid_data_service()
        horizon_hours = _parse_forecast_horizon(forecast_horizon)
        
        # Get data for current forecast
        current_end = datetime.now()
        current_start = current_end - timedelta(days=30)
        
        current_data = await get_forecasting_data(
            hybrid_service, current_start, current_end, [node_id], metric_type
        )
        
        # Get data for previous forecast (offset by forecast horizon)
        previous_end = current_end - timedelta(hours=horizon_hours)
        previous_start = previous_end - timedelta(days=30)
        
        previous_data = await get_forecasting_data(
            hybrid_service, previous_start, previous_end, [node_id], metric_type
        )
        
        if current_data is None or previous_data is None:
            raise HTTPException(status_code=404, detail="Insufficient data for comparison")
        
        # Generate forecasts
        current_forecast = await generate_forecast_points(
            current_data, node_id, metric_type, horizon_hours, model_type
        )
        
        previous_forecast = await generate_forecast_points(
            previous_data, node_id, metric_type, horizon_hours, model_type
        )
        
        # Calculate accuracy improvement
        accuracy_improvement = _calculate_accuracy_improvement(
            current_forecast, previous_forecast, current_data
        )
        
        # Identify key changes
        key_changes = _identify_forecast_changes(current_forecast, previous_forecast)
        
        # Determine revision reason
        revision_reason = _determine_revision_reason(key_changes, accuracy_improvement)
        
        return ForecastComparison(
            metric_type=metric_type,
            current_forecast=current_forecast,
            previous_forecast=previous_forecast,
            accuracy_improvement=accuracy_improvement,
            key_changes=key_changes,
            revision_reason=revision_reason
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{node_id}", response_model=ForecastPerformance)
async def get_forecast_performance(
    node_id: str,
    metric_type: str = Query("flow_rate", description="Metric to evaluate"),
    evaluation_period: str = Query("7d", description="Evaluation period"),
    model_type: str = Query("auto", description="Model type")
):
    """
    Get forecast performance metrics and benchmarks.
    """
    try:
        hybrid_service = await get_hybrid_data_service()
        
        # Parse evaluation period
        period_hours = _parse_forecast_horizon(evaluation_period)
        
        # Get historical data
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=period_hours)
        
        historical_data = await get_forecasting_data(
            hybrid_service, start_time, end_time, [node_id], metric_type
        )
        
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail="No data found for performance evaluation")
        
        # Calculate performance metrics
        performance = calculate_forecast_performance(
            historical_data, node_id, metric_type, model_type
        )
        
        return performance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calibration/{node_id}", response_model=ForecastCalibration)
async def get_forecast_calibration(
    node_id: str,
    metric_type: str = Query("flow_rate", description="Metric to calibrate"),
    model_type: str = Query("auto", description="Model type")
):
    """
    Get forecast calibration data for reliability assessment.
    """
    try:
        hybrid_service = await get_hybrid_data_service()
        
        # Get historical data for calibration
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        historical_data = await get_forecasting_data(
            hybrid_service, start_time, end_time, [node_id], metric_type
        )
        
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail="No data found for calibration")
        
        # Generate calibration data
        calibration = calibrate_forecast_model(
            historical_data, node_id, metric_type, model_type
        )
        
        return calibration
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explanation/{node_id}", response_model=ForecastExplanation)
async def get_forecast_explanation(
    node_id: str,
    metric_type: str = Query("flow_rate", description="Metric to explain"),
    model_type: str = Query("auto", description="Model type")
):
    """
    Get forecast explanation and interpretability data.
    """
    try:
        hybrid_service = await get_hybrid_data_service()
        
        # Get historical data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        historical_data = await get_forecasting_data(
            hybrid_service, start_time, end_time, [node_id], metric_type
        )
        
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail="No data found for explanation")
        
        # Generate explanation
        explanation = generate_forecast_explanations(
            historical_data, node_id, metric_type, model_type
        )
        
        return explanation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomaly-forecast/{node_id}", response_model=List[AnomalyForecast])
async def get_anomaly_forecast(
    node_id: str,
    forecast_horizon: str = Query("24h", description="Forecast horizon"),
    confidence_threshold: float = Query(0.7, description="Confidence threshold for anomaly detection")
):
    """
    Get anomaly forecasts for a specific node.
    """
    try:
        hybrid_service = await get_hybrid_data_service()
        horizon_hours = _parse_forecast_horizon(forecast_horizon)
        
        # Get historical data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        historical_data = await get_forecasting_data(
            hybrid_service, start_time, end_time, [node_id], "flow_rate"
        )
        
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail="No data found for anomaly forecasting")
        
        # Generate forecast points for anomaly detection
        forecast_points = await generate_forecast_points(
            historical_data, node_id, "flow_rate", horizon_hours, "auto"
        )
        
        # Generate anomaly forecasts
        anomaly_forecasts = generate_anomaly_forecasts(
            historical_data, forecast_points, confidence_threshold
        )
        
        return anomaly_forecasts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _parse_forecast_horizon(horizon: str) -> int:
    """Parse forecast horizon string to hours."""
    horizon_mappings = {
        "1h": 1,
        "6h": 6,
        "12h": 12,
        "24h": 24,
        "7d": 168,
        "30d": 720
    }
    
    if horizon not in horizon_mappings:
        raise HTTPException(status_code=400, detail=f"Invalid forecast horizon: {horizon}")
    
    return horizon_mappings[horizon]


def _get_node_name(node_id: str) -> str:
    """Get node display name."""
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
    return node_names.get(node_id, f"Node {node_id}")


def _get_model_info(model_type: str, data: pd.DataFrame) -> ForecastModel:
    """Get model information."""
    # Calculate basic accuracy metrics
    values = data['value'].values if 'value' in data.columns else data.iloc[:, -1].values
    
    # Simple accuracy calculation
    mae = np.mean(np.abs(np.diff(values)))
    mse = np.mean(np.square(np.diff(values)))
    
    return ForecastModel(
        model_name=f"{model_type.upper()}_Model",
        model_type=model_type,
        training_period=f"{len(data)} data points",
        accuracy_metrics={
            "mae": mae,
            "mse": mse,
            "rmse": np.sqrt(mse)
        },
        parameters={
            "auto_selected": True,
            "seasonality": "auto",
            "trend": "auto"
        },
        last_updated=datetime.now().isoformat()
    )


def _generate_influencing_factors(data: pd.DataFrame, metric_type: str) -> List[Dict[str, Any]]:
    """Generate influencing factors for the forecast."""
    factors = []
    
    # Add seasonal factor
    factors.append({
        "factor_name": "Seasonal Pattern",
        "factor_type": "internal",
        "impact_score": 0.7,
        "confidence": 0.85,
        "description": "Regular seasonal variation in water demand"
    })
    
    # Add trend factor
    if len(data) > 1:
        trend = np.polyfit(range(len(data)), data.iloc[:, -1], 1)[0]
        factors.append({
            "factor_name": "Long-term Trend",
            "factor_type": "internal",
            "impact_score": abs(trend) * 0.5,
            "confidence": 0.75,
            "description": f"Long-term {'increasing' if trend > 0 else 'decreasing'} trend"
        })
    
    return factors


def _calculate_node_correlation(data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Calculate correlation matrix between nodes."""
    correlation_matrix = {}
    
    if 'node_id' in data.columns:
        # Pivot data to have nodes as columns
        pivot_data = data.pivot_table(
            index='timestamp', 
            columns='node_id', 
            values=data.columns[-1],
            aggfunc='mean'
        )
        
        # Calculate correlation
        corr = pivot_data.corr()
        
        # Convert to dictionary
        for node1 in corr.index:
            correlation_matrix[str(node1)] = {}
            for node2 in corr.columns:
                correlation_matrix[str(node1)][str(node2)] = float(corr.loc[node1, node2])
    
    return correlation_matrix


def _identify_system_risks(data: pd.DataFrame, forecast: List[ForecastPoint]) -> List[str]:
    """Identify system-wide risks based on forecast."""
    risks = []
    
    # Check for declining trends
    if len(forecast) > 1:
        trend = (forecast[-1].predicted_value - forecast[0].predicted_value) / len(forecast)
        if trend < -0.1:
            risks.append("Declining system performance trend")
    
    # Check for high variability
    forecast_values = [fp.predicted_value for fp in forecast]
    if len(forecast_values) > 1:
        cv = np.std(forecast_values) / np.mean(forecast_values)
        if cv > 0.3:
            risks.append("High forecast variability indicating instability")
    
    # Check for capacity issues
    max_forecast = max(forecast_values) if forecast_values else 0
    if max_forecast > 1000:  # Arbitrary threshold
        risks.append("Potential capacity constraints")
    
    return risks


def _calculate_capacity_utilization(forecast: List[ForecastPoint], data: pd.DataFrame) -> float:
    """Calculate predicted capacity utilization."""
    if not forecast:
        return 0.0
    
    # Simple capacity calculation
    max_forecast = max(fp.predicted_value for fp in forecast)
    historical_max = data.iloc[:, -1].max() if len(data) > 0 else 100
    
    # Assume capacity is 120% of historical max
    capacity = historical_max * 1.2
    
    return min(100.0, (max_forecast / capacity) * 100)


def _calculate_accuracy_improvement(current: List[ForecastPoint], previous: List[ForecastPoint], data: pd.DataFrame) -> float:
    """Calculate accuracy improvement percentage."""
    # Simplified accuracy calculation
    if len(current) == len(previous):
        current_accuracy = 90.0  # Placeholder
        previous_accuracy = 85.0  # Placeholder
        return ((current_accuracy - previous_accuracy) / previous_accuracy) * 100
    return 0.0


def _identify_forecast_changes(current: List[ForecastPoint], previous: List[ForecastPoint]) -> List[str]:
    """Identify key changes between forecasts."""
    changes = []
    
    if len(current) > 0 and len(previous) > 0:
        current_avg = np.mean([fp.predicted_value for fp in current])
        previous_avg = np.mean([fp.predicted_value for fp in previous])
        
        change_pct = ((current_avg - previous_avg) / previous_avg) * 100
        
        if abs(change_pct) > 5:
            changes.append(f"Average forecast value changed by {change_pct:.1f}%")
    
    return changes


def _determine_revision_reason(changes: List[str], accuracy_improvement: float) -> str:
    """Determine reason for forecast revision."""
    if accuracy_improvement > 5:
        return "Improved model accuracy with new data"
    elif len(changes) > 0:
        return "Significant changes in underlying patterns"
    else:
        return "Routine forecast update" 
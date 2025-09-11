"""
Unit tests for prediction service with Simple ML models.
Following TDD approach - RED phase.
"""

import pytest
from datetime import datetime, timedelta
import numpy as np
from unittest.mock import Mock, patch

from src.application.prediction_service import PredictionService
from src.application.models.time_series_simple import (
    MovingAveragePredictor,
    SeasonalDecomposer,
    SimpleAnomalyDetector
)


class TestPredictionService:
    """Test suite for PredictionService following AAA pattern."""
    
    def test_prediction_service_initializes(self):
        """Test that PredictionService can be instantiated."""
        # Arrange & Act
        service = PredictionService()
        
        # Assert
        assert service is not None
        assert hasattr(service, 'predict_peak_demand')
        assert hasattr(service, 'optimize_energy_cost')
        assert hasattr(service, 'predict_maintenance')
        assert hasattr(service, 'predict_water_loss')
    
    def test_predict_peak_demand_returns_forecast(self):
        """Test peak demand prediction returns 7-day forecast."""
        # Arrange
        service = PredictionService()
        historical_data = np.random.randn(30*24) * 10 + 100  # 30 days hourly
        
        # Act
        forecast = service.predict_peak_demand(historical_data, days=7)
        
        # Assert
        assert isinstance(forecast, dict)
        assert 'predictions' in forecast
        assert len(forecast['predictions']) == 7 * 24  # 7 days hourly
        assert 'confidence_interval' in forecast
        assert 'accuracy_score' in forecast
        assert forecast['accuracy_score'] > 0.6  # Better than random
    
    def test_optimize_energy_cost_with_tariffs(self):
        """Test energy optimization considers real tariffs."""
        # Arrange
        service = PredictionService()
        demand_forecast = np.array([100, 120, 80, 90] * 6)  # 24 hours
        tariffs = {
            'peak': [8, 9, 10, 11, 17, 18, 19, 20],  # Peak hours
            'off_peak': list(range(0, 8)) + list(range(21, 24)),
            'rates': {'peak': 0.25, 'off_peak': 0.10}
        }
        
        # Act
        optimization = service.optimize_energy_cost(demand_forecast, tariffs)
        
        # Assert
        assert 'schedule' in optimization
        assert 'estimated_savings' in optimization
        assert 'baseline_cost' in optimization
        assert 'optimized_cost' in optimization
        assert optimization['estimated_savings'] > 0
        assert optimization['optimized_cost'] < optimization['baseline_cost']
    
    def test_predict_maintenance_with_sensor_trends(self):
        """Test maintenance prediction based on sensor degradation."""
        # Arrange
        service = PredictionService()
        sensor_history = {
            'pressure': np.linspace(3.5, 2.8, 100),  # Degrading
            'vibration': np.random.randn(100) * 0.1 + np.linspace(0, 0.5, 100),
            'temperature': np.random.randn(100) * 2 + 25,
            'equipment_age_days': 730
        }
        
        # Act
        prediction = service.predict_maintenance(sensor_history)
        
        # Assert
        assert 'risk_score' in prediction
        assert 'days_to_maintenance' in prediction
        assert 'confidence' in prediction
        assert 'failure_probability' in prediction
        assert prediction['risk_score'] in ['low', 'medium', 'high', 'critical']
        assert 0 <= prediction['failure_probability'] <= 1
    
    def test_predict_water_loss_with_flow_balance(self):
        """Test water loss prediction using flow balance analysis."""
        # Arrange
        service = PredictionService()
        flow_data = {
            'flow_in': np.array([100, 102, 98, 101, 99]),
            'flow_out': np.array([95, 96, 91, 94, 92]),  # ~5-7% loss
            'pressure': np.array([3.2, 3.1, 2.9, 3.0, 2.95]),
            'night_flow': np.array([20, 22, 25, 23, 24])  # Increasing night flow
        }
        
        # Act
        prediction = service.predict_water_loss(flow_data)
        
        # Assert
        assert 'current_loss_percentage' in prediction
        assert 'predicted_loss_trend' in prediction
        assert 'leak_probability' in prediction
        assert 'recommended_actions' in prediction
        assert prediction['current_loss_percentage'] > 0
        assert 0 <= prediction['leak_probability'] <= 1


class TestMovingAveragePredictor:
    """Test suite for MovingAveragePredictor."""
    
    def test_moving_average_with_weights(self):
        """Test weighted moving average calculation."""
        # Arrange
        predictor = MovingAveragePredictor(window_size=7)
        data = np.array([100, 105, 110, 108, 112, 115, 120])
        
        # Act
        prediction = predictor.predict(data, steps=1)
        
        # Assert
        assert isinstance(prediction, np.ndarray)
        assert len(prediction) == 1
        assert 110 < prediction[0] < 120  # Should be weighted toward recent
    
    def test_moving_average_multi_step_forecast(self):
        """Test multi-step ahead forecasting."""
        # Arrange
        predictor = MovingAveragePredictor(window_size=7)
        data = np.random.randn(30) * 10 + 100
        
        # Act
        forecast = predictor.predict(data, steps=7)
        
        # Assert
        assert len(forecast) == 7
        assert all(80 < f < 120 for f in forecast)  # Reasonable range


class TestSeasonalDecomposer:
    """Test suite for SeasonalDecomposer."""
    
    def test_seasonal_decomposition_daily_pattern(self):
        """Test extraction of daily seasonal patterns."""
        # Arrange
        decomposer = SeasonalDecomposer(period=24)  # Daily pattern
        # Create data with clear daily pattern
        t = np.arange(7*24)  # 7 days hourly
        trend = t * 0.1
        seasonal = 10 * np.sin(2 * np.pi * t / 24)
        noise = np.random.randn(len(t)) * 2
        data = 100 + trend + seasonal + noise
        
        # Act
        components = decomposer.decompose(data)
        
        # Assert
        assert 'trend' in components
        assert 'seasonal' in components
        assert 'residual' in components
        assert len(components['seasonal']) == len(data)
        assert np.std(components['seasonal']) > 5  # Has seasonality
    
    def test_seasonal_adjustment_factors(self):
        """Test calculation of seasonal adjustment factors."""
        # Arrange
        decomposer = SeasonalDecomposer(period=24)
        data = np.random.randn(30*24) * 10 + 100
        
        # Act
        factors = decomposer.get_seasonal_factors(data)
        
        # Assert
        assert len(factors) == 24  # One per hour
        assert all(0.5 < f < 1.5 for f in factors)  # Reasonable range


class TestSimpleAnomalyDetector:
    """Test suite for SimpleAnomalyDetector."""
    
    def test_anomaly_detection_threshold_based(self):
        """Test threshold-based anomaly detection."""
        # Arrange
        detector = SimpleAnomalyDetector(threshold_std=2.0)
        normal_data = np.random.randn(100) * 10 + 100
        # Add anomalies
        anomaly_data = normal_data.copy()
        anomaly_data[20] = 150  # Spike
        anomaly_data[50] = 40   # Drop
        
        # Act
        anomalies = detector.detect(anomaly_data)
        
        # Assert
        assert 'anomaly_indices' in anomalies
        assert 'anomaly_scores' in anomalies
        assert 20 in anomalies['anomaly_indices']
        assert 50 in anomalies['anomaly_indices']
        assert len(anomalies['anomaly_indices']) >= 2
    
    def test_anomaly_detection_with_trend(self):
        """Test anomaly detection with trending data."""
        # Arrange
        detector = SimpleAnomalyDetector(threshold_std=2.0)
        # Data with upward trend
        t = np.arange(100)
        data = 100 + t * 0.5 + np.random.randn(100) * 5
        data[80] = 200  # Clear anomaly
        
        # Act
        anomalies = detector.detect(data, detrend=True)
        
        # Assert
        assert 80 in anomalies['anomaly_indices']
        assert anomalies['anomaly_scores'][80] > 2.0
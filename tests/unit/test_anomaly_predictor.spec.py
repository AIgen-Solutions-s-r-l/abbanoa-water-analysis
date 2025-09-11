"""Unit tests for anomaly prediction system"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.application.services.anomaly_predictor import (
    AnomalyPredictor,
    AnomalyPrediction,
    PredictionConfidence
)


class TestAnomalyPredictor:
    """Test suite for AnomalyPredictor class"""

    @pytest.fixture
    def predictor(self):
        """Create AnomalyPredictor instance"""
        return AnomalyPredictor()

    @pytest.fixture
    def historical_data(self):
        """Generate sample historical anomaly data"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='H')
        return pd.DataFrame({
            'timestamp': dates,
            'node_id': 'NODE_001',
            'pressure': np.random.normal(5.0, 0.5, 100),
            'flow_rate': np.random.normal(100, 10, 100),
            'anomaly_occurred': [False] * 95 + [True] * 5
        })

    def test_predictor_initialization(self, predictor):
        """Test predictor initializes with correct default parameters"""
        # Arrange & Act
        # Assert
        assert predictor.model is not None
        assert predictor.lookback_hours == 24
        assert predictor.prediction_horizon == 6

    def test_preprocess_sensor_data(self, predictor, historical_data):
        """Test sensor data preprocessing for prediction"""
        # Arrange
        # Act
        processed = predictor.preprocess_data(historical_data)
        
        # Assert
        assert 'pressure_rolling_mean' in processed.columns
        assert 'pressure_rolling_std' in processed.columns
        assert 'hour_of_day' in processed.columns
        assert 'day_of_week' in processed.columns
        assert len(processed) == len(historical_data)

    def test_extract_anomaly_patterns(self, predictor, historical_data):
        """Test extraction of pre-anomaly patterns from historical data"""
        # Arrange
        # Act
        patterns = predictor.extract_patterns(historical_data)
        
        # Assert
        assert 'pressure_trend' in patterns
        assert 'flow_rate_volatility' in patterns
        assert patterns['anomaly_risk_score'] >= 0
        assert patterns['anomaly_risk_score'] <= 1

    def test_predict_single_node(self, predictor, historical_data):
        """Test anomaly prediction for single node"""
        # Arrange
        predictor.train(historical_data)
        recent_data = historical_data.tail(24)
        
        # Act
        prediction = predictor.predict(
            node_id='NODE_001',
            sensor_data=recent_data
        )
        
        # Assert
        assert isinstance(prediction, AnomalyPrediction)
        assert prediction.node_id == 'NODE_001'
        assert prediction.probability >= 0 and prediction.probability <= 1
        assert prediction.predicted_time is not None
        assert prediction.confidence in [c.value for c in PredictionConfidence]

    def test_predict_multiple_nodes(self, predictor):
        """Test batch prediction for multiple nodes"""
        # Arrange
        nodes_data = {
            'NODE_001': pd.DataFrame({'pressure': [5.0] * 24, 'flow_rate': [100] * 24}),
            'NODE_002': pd.DataFrame({'pressure': [4.5] * 24, 'flow_rate': [90] * 24}),
            'NODE_003': pd.DataFrame({'pressure': [5.5] * 24, 'flow_rate': [110] * 24})
        }
        
        # Act
        predictions = predictor.predict_batch(nodes_data)
        
        # Assert
        assert len(predictions) == 3
        assert all(isinstance(p, AnomalyPrediction) for p in predictions)
        assert all(p.node_id in nodes_data.keys() for p in predictions)

    def test_high_risk_alert_generation(self, predictor):
        """Test alert generation for high-risk predictions"""
        # Arrange
        prediction = AnomalyPrediction(
            node_id='NODE_001',
            probability=0.85,
            predicted_time=datetime.now() + timedelta(hours=2),
            confidence=PredictionConfidence.HIGH,
            risk_factors=['pressure_spike', 'abnormal_flow']
        )
        
        # Act
        alert = predictor.generate_alert(prediction)
        
        # Assert
        assert alert.severity == 'HIGH'
        assert alert.time_to_event_hours <= 6
        assert 'pressure_spike' in alert.description
        assert alert.recommended_actions is not None

    def test_model_accuracy_threshold(self, predictor, historical_data):
        """Test model meets minimum accuracy requirements"""
        # Arrange
        train_data = historical_data.iloc[:80]
        test_data = historical_data.iloc[80:]
        predictor.train(train_data)
        
        # Act
        accuracy = predictor.evaluate(test_data)
        
        # Assert
        assert accuracy['precision'] >= 0.75
        assert accuracy['recall'] >= 0.70
        assert accuracy['f1_score'] >= 0.72

    def test_prediction_with_insufficient_data(self, predictor):
        """Test handling of insufficient historical data"""
        # Arrange
        insufficient_data = pd.DataFrame({
            'pressure': [5.0] * 5,  # Only 5 hours
            'flow_rate': [100] * 5
        })
        
        # Act & Assert
        with pytest.raises(ValueError, match="Insufficient data"):
            predictor.predict('NODE_001', insufficient_data)

    def test_realtime_update_capability(self, predictor):
        """Test model can be updated with new data in real-time"""
        # Arrange
        initial_data = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=100, freq='H'),
            'pressure': np.random.normal(5.0, 0.5, 100)
        })
        new_data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'pressure': [5.2]
        })
        
        # Act
        predictor.train(initial_data)
        initial_params = predictor.model.get_params()
        predictor.update(new_data)
        updated_params = predictor.model.get_params()
        
        # Assert
        assert predictor.last_update_time > predictor.training_time
        assert predictor.data_points_processed == 101
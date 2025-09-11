"""Unit tests for prediction tracking and reconciliation system"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import pandas as pd

from src.application.services.prediction_tracker import (
    PredictionTracker,
    PredictionOutcome,
    PerformanceMetrics,
    ReconciliationResult
)


class TestPredictionTracker:
    """Test suite for prediction tracking system"""
    
    @pytest.fixture
    def tracker(self):
        """Create PredictionTracker instance with mock repository"""
        mock_repo = Mock()
        return PredictionTracker(repository=mock_repo)
    
    @pytest.fixture
    def sample_prediction(self):
        """Sample prediction data"""
        return {
            'prediction_id': 1,
            'node_id': 'NODE_001',
            'probability': 0.85,
            'predicted_timestamp': datetime.now() + timedelta(hours=2),
            'confidence': 'HIGH',
            'created_at': datetime.now()
        }
    
    def test_tracker_initialization(self, tracker):
        """Test tracker initializes correctly"""
        # Assert
        assert tracker is not None
        assert tracker.repository is not None
        assert tracker.reconciliation_window_hours == 6
    
    async def test_mark_prediction_outcome(self, tracker, sample_prediction):
        """Test marking a prediction with actual outcome"""
        # Arrange
        prediction_id = sample_prediction['prediction_id']
        actual_outcome = True
        
        # Act
        result = await tracker.mark_outcome(
            prediction_id=prediction_id,
            actual_occurred=actual_outcome,
            feedback_source='automatic'
        )
        
        # Assert
        assert result.prediction_id == prediction_id
        assert result.actual_occurred == actual_outcome
        assert result.is_correct == True  # High probability + occurred = correct
        assert result.feedback_source == 'automatic'
    
    async def test_reconcile_predictions(self, tracker):
        """Test reconciliation of predictions with actual anomalies"""
        # Arrange
        mock_predictions = pd.DataFrame([
            {'prediction_id': 1, 'node_id': 'NODE_001', 'probability': 0.8, 
             'predicted_timestamp': datetime.now() - timedelta(hours=1)},
            {'prediction_id': 2, 'node_id': 'NODE_002', 'probability': 0.3,
             'predicted_timestamp': datetime.now() - timedelta(hours=2)}
        ])
        
        mock_anomalies = pd.DataFrame([
            {'node_id': 'NODE_001', 'timestamp': datetime.now() - timedelta(minutes=30)}
        ])
        
        tracker.repository.get_unreconciled_predictions = AsyncMock(return_value=mock_predictions)
        tracker.repository.get_actual_anomalies = AsyncMock(return_value=mock_anomalies)
        
        # Act
        result = await tracker.reconcile_predictions()
        
        # Assert
        assert isinstance(result, ReconciliationResult)
        assert result.total_predictions == 2
        assert result.true_positives == 1  # NODE_001 predicted and occurred
        assert result.false_positives == 0  # NODE_002 low probability, doesn't count
        assert result.reconciled_count == 2
    
    async def test_calculate_performance_metrics(self, tracker):
        """Test calculation of model performance metrics"""
        # Arrange
        days_back = 7
        
        # Mock data with various outcomes
        tracker.repository.get_prediction_outcomes = AsyncMock(return_value=pd.DataFrame([
            {'predicted': True, 'actual': True},   # True positive
            {'predicted': True, 'actual': True},   # True positive
            {'predicted': True, 'actual': False},  # False positive
            {'predicted': False, 'actual': False}, # True negative
            {'predicted': False, 'actual': True},  # False negative
        ]))
        
        # Act
        metrics = await tracker.calculate_metrics(days_back=days_back)
        
        # Assert
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.precision == 2/3  # 2 TP / (2 TP + 1 FP)
        assert metrics.recall == 2/3     # 2 TP / (2 TP + 1 FN)
        assert abs(metrics.f1_score - 0.667) < 0.01
        assert metrics.accuracy == 0.6   # (2 TP + 1 TN) / 5
    
    async def test_detect_performance_degradation(self, tracker):
        """Test detection of model performance degradation"""
        # Arrange
        # Mock recent poor performance
        tracker.calculate_metrics = AsyncMock(return_value=PerformanceMetrics(
            precision=0.5,
            recall=0.4,
            f1_score=0.44,
            accuracy=0.45
        ))
        
        # Act
        is_degraded = await tracker.check_performance_degradation(
            threshold_f1=0.7
        )
        
        # Assert
        assert is_degraded == True
        assert tracker.repository.log_alert.called
    
    async def test_feedback_loop_integration(self, tracker):
        """Test operator feedback integration"""
        # Arrange
        feedback = {
            'prediction_id': 1,
            'operator_id': 'OP001',
            'feedback': 'false_positive',
            'notes': 'Sensor malfunction, not real anomaly'
        }
        
        # Act
        result = await tracker.process_operator_feedback(feedback)
        
        # Assert
        assert result.status == 'processed'
        assert result.outcome_marked == False  # False positive
        assert result.retraining_triggered == False  # Wait for more feedback
    
    async def test_time_window_matching(self, tracker):
        """Test matching predictions with anomalies in time window"""
        # Arrange
        prediction_time = datetime.now()
        anomaly_time_match = prediction_time + timedelta(hours=1)  # Within window
        anomaly_time_no_match = prediction_time + timedelta(hours=7)  # Outside window
        
        # Act
        match1 = tracker.is_within_window(prediction_time, anomaly_time_match)
        match2 = tracker.is_within_window(prediction_time, anomaly_time_no_match)
        
        # Assert
        assert match1 == True
        assert match2 == False
    
    async def test_bulk_reconciliation(self, tracker):
        """Test bulk reconciliation of multiple nodes"""
        # Arrange
        nodes = ['NODE_001', 'NODE_002', 'NODE_003']
        
        # Act
        results = await tracker.bulk_reconcile(nodes)
        
        # Assert
        assert len(results) == 3
        assert all(isinstance(r, ReconciliationResult) for r in results)
    
    async def test_metrics_persistence(self, tracker):
        """Test saving performance metrics to database"""
        # Arrange
        metrics = PerformanceMetrics(
            precision=0.85,
            recall=0.80,
            f1_score=0.82,
            accuracy=0.83
        )
        
        # Act
        saved = await tracker.save_metrics(metrics, model_version='v1.0')
        
        # Assert
        assert saved == True
        assert tracker.repository.save_performance_metrics.called_once()
    
    async def test_cleanup_old_predictions(self, tracker):
        """Test cleanup of old prediction records"""
        # Arrange
        retention_days = 90
        
        # Act
        deleted_count = await tracker.cleanup_old_predictions(retention_days)
        
        # Assert
        assert deleted_count >= 0
        assert tracker.repository.delete_old_predictions.called_with(retention_days)
"""Service for tracking and reconciling ML predictions with actual outcomes"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class FeedbackSource(Enum):
    """Source of prediction outcome feedback"""
    AUTOMATIC = "automatic"
    OPERATOR = "operator"
    SYSTEM = "system"


@dataclass
class PredictionOutcome:
    """Represents the outcome of a prediction"""
    prediction_id: int
    actual_occurred: bool
    is_correct: bool
    feedback_source: str
    marked_at: datetime


@dataclass
class PerformanceMetrics:
    """Model performance metrics"""
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0


@dataclass
class ReconciliationResult:
    """Result of prediction reconciliation process"""
    total_predictions: int
    reconciled_count: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PredictionTracker:
    """Tracks and reconciles ML predictions with actual outcomes"""
    
    def __init__(self, repository, reconciliation_window_hours: int = 6):
        """Initialize tracker with repository and configuration
        
        Args:
            repository: Database repository for predictions
            reconciliation_window_hours: Time window for matching predictions to outcomes
        """
        self.repository = repository
        self.reconciliation_window_hours = reconciliation_window_hours
        
    async def mark_outcome(
        self,
        prediction_id: int,
        actual_occurred: bool,
        feedback_source: str = "automatic"
    ) -> PredictionOutcome:
        """Mark a prediction with its actual outcome
        
        Args:
            prediction_id: ID of the prediction
            actual_occurred: Whether the predicted event actually occurred
            feedback_source: Source of the feedback
            
        Returns:
            PredictionOutcome with results
        """
        # Get original prediction
        prediction = await self.repository.get_prediction(prediction_id)
        
        if not prediction:
            raise ValueError(f"Prediction {prediction_id} not found")
        
        # Determine if prediction was correct
        # High probability (>0.7) + occurred = correct
        # Low probability (<0.3) + not occurred = correct
        is_correct = False
        if prediction['probability'] > 0.7 and actual_occurred:
            is_correct = True
        elif prediction['probability'] < 0.3 and not actual_occurred:
            is_correct = True
        
        # Update database
        await self.repository.update_prediction_outcome(
            prediction_id=prediction_id,
            actual_occurred=actual_occurred,
            feedback_source=feedback_source
        )
        
        return PredictionOutcome(
            prediction_id=prediction_id,
            actual_occurred=actual_occurred,
            is_correct=is_correct,
            feedback_source=feedback_source,
            marked_at=datetime.now()
        )
    
    async def reconcile_predictions(self) -> ReconciliationResult:
        """Reconcile predictions with actual anomalies
        
        Returns:
            ReconciliationResult with statistics
        """
        # Get unreconciled predictions
        predictions = await self.repository.get_unreconciled_predictions()
        
        if predictions.empty:
            logger.info("No predictions to reconcile")
            return ReconciliationResult(
                total_predictions=0,
                reconciled_count=0,
                true_positives=0,
                false_positives=0,
                false_negatives=0,
                true_negatives=0
            )
        
        # Get actual anomalies for the time period
        min_time = predictions['predicted_timestamp'].min() - timedelta(hours=self.reconciliation_window_hours)
        max_time = predictions['predicted_timestamp'].max() + timedelta(hours=self.reconciliation_window_hours)
        
        anomalies = await self.repository.get_actual_anomalies(
            start_time=min_time,
            end_time=max_time
        )
        
        # Match predictions with anomalies
        tp, fp, fn, tn = 0, 0, 0, 0
        reconciled = 0
        
        for _, pred in predictions.iterrows():
            node_id = pred['node_id']
            pred_time = pred['predicted_timestamp']
            probability = pred['probability']
            
            # Find matching anomaly within time window
            node_anomalies = anomalies[anomalies['node_id'] == node_id]
            
            matched = False
            for _, anomaly in node_anomalies.iterrows():
                if self.is_within_window(pred_time, anomaly['timestamp']):
                    matched = True
                    break
            
            # Classify outcome
            if probability > 0.7:  # Predicted positive
                if matched:
                    tp += 1  # True positive
                    await self.mark_outcome(pred['prediction_id'], True, "automatic")
                else:
                    fp += 1  # False positive
                    await self.mark_outcome(pred['prediction_id'], False, "automatic")
            else:  # Predicted negative (low probability)
                if matched:
                    fn += 1  # False negative
                else:
                    tn += 1  # True negative
                    
            reconciled += 1
        
        return ReconciliationResult(
            total_predictions=len(predictions),
            reconciled_count=reconciled,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            true_negatives=tn
        )
    
    async def calculate_metrics(self, days_back: int = 7) -> PerformanceMetrics:
        """Calculate performance metrics for recent predictions
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            PerformanceMetrics with calculated values
        """
        # Get prediction outcomes
        outcomes = await self.repository.get_prediction_outcomes(days_back)
        
        if outcomes.empty:
            return PerformanceMetrics(
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                accuracy=0.0
            )
        
        # Calculate confusion matrix
        tp = len(outcomes[(outcomes['predicted'] == True) & (outcomes['actual'] == True)])
        fp = len(outcomes[(outcomes['predicted'] == True) & (outcomes['actual'] == False)])
        tn = len(outcomes[(outcomes['predicted'] == False) & (outcomes['actual'] == False)])
        fn = len(outcomes[(outcomes['predicted'] == False) & (outcomes['actual'] == True)])
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / len(outcomes) if len(outcomes) > 0 else 0
        
        return PerformanceMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            accuracy=accuracy,
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn
        )
    
    async def check_performance_degradation(
        self,
        threshold_f1: float = 0.7,
        days_back: int = 7
    ) -> bool:
        """Check if model performance has degraded below threshold
        
        Args:
            threshold_f1: Minimum acceptable F1 score
            days_back: Days to analyze
            
        Returns:
            True if performance is degraded
        """
        metrics = await self.calculate_metrics(days_back)
        
        if metrics.f1_score < threshold_f1:
            logger.warning(f"Model performance degraded: F1={metrics.f1_score:.2f} < {threshold_f1}")
            
            # Log alert
            if hasattr(self.repository, 'log_alert'):
                await self.repository.log_alert(
                    alert_type='performance_degradation',
                    details={
                        'f1_score': metrics.f1_score,
                        'threshold': threshold_f1,
                        'precision': metrics.precision,
                        'recall': metrics.recall
                    }
                )
            
            return True
        
        return False
    
    async def process_operator_feedback(self, feedback: Dict) -> Dict:
        """Process feedback from operators
        
        Args:
            feedback: Feedback data from operator
            
        Returns:
            Processing result
        """
        prediction_id = feedback['prediction_id']
        feedback_type = feedback['feedback']
        
        # Map feedback to outcome
        if feedback_type == 'false_positive':
            actual_occurred = False
        elif feedback_type == 'false_negative':
            actual_occurred = True
        else:
            actual_occurred = feedback.get('actual_occurred', False)
        
        # Mark outcome
        outcome = await self.mark_outcome(
            prediction_id=prediction_id,
            actual_occurred=actual_occurred,
            feedback_source='operator'
        )
        
        # Store detailed feedback
        if hasattr(self.repository, 'save_operator_feedback'):
            await self.repository.save_operator_feedback(feedback)
        
        # Check if retraining needed
        retraining_triggered = False
        feedback_count = await self.repository.get_feedback_count(days=1) if hasattr(self.repository, 'get_feedback_count') else 0
        
        if feedback_count > 10:  # Threshold for retraining
            retraining_triggered = True
            logger.info("Retraining triggered due to operator feedback volume")
        
        return {
            'status': 'processed',
            'outcome_marked': actual_occurred,
            'retraining_triggered': retraining_triggered,
            'prediction_id': prediction_id
        }
    
    def is_within_window(
        self,
        prediction_time: datetime,
        actual_time: datetime
    ) -> bool:
        """Check if actual event is within prediction window
        
        Args:
            prediction_time: Time of prediction
            actual_time: Time of actual event
            
        Returns:
            True if within window
        """
        time_diff = abs((actual_time - prediction_time).total_seconds() / 3600)
        return time_diff <= self.reconciliation_window_hours
    
    async def bulk_reconcile(self, nodes: List[str]) -> List[ReconciliationResult]:
        """Reconcile predictions for multiple nodes
        
        Args:
            nodes: List of node IDs
            
        Returns:
            List of reconciliation results
        """
        results = []
        
        for node_id in nodes:
            # Get predictions for node
            predictions = await self.repository.get_node_predictions(node_id)
            
            if predictions.empty:
                continue
            
            # Get anomalies for node
            anomalies = await self.repository.get_node_anomalies(node_id)
            
            # Reconcile
            tp, fp, fn, tn = 0, 0, 0, 0
            
            for _, pred in predictions.iterrows():
                matched = False
                for _, anomaly in anomalies.iterrows():
                    if self.is_within_window(pred['predicted_timestamp'], anomaly['timestamp']):
                        matched = True
                        break
                
                if pred['probability'] > 0.7:
                    if matched:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if matched:
                        fn += 1
                    else:
                        tn += 1
            
            results.append(ReconciliationResult(
                total_predictions=len(predictions),
                reconciled_count=len(predictions),
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                true_negatives=tn
            ))
        
        return results
    
    async def save_metrics(
        self,
        metrics: PerformanceMetrics,
        model_version: str
    ) -> bool:
        """Save performance metrics to database
        
        Args:
            metrics: Calculated metrics
            model_version: Version of the model
            
        Returns:
            True if saved successfully
        """
        try:
            if hasattr(self.repository, 'save_performance_metrics'):
                await self.repository.save_performance_metrics(
                    metrics=metrics,
                    model_version=model_version,
                    timestamp=datetime.now()
                )
            return True
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            return False
    
    async def cleanup_old_predictions(self, retention_days: int = 90) -> int:
        """Clean up old prediction records
        
        Args:
            retention_days: Days to retain predictions
            
        Returns:
            Number of records deleted
        """
        if hasattr(self.repository, 'delete_old_predictions'):
            deleted = await self.repository.delete_old_predictions(retention_days)
            logger.info(f"Deleted {deleted} old predictions")
            return deleted
        return 0
"""Custom exceptions for prediction tracking system"""

from typing import Optional, Any


class PredictionTrackingError(Exception):
    """Base exception for prediction tracking system"""
    pass


class PredictionNotFoundError(PredictionTrackingError):
    """Raised when a prediction cannot be found"""
    
    def __init__(self, prediction_id: int):
        self.prediction_id = prediction_id
        super().__init__(f"Prediction {prediction_id} not found")


class InvalidFeedbackError(PredictionTrackingError):
    """Raised when invalid feedback is provided"""
    
    def __init__(self, message: str, feedback_data: Optional[Any] = None):
        self.feedback_data = feedback_data
        super().__init__(f"Invalid feedback: {message}")


class ReconciliationError(PredictionTrackingError):
    """Raised when reconciliation process fails"""
    
    def __init__(self, message: str, node_id: Optional[str] = None):
        self.node_id = node_id
        super().__init__(f"Reconciliation failed: {message}")


class MetricsCalculationError(PredictionTrackingError):
    """Raised when metrics calculation fails"""
    
    def __init__(self, message: str, period: Optional[str] = None):
        self.period = period
        super().__init__(f"Metrics calculation failed: {message}")


class DatabaseTransactionError(PredictionTrackingError):
    """Raised when database transaction fails"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        self.operation = operation
        super().__init__(f"Database transaction failed: {message}")


class ValidationError(PredictionTrackingError):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, value: Any, constraint: str):
        self.field = field
        self.value = value
        self.constraint = constraint
        super().__init__(f"Validation failed for {field}='{value}': {constraint}")


class PerformanceDegradationError(PredictionTrackingError):
    """Raised when model performance degrades below threshold"""
    
    def __init__(self, current_score: float, threshold: float, metric: str = "f1_score"):
        self.current_score = current_score
        self.threshold = threshold
        self.metric = metric
        super().__init__(
            f"Performance degraded: {metric}={current_score:.3f} < {threshold:.3f}"
        )
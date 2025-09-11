"""API endpoints for prediction tracking and performance metrics"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from src.application.services.prediction_tracker import (
    PredictionTracker,
    PerformanceMetrics,
    ReconciliationResult
)
from src.infrastructure.repositories.tracking_repository_extension import (
    TrackingRepositoryExtension
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tracking",
    tags=["Prediction Tracking"],
    responses={404: {"description": "Not found"}},
)


class FeedbackRequest(BaseModel):
    """Operator feedback for a prediction"""
    prediction_id: int = Field(..., description="Prediction ID")
    operator_id: str = Field(..., description="Operator identifier")
    feedback: str = Field(..., description="Feedback type: false_positive, false_negative, correct")
    notes: Optional[str] = Field(None, description="Additional notes")


class OutcomeRequest(BaseModel):
    """Mark prediction outcome"""
    prediction_id: int
    actual_occurred: bool
    feedback_source: str = "automatic"


class MetricsResponse(BaseModel):
    """Performance metrics response"""
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    calculated_at: datetime


class ReconciliationResponse(BaseModel):
    """Reconciliation result response"""
    total_predictions: int
    reconciled_count: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    timestamp: datetime


@router.post("/feedback", response_model=Dict)
async def submit_operator_feedback(request: FeedbackRequest, req: Request) -> Dict:
    """Submit operator feedback for a prediction
    
    Args:
        request: Feedback data
        req: FastAPI request with database pool
        
    Returns:
        Processing result
    """
    try:
        # Get database pool
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Initialize tracker
        repo = TrackingRepositoryExtension(pool)
        tracker = PredictionTracker(repository=repo)
        
        # Process feedback
        result = await tracker.process_operator_feedback(request.dict())
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to process feedback")


@router.post("/outcome", response_model=Dict)
async def mark_prediction_outcome(request: OutcomeRequest, req: Request) -> Dict:
    """Mark the actual outcome of a prediction
    
    Args:
        request: Outcome data
        req: FastAPI request
        
    Returns:
        Update confirmation
    """
    try:
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        repo = TrackingRepositoryExtension(pool)
        tracker = PredictionTracker(repository=repo)
        
        outcome = await tracker.mark_outcome(
            prediction_id=request.prediction_id,
            actual_occurred=request.actual_occurred,
            feedback_source=request.feedback_source
        )
        
        return {
            "status": "success",
            "prediction_id": outcome.prediction_id,
            "is_correct": outcome.is_correct,
            "marked_at": outcome.marked_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to mark outcome: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark outcome")


@router.post("/reconcile", response_model=ReconciliationResponse)
async def reconcile_predictions(
    req: Request,
    nodes: Optional[List[str]] = None
) -> ReconciliationResponse:
    """Reconcile predictions with actual anomalies
    
    Args:
        req: FastAPI request
        nodes: Optional list of nodes to reconcile
        
    Returns:
        Reconciliation statistics
    """
    try:
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        repo = TrackingRepositoryExtension(pool)
        tracker = PredictionTracker(repository=repo)
        
        if nodes:
            # Bulk reconcile specific nodes
            results = await tracker.bulk_reconcile(nodes)
            # Aggregate results
            total_result = ReconciliationResult(
                total_predictions=sum(r.total_predictions for r in results),
                reconciled_count=sum(r.reconciled_count for r in results),
                true_positives=sum(r.true_positives for r in results),
                false_positives=sum(r.false_positives for r in results),
                false_negatives=sum(r.false_negatives for r in results),
                true_negatives=sum(r.true_negatives for r in results)
            )
        else:
            # Reconcile all predictions
            total_result = await tracker.reconcile_predictions()
        
        return ReconciliationResponse(
            total_predictions=total_result.total_predictions,
            reconciled_count=total_result.reconciled_count,
            true_positives=total_result.true_positives,
            false_positives=total_result.false_positives,
            false_negatives=total_result.false_negatives,
            true_negatives=total_result.true_negatives,
            timestamp=total_result.timestamp
        )
    except Exception as e:
        logger.error(f"Reconciliation failed: {e}")
        raise HTTPException(status_code=500, detail="Reconciliation failed")


@router.get("/metrics", response_model=MetricsResponse)
async def get_performance_metrics(
    req: Request,
    days_back: int = Query(7, ge=1, le=90, description="Days of history to analyze")
) -> MetricsResponse:
    """Get model performance metrics
    
    Args:
        req: FastAPI request
        days_back: Days to analyze
        
    Returns:
        Performance metrics
    """
    try:
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        repo = TrackingRepositoryExtension(pool)
        tracker = PredictionTracker(repository=repo)
        
        metrics = await tracker.calculate_metrics(days_back=days_back)
        
        return MetricsResponse(
            precision=metrics.precision,
            recall=metrics.recall,
            f1_score=metrics.f1_score,
            accuracy=metrics.accuracy,
            true_positives=metrics.true_positives,
            false_positives=metrics.false_positives,
            true_negatives=metrics.true_negatives,
            false_negatives=metrics.false_negatives,
            calculated_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Failed to calculate metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate metrics")


@router.get("/metrics/history")
async def get_metrics_history(
    req: Request,
    days: int = Query(30, ge=7, le=365, description="Days of history")
) -> List[Dict]:
    """Get historical performance metrics
    
    Args:
        req: FastAPI request
        days: Days of history
        
    Returns:
        List of historical metrics
    """
    try:
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        query = """
            SELECT * FROM water_infrastructure.model_performance_metrics
            WHERE calculated_at > NOW() - INTERVAL '%s days'
            ORDER BY calculated_at DESC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query % days)
            
            return [
                {
                    "calculated_at": row['calculated_at'].isoformat(),
                    "model_version": row['model_version'],
                    "precision": float(row['precision']),
                    "recall": float(row['recall']),
                    "f1_score": float(row['f1_score']),
                    "accuracy": float(row['accuracy'])
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics history")


@router.get("/health-check")
async def check_model_health(
    req: Request,
    threshold_f1: float = Query(0.7, ge=0.5, le=0.95, description="F1 score threshold")
) -> Dict:
    """Check if model performance is degraded
    
    Args:
        req: FastAPI request
        threshold_f1: Minimum acceptable F1 score
        
    Returns:
        Health status
    """
    try:
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        repo = TrackingRepositoryExtension(pool)
        tracker = PredictionTracker(repository=repo)
        
        is_degraded = await tracker.check_performance_degradation(threshold_f1=threshold_f1)
        metrics = await tracker.calculate_metrics(days_back=7)
        
        return {
            "status": "degraded" if is_degraded else "healthy",
            "current_f1": metrics.f1_score,
            "threshold": threshold_f1,
            "recommendation": "Consider retraining" if is_degraded else "Performance acceptable"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.delete("/cleanup")
async def cleanup_old_predictions(
    req: Request,
    retention_days: int = Query(90, ge=30, le=365, description="Days to retain")
) -> Dict:
    """Clean up old prediction records
    
    Args:
        req: FastAPI request
        retention_days: Days to retain predictions
        
    Returns:
        Cleanup statistics
    """
    try:
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        repo = TrackingRepositoryExtension(pool)
        tracker = PredictionTracker(repository=repo)
        
        deleted_count = await tracker.cleanup_old_predictions(retention_days)
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "retention_days": retention_days
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")
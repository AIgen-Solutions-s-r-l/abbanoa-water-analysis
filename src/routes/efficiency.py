"""
FastAPI routes for Network Efficiency API.

This module provides REST endpoints for network efficiency analytics,
including summary statistics, performance metrics, and node analysis.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from src.core.efficiency_service import EfficiencyService
from src.schemas.api.efficiency import EfficiencyResponse, ErrorResponse

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/v1/efficiency",
    tags=["efficiency"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)

# Global efficiency service instance
_efficiency_service: Optional[EfficiencyService] = None


async def get_efficiency_service() -> EfficiencyService:
    """Dependency to get efficiency service instance."""
    global _efficiency_service
    if _efficiency_service is None:
        _efficiency_service = EfficiencyService()
        await _efficiency_service.initialize()
    return _efficiency_service


@router.get(
    "/summary",
    response_model=EfficiencyResponse,
    summary="Get Network Efficiency Summary",
    description="""
    Get comprehensive network efficiency summary including:
    - Overall network efficiency metrics
    - System-wide performance statistics
    - Individual node performance data
    - Quality scores and operational efficiency
    
    Supports time range filtering and optional node filtering.
    """,
    responses={
        200: {
            "description": "Efficiency summary retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "summary": {
                            "time_range": "24h",
                            "period_start": "2024-01-15T00:00:00",
                            "period_end": "2024-01-16T00:00:00",
                            "total_nodes": 8,
                            "active_nodes": 7,
                            "analyzed_hours": 24
                        },
                        "efficiency_metrics": {
                            "network_efficiency_percentage": 87.5,
                            "total_throughput_m3h": 1250.75,
                            "average_pressure_bar": 4.2,
                            "quality_score": 0.95,
                            "operational_efficiency": 83.3,
                            "flow_consistency_score": 0.92
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "example": {
                        "error": "invalid_time_range",
                        "message": "Invalid time range: 48h. Must be one of: ['1h', '6h', '24h', '3d', '7d', '30d']",
                        "details": {
                            "provided_value": "48h",
                            "valid_values": ["1h", "6h", "24h", "3d", "7d", "30d"]
                        }
                    }
                }
            }
        }
    }
)
async def get_efficiency_summary(
    time_range: str = Query(
        default="24h",
        description="Time range for analysis",
        regex="^(1h|6h|24h|3d|7d|30d)$",
        example="24h"
    ),
    node_ids: Optional[List[str]] = Query(
        default=None,
        description="Optional list of specific node IDs to analyze",
        example=["215542", "288400"]
    ),
    service: EfficiencyService = Depends(get_efficiency_service)
) -> EfficiencyResponse:
    """
    Get network efficiency summary with optional filtering.
    
    Args:
        time_range: Time range for analysis ("1h", "6h", "24h", "3d", "7d", "30d")
        node_ids: Optional list of specific node IDs to analyze
        service: Injected efficiency service
        
    Returns:
        EfficiencyResponse with comprehensive efficiency metrics
        
    Raises:
        400: Invalid time range or node IDs
        500: Internal server error
    """
    try:
        logger.info(f"Efficiency summary request: time_range={time_range}, node_ids={node_ids}")
        
        # Validate time range
        valid_ranges = ["1h", "6h", "24h", "3d", "7d", "30d"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_time_range",
                    "message": f"Invalid time range: {time_range}. Must be one of: {valid_ranges}",
                    "details": {
                        "provided_value": time_range,
                        "valid_values": valid_ranges
                    }
                }
            )
        
        # Validate node IDs if provided
        if node_ids is not None:
            if not isinstance(node_ids, list) or len(node_ids) == 0:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_node_ids",
                        "message": "node_ids must be a non-empty list of strings",
                        "details": {
                            "provided_value": node_ids,
                            "expected_type": "List[str]"
                        }
                    }
                )
            
            # Validate each node ID is a string
            for node_id in node_ids:
                if not isinstance(node_id, str) or not node_id.strip():
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "invalid_node_id",
                            "message": f"Invalid node ID: {node_id}. Must be a non-empty string",
                            "details": {
                                "provided_value": node_id,
                                "node_ids": node_ids
                            }
                        }
                    )
        
        # Get efficiency summary from service
        result = await service.get_efficiency_summary(
            time_range=time_range,
            node_ids=node_ids
        )
        
        logger.info(f"Efficiency summary completed: {result['summary']['total_nodes']} nodes analyzed")
        
        return EfficiencyResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
        
    except ValueError as e:
        # Handle service validation errors
        logger.warning(f"Invalid request parameters: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_parameters",
                "message": str(e),
                "details": {
                    "time_range": time_range,
                    "node_ids": node_ids
                }
            }
        )
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in efficiency summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred while processing the efficiency summary",
                "details": {
                    "time_range": time_range,
                    "node_ids": node_ids
                }
            }
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check the health status of the efficiency service",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "efficiency",
                        "version": "1.0"
                    }
                }
            }
        }
    }
)
async def health_check(
    service: EfficiencyService = Depends(get_efficiency_service)
) -> dict:
    """
    Health check endpoint for the efficiency service.
    
    Returns:
        Dictionary with health status information
    """
    try:
        # Test service connection
        await service.get_efficiency_summary(time_range="1h", node_ids=None)
        
        return {
            "status": "healthy",
            "service": "efficiency",
            "version": "1.0",
            "timestamp": "2024-01-16T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "Efficiency service is currently unavailable",
                "details": {
                    "error": str(e)
                }
            }
        ) 
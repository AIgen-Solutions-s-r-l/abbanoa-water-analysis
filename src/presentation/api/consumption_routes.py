"""
API routes for consumption analytics.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import os

from src.infrastructure.database.consumption_service import (
    ConsumptionService,
    ConsumptionServiceError,
)

router = APIRouter(prefix="/consumption", tags=["consumption"])


def get_consumption_service() -> ConsumptionService:
    """Get consumption service instance."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://abbanoa_user:abbanoa_secure_pass@localhost:5432/abbanoa_processing",
    )
    return ConsumptionService(database_url)


@router.get("/analytics")
async def get_consumption_analytics(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get comprehensive consumption analytics using real data.

    Returns:
        Dict containing:
        - data_metadata: Information about the data source and quality
        - summary: Key consumption metrics
        - district_consumption: Consumption data by district/node
        - consumption_timeline: 24-hour consumption pattern
        - user_segments: User segmentation analysis
        - peak_demand: Peak demand analysis
        - conservation_opportunities: Water conservation opportunities
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return analytics_data
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/summary")
async def get_consumption_summary(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get consumption summary metrics.

    Returns:
        Dict containing summary metrics only
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "summary": analytics_data.get("summary", {}),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/districts")
async def get_district_consumption(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get consumption data by district/node.

    Returns:
        Dict containing district consumption data
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "district_consumption": analytics_data.get("district_consumption", []),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/timeline")
async def get_consumption_timeline(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get 24-hour consumption timeline.

    Returns:
        Dict containing consumption timeline data
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "consumption_timeline": analytics_data.get("consumption_timeline", []),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/segments")
async def get_user_segments(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get user segmentation analysis.

    Returns:
        Dict containing user segments data
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "user_segments": analytics_data.get("user_segments", []),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/peak-demand")
async def get_peak_demand(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get peak demand analysis.

    Returns:
        Dict containing peak demand data
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "peak_demand": analytics_data.get("peak_demand", {}),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/conservation")
async def get_conservation_opportunities(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get water conservation opportunities.
    
    Returns:
        Dict containing conservation opportunities data
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "conservation_opportunities": analytics_data.get(
                "conservation_opportunities", []
            ),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/hourly-pattern")
async def get_hourly_pattern(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get detailed hourly consumption pattern for 24-hour visualization.
    
    Returns:
        Dict containing hourly pattern data for charts
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "hourly_pattern": analytics_data.get("hourly_pattern", []),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/trend-analysis")
async def get_trend_analysis(
    service: ConsumptionService = Depends(get_consumption_service),
) -> Dict[str, Any]:
    """
    Get trend analysis data for consumption patterns.
    
    Returns:
        Dict containing trend analysis data
    """
    try:
        analytics_data = service.get_consumption_analytics()
        return {
            "trend_analysis": analytics_data.get("trend_analysis", {}),
            "data_metadata": analytics_data.get("data_metadata", {}),
        }
    except ConsumptionServiceError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

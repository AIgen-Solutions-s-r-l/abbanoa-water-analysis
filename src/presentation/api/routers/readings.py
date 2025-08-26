
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.application.services.reading_service import ReadingService
from src.presentation.api.dependencies import get_reading_service
from src.schemas.reading import Reading

router = APIRouter()

@router.get("/nodes/{node_id}/readings", response_model=List[Reading])
async def get_node_readings(
    node_id: str,
    start_time: Optional[str] = Query(None, description="Start time for readings (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time for readings (ISO format)"),
    max_points: int = Query(500, description="Maximum number of data points to return"),
    reading_service: ReadingService = Depends(get_reading_service)
):
    try:
        return await reading_service.get_node_readings(node_id, start_time, end_time, max_points)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

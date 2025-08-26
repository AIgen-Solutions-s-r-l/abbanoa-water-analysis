
from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import Optional
from src.application.services.energy_service import EnergyService
from src.presentation.api.dependencies import get_energy_service
from src.schemas.energy import EnergyOptimization

router = APIRouter()

@router.get("/energy/optimization", response_model=Optional[EnergyOptimization])
async def get_energy_optimization(
    response: Response,
    energy_service: EnergyService = Depends(get_energy_service)
):
    try:
        result = await energy_service.get_energy_optimization()
        if result is None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

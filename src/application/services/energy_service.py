
from typing import Optional
from src.infrastructure.repositories.energy_repository import EnergyRepository
from src.schemas.energy import EnergyOptimization

class EnergyService:
    def __init__(self, energy_repository: EnergyRepository):
        self.energy_repository = energy_repository

    async def get_energy_optimization(self) -> Optional[EnergyOptimization]:
        return await self.energy_repository.get_energy_optimization()

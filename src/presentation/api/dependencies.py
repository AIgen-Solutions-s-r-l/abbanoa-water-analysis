
from fastapi import Depends, Request
from src.application.services.node_service import NodeService
from src.infrastructure.repositories.node_repository import NodeRepository
from src.application.services.dashboard_service import DashboardService
from src.infrastructure.repositories.dashboard_repository import DashboardRepository
from src.application.services.anomaly_service import AnomalyService
from src.infrastructure.repositories.anomaly_repository import AnomalyRepository
from src.application.services.reading_service import ReadingService
from src.infrastructure.repositories.reading_repository import ReadingRepository
from src.application.services.efficiency_service import EfficiencyService
from src.infrastructure.repositories.efficiency_repository import EfficiencyRepository
from src.application.services.pressure_service import PressureService
from src.infrastructure.repositories.pressure_repository import PressureRepository
from src.application.services.consumption_service import ConsumptionService
from src.infrastructure.repositories.consumption_repository import ConsumptionRepository
from src.application.services.energy_service import EnergyService
from src.infrastructure.repositories.energy_repository import EnergyRepository
from src.application.services.weather_service import WeatherService
from src.infrastructure.repositories.weather_repository import WeatherRepository
from src.application.services.ml_service import MLService
from src.infrastructure.repositories.ml_repository import MLRepository

def get_pool(request: Request):
    return request.app.state.pool

def get_node_repository(pool = Depends(get_pool)) -> NodeRepository:
    return NodeRepository(pool)

def get_node_service(node_repository: NodeRepository = Depends(get_node_repository)) -> NodeService:
    return NodeService(node_repository)

def get_dashboard_repository(pool = Depends(get_pool)) -> DashboardRepository:
    return DashboardRepository(pool)

def get_dashboard_service(dashboard_repository: DashboardRepository = Depends(get_dashboard_repository)) -> DashboardService:
    return DashboardService(dashboard_repository)

def get_anomaly_repository(pool = Depends(get_pool)) -> AnomalyRepository:
    return AnomalyRepository(pool)

def get_anomaly_service(anomaly_repository: AnomalyRepository = Depends(get_anomaly_repository)) -> AnomalyService:
    return AnomalyService(anomaly_repository)

def get_reading_repository(pool = Depends(get_pool)) -> ReadingRepository:
    return ReadingRepository(pool)

def get_reading_service(reading_repository: ReadingRepository = Depends(get_reading_repository)) -> ReadingService:
    return ReadingService(reading_repository)

def get_efficiency_repository(pool = Depends(get_pool)) -> EfficiencyRepository:
    return EfficiencyRepository(pool)

def get_efficiency_service(efficiency_repository: EfficiencyRepository = Depends(get_efficiency_repository)) -> EfficiencyService:
    return EfficiencyService(efficiency_repository)

def get_pressure_repository(pool = Depends(get_pool)) -> PressureRepository:
    return PressureRepository(pool)

def get_pressure_service(pressure_repository: PressureRepository = Depends(get_pressure_repository)) -> PressureService:
    return PressureService(pressure_repository)

def get_consumption_repository(pool = Depends(get_pool)) -> ConsumptionRepository:
    return ConsumptionRepository(pool)

def get_consumption_service(consumption_repository: ConsumptionRepository = Depends(get_consumption_repository)) -> ConsumptionService:
    return ConsumptionService(consumption_repository)

def get_energy_repository(pool = Depends(get_pool)) -> EnergyRepository:
    return EnergyRepository(pool)

def get_energy_service(energy_repository: EnergyRepository = Depends(get_energy_repository)) -> EnergyService:
    return EnergyService(energy_repository)

def get_weather_repository(pool = Depends(get_pool)) -> WeatherRepository:
    return WeatherRepository(pool)

def get_weather_service(weather_repository: WeatherRepository = Depends(get_weather_repository)) -> WeatherService:
    return WeatherService(weather_repository)

def get_ml_repository(pool = Depends(get_pool)) -> MLRepository:
    return MLRepository(pool)

def get_ml_service(ml_repository: MLRepository = Depends(get_ml_repository)) -> MLService:
    return MLService(ml_repository)

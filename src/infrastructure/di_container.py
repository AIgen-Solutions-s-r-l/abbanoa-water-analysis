"""Dependency injection container configuration."""

from dependency_injector import containers, providers

from src.application.interfaces.event_bus import IEventBus
from src.application.interfaces.notification_service import INotificationService
from src.application.interfaces.repositories import (
    IMonitoringNodeRepository,
    ISensorReadingRepository,
    IWaterNetworkRepository,
)
from src.application.use_cases.analyze_consumption_patterns import (
    AnalyzeConsumptionPatternsUseCase,
)
from src.application.use_cases.calculate_network_efficiency import (
    CalculateNetworkEfficiencyUseCase,
)
from src.application.use_cases.detect_network_anomalies import (
    DetectNetworkAnomaliesUseCase,
)
from src.application.use_cases.forecast_consumption import ForecastConsumption
from src.domain.services.anomaly_detection_service import AnomalyDetectionService
from src.domain.services.network_efficiency_service import NetworkEfficiencyService
from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient
from src.infrastructure.repositories.bigquery_forecast_repository import BigQueryForecastRepository
from src.infrastructure.services.forecast_calculation_service import ForecastCalculationService
from src.infrastructure.external_services.bigquery_service import BigQueryService
from src.infrastructure.external_services.event_bus import InMemoryEventBus
from src.infrastructure.external_services.notification_service import (
    LoggingNotificationService,
)
from src.infrastructure.persistence.bigquery_config import (
    BigQueryConfig,
    BigQueryConnection,
)
from src.infrastructure.repositories.monitoring_node_repository import (
    BigQueryMonitoringNodeRepository,
)
from src.infrastructure.repositories.sensor_data_repository import (
    SensorDataRepository,
)
from src.infrastructure.repositories.sensor_reading_repository import (
    BigQuerySensorReadingRepository,
)
from src.infrastructure.repositories.static_monitoring_node_repository import (
    StaticMonitoringNodeRepository,
)
from src.infrastructure.repositories.water_network_repository import (
    BigQueryWaterNetworkRepository,
)


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    config = providers.Configuration()

    # BigQuery configuration
    bigquery_config = providers.Singleton(
        BigQueryConfig,
        project_id=config.bigquery.project_id,
        dataset_id=config.bigquery.dataset_id,
        credentials_path=config.bigquery.credentials_path,
        location=config.bigquery.location,
    )

    # BigQuery connection
    bigquery_connection = providers.Singleton(
        BigQueryConnection,
        config=bigquery_config,
    )

    # External services
    bigquery_service = providers.Singleton(
        BigQueryService,
        config=bigquery_config,
    )

    event_bus = providers.Singleton(
        InMemoryEventBus,
    )

    notification_service = providers.Singleton(
        LoggingNotificationService,
    )
    
    # Async BigQuery client for forecast services
    async_bigquery_client = providers.Singleton(
        AsyncBigQueryClient,
        project_id=config.bigquery.project_id,
        dataset_id=config.bigquery.dataset_id,
    )

    # Repositories
    # Use SensorDataRepository for real data from sensor_data table
    sensor_reading_repository = providers.Singleton(
        SensorDataRepository,
        connection=bigquery_connection,
    )

    monitoring_node_repository = providers.Singleton(
        StaticMonitoringNodeRepository,
        connection=bigquery_connection,
    )

    water_network_repository = providers.Singleton(
        BigQueryWaterNetworkRepository,
        connection=bigquery_connection,
    )
    
    # Forecast repositories and services
    forecast_repository = providers.Singleton(
        BigQueryForecastRepository,
        client=async_bigquery_client,
        ml_dataset_id="ml_models",  # Default ML dataset
    )
    
    forecast_calculation_service = providers.Singleton(
        ForecastCalculationService,
        bigquery_client=async_bigquery_client,
    )

    # Domain services
    anomaly_detection_service = providers.Singleton(
        AnomalyDetectionService,
        z_score_threshold=config.anomaly_detection.z_score_threshold,
        min_data_points=config.anomaly_detection.min_data_points,
        rolling_window_hours=config.anomaly_detection.rolling_window_hours,
    )

    network_efficiency_service = providers.Singleton(
        NetworkEfficiencyService,
    )

    # Use cases
    analyze_consumption_patterns_use_case = providers.Factory(
        AnalyzeConsumptionPatternsUseCase,
        sensor_reading_repository=sensor_reading_repository,
    )

    detect_network_anomalies_use_case = providers.Factory(
        DetectNetworkAnomaliesUseCase,
        sensor_reading_repository=sensor_reading_repository,
        monitoring_node_repository=monitoring_node_repository,
        anomaly_detection_service=anomaly_detection_service,
        event_bus=event_bus,
        notification_service=notification_service,
    )

    calculate_network_efficiency_use_case = providers.Factory(
        CalculateNetworkEfficiencyUseCase,
        water_network_repository=water_network_repository,
        monitoring_node_repository=monitoring_node_repository,
        sensor_reading_repository=sensor_reading_repository,
        network_efficiency_service=network_efficiency_service,
        event_bus=event_bus,
    )
    
    forecast_consumption_use_case = providers.Factory(
        ForecastConsumption,
        forecast_repository=forecast_repository,
        forecast_calculation_service=forecast_calculation_service,
    )

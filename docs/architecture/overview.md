# Architecture Overview

## Introduction

The Abbanoa Water Infrastructure Monitoring System is built following Domain-Driven Design (DDD) principles and clean architecture patterns. This document provides an overview of the system architecture, key design decisions, and implementation patterns.

## Architectural Principles

### 1. Domain-Driven Design (DDD)

The system is organized around the water infrastructure domain, with clear boundaries between:

- **Core Domain**: Water monitoring, sensor readings, network efficiency
- **Supporting Subdomains**: Data normalization, reporting, notifications
- **Generic Subdomains**: Authentication, logging, data persistence

### 2. Clean Architecture

The architecture follows the clean architecture pattern with clear layer separation:

```
┌─────────────────────────────────────────────────────┐
│                   Presentation                      │
│         (Web UI, CLI, REST API)                    │
├─────────────────────────────────────────────────────┤
│                   Application                       │
│         (Use Cases, DTOs, Interfaces)             │
├─────────────────────────────────────────────────────┤
│                     Domain                          │
│    (Entities, Value Objects, Domain Services)     │
├─────────────────────────────────────────────────────┤
│                 Infrastructure                      │
│    (Repositories, External Services, DB)          │
└─────────────────────────────────────────────────────┘
```

### 3. Dependency Rule

Dependencies flow inward:
- Infrastructure depends on Domain
- Application depends on Domain
- Presentation depends on Application and Domain
- Domain has no external dependencies

## Layer Descriptions

### Domain Layer

The heart of the system containing:

- **Entities**: Core business objects with identity
  - `SensorReading`: Time-series sensor measurements
  - `MonitoringNode`: Physical monitoring locations
  - `WaterNetwork`: Network of interconnected nodes

- **Value Objects**: Immutable objects without identity
  - `FlowRate`, `Pressure`, `Temperature`, `Volume`: Measurements
  - `NodeLocation`: Geographic and administrative location
  - `DataQualityMetrics`: Data quality indicators

- **Domain Services**: Business logic spanning multiple entities
  - `AnomalyDetectionService`: Statistical anomaly detection
  - `NetworkEfficiencyService`: Efficiency calculations

- **Domain Events**: Significant business occurrences
  - `AnomalyDetectedEvent`
  - `ThresholdExceededEvent`
  - `NetworkEfficiencyCalculatedEvent`

### Application Layer

Orchestrates the domain layer:

- **Use Cases**: Application-specific business rules
  - `AnalyzeConsumptionPatternsUseCase`
  - `DetectNetworkAnomaliesUseCase`
  - `CalculateNetworkEfficiencyUseCase`

- **Interfaces**: Contracts for infrastructure services
  - `ISensorReadingRepository`
  - `IEventBus`
  - `INotificationService`

- **DTOs**: Data transfer objects for external communication

### Infrastructure Layer

Technical implementations:

- **Repositories**: Data persistence implementations
  - `BigQuerySensorReadingRepository`
  - `BigQueryMonitoringNodeRepository`

- **External Services**: Third-party integrations
  - `BigQueryService`: Google BigQuery integration
  - `InMemoryEventBus`: Event handling
  - `LoggingNotificationService`: Alert notifications

- **Data Normalization**: CSV data processing
  - `SelargiusDataNormalizer`: Site-specific normalization

### Presentation Layer

User interfaces:

- **Web Dashboard**: Streamlit-based real-time monitoring
- **CLI**: Command-line tools for operations
- **REST API**: FastAPI-based programmatic access

## Key Design Patterns

### Repository Pattern

Abstracts data access behind interfaces:

```python
class ISensorReadingRepository(ABC):
    async def add(self, reading: SensorReading) -> None
    async def get_by_id(self, id: UUID) -> Optional[SensorReading]
    async def get_by_node_id(self, node_id: UUID) -> List[SensorReading]
```

### Dependency Injection

Uses `dependency-injector` for IoC:

```python
class Container(containers.DeclarativeContainer):
    sensor_reading_repository = providers.Singleton(
        BigQuerySensorReadingRepository,
        connection=bigquery_connection
    )
```

### Event-Driven Architecture

Domain events for loose coupling:

```python
@dataclass
class AnomalyDetectedEvent(DomainEvent):
    node_id: UUID
    anomaly_type: str
    severity: str
```

### Value Objects

Encapsulate business rules:

```python
@dataclass(frozen=True)
class FlowRate(Measurement):
    value: float
    unit: str = "L/s"
    
    def _validate(self) -> None:
        if self.value < 0:
            raise ValueError("Flow rate cannot be negative")
```

## Data Flow

### Sensor Data Ingestion

1. CSV files uploaded to system
2. `SelargiusDataNormalizer` processes raw data
3. Domain entities created from normalized data
4. Entities persisted via repositories
5. Events published for significant occurrences

### Analysis Request Flow

1. User initiates analysis via UI/CLI/API
2. Presentation layer invokes use case
3. Use case orchestrates domain services
4. Domain services apply business logic
5. Results returned through DTOs
6. Presentation layer formats for display

## Technology Stack

- **Language**: Python 3.12+
- **Frameworks**: FastAPI, Streamlit
- **Database**: Google BigQuery
- **DI Container**: dependency-injector
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, isort, flake8, mypy

## Scalability Considerations

1. **Horizontal Scaling**: Stateless services enable easy scaling
2. **Event Bus**: Supports distributed event handling
3. **Repository Pattern**: Allows switching data stores
4. **BigQuery**: Handles large-scale time-series data

## Security Considerations

1. **Authentication**: Handled at presentation layer
2. **Authorization**: Role-based access control
3. **Data Validation**: Value objects enforce constraints
4. **Audit Trail**: Domain events provide history

## Future Enhancements

1. **CQRS**: Separate read/write models for performance
2. **Event Sourcing**: Store events as source of truth
3. **Microservices**: Split into smaller services
4. **Real-time Processing**: Stream processing for live data
# Changelog

All notable changes to the Abbanoa Water Infrastructure Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-04

### Added
- **Domain-Driven Design (DDD) Architecture**: Complete restructure with clean architecture principles
  - Domain layer with entities, value objects, and services
  - Application layer with use cases and DTOs
  - Infrastructure layer with repositories and external services
  - Presentation layer with multiple interfaces (Web, API, CLI)
- **Integrated Streamlit Dashboard**: Unified dashboard with 6 main tabs
  - Overview: Real-time system metrics and alerts
  - Forecast: ML-powered 7-day predictions
  - Anomaly Detection: Real-time anomaly monitoring
  - Consumption Patterns: Historical analysis and trends
  - Network Efficiency: Performance metrics and KPIs
  - Reports: Automated report generation
- **BigQuery Integration**: Direct connection to production data warehouse
  - Normalized view `v_sensor_readings_normalized`
  - Support for existing `sensor_data` table
  - Static monitoring node repository
- **Dependency Injection**: Clean dependency management with dependency-injector
- **No Synthetic Data**: Pure real-data visualization
  - Removed all random data generation
  - Shows actual data from November 2024 - March 2025
  - Empty states when no data available

### Changed
- **Architecture**: From monolithic scripts to DDD layers
- **Data Access**: From direct BigQuery queries to repository pattern
- **Dashboard**: From separate dashboard to integrated multi-tab interface
- **Configuration**: Environment-based configuration with DI container
- **Error Handling**: Comprehensive error handling across all layers

### Fixed
- ImportError issues with Location/Coordinates value objects
- Streamlit caching issues with self parameters
- Abstract method implementation in repository classes
- Date/time handling to avoid synthetic current dates

### Removed
- Old dashboard implementation (`legacy/` directory)
- Synthetic data generation in all components
- Direct BigQuery client usage in favor of repositories
- Hardcoded configuration values

## [0.5.0] - 2025-06-15

### Added
- Initial Streamlit dashboard with forecast tab
- Basic BigQuery integration
- ML model integration for forecasting

## [0.4.0] - 2025-05-20

### Added
- ARIMA_PLUS ML models for 7-day forecasting
- Async forecast consumption use case
- BigQuery ML integration
- Operational documentation

### Changed
- Improved forecast accuracy to <15% MAPE
- Enhanced data pipeline performance

## [0.3.0] - 2025-04-10

### Added
- Teatinos data processing pipeline
- Hidroconta sensor data normalization
- Multi-site architecture support

### Changed
- Unified BigQuery schema for multiple sites
- Enhanced data quality checks

## [0.2.0] - 2025-03-05

### Added
- Selargius data processing pipeline
- BigQuery data warehouse integration
- Basic analytics queries

### Changed
- Improved CSV parsing for Italian formats
- Enhanced error handling

## [0.1.0] - 2025-02-01

### Added
- Initial project structure
- Basic data ingestion scripts
- README documentation
- BigQuery schema definitions

[1.0.0]: https://github.com/abbanoa/water-infrastructure/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/abbanoa/water-infrastructure/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/abbanoa/water-infrastructure/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/abbanoa/water-infrastructure/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/abbanoa/water-infrastructure/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/abbanoa/water-infrastructure/releases/tag/v0.1.0
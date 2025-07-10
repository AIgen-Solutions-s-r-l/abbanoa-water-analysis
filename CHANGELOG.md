# Changelog



## [v1.2.2.0] - 2025-07-10

- ✨ feat: integrate new sensor nodes from backup data

## [v1.2.1.0] - 2025-07-10

- ✨ feat: add ML/AI-ready data pipeline for backup sensor data
- 🐛 fix: replace vw_daily_timeseries with v_sensor_readings_normalized
- 🐛 fix: resolve parameter validation and timeout issues
- ✨ feat: add Docker support for API deployment
- 📚 docs: improve user guidance for forecast feature
- 🐛 fix: remove invalid ml_dataset_id configuration

## [1.2.0.1] - 2025-07-07

### Bug Fixes
- Fixed forecast functionality issues with ARIMA model integration
- Resolved BigQuery ML.FORECAST query structure problems
- Fixed column name mismatches between frontend and backend
- Corrected DataFetcher to call actual API endpoints

### Improvements
- Moved all forecast calculations from frontend to backend
- Created ForecastCalculationService for centralized computation
- Added comprehensive error handling with fallback mechanisms
- Enhanced logging throughout the forecast pipeline
- Improved performance with backend-side calculations

### Features
- Added forecast API endpoint at `/api/v1/forecasts/{district_id}/{metric}`
- Implemented fallback forecast using simple moving average
- Added model status endpoint for monitoring
- Created validation script for testing forecast functionality

### Technical Changes
- Updated DI container to wire forecast services
- Added structured logging with performance metrics
- Created integration tests for end-to-end forecast flow
- Added error handling middleware for consistent API responses

### Documentation
- Created comprehensive hotfix summary document
- Added API documentation for forecast endpoints
- Updated validation and testing procedures

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.2.0.0] - 2025-07-05

### Features
- Enhanced Streamlit dashboard with comprehensive time range filtering capabilities
- Implemented real-time alert system with severity levels (Critical, Warning, Info)
- Added intelligent alert detection based on pressure thresholds, flow anomalies, and data quality

### Improvements
- Enhanced date range handling to respect actual data boundaries (Nov 13, 2024 - Mar 31, 2025)
- Improved anomaly visualization methods with time range parameters
- Applied code formatting with black and isort for better code consistency

### Bug Fixes
- Fixed edge cases where requested time ranges could exceed available data
- Improved data validation to ensure queries stay within valid date ranges

### Documentation
- Added comprehensive release notes documentation
- Updated code style with consistent formatting

### Contributors
- @alessio

🤖 Generated with [Claude Code](https://claude.ai/code)

All notable changes to the Abbanoa Water Infrastructure Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with 4-digit versioning (W.X.Y.Z).

## [1.1.0.0] - 2025-07-04

### Added
- **"Last Year" Time Range**: New option to analyze full year of historical data
- **Custom Date Range Selector**: Pick any date range within available data (Nov 2024 - Mar 2025)
- **Real-Time Node Status**: Live flow rate and pressure readings in Overview tab
- **Automatic Authentication**: Auto-detection of Google Cloud Application Default Credentials
- **Enhanced Error Handling**: Better error messages and debugging information
- **Data Availability Notice**: Clear indication of available data range in sidebar

### Changed
- **Overview Tab**: Complete rewrite to fetch real BigQuery data
  - Real flow rate trends with actual sensor data
  - Live node status cards with current metrics
  - Proper data aggregation for efficiency calculations
- **Consumption Tab**: Direct repository access for better performance
  - Removed use case dependency for simpler data flow
  - Added success messages when data is loaded
  - Fixed DataFrame pivoting for multiple nodes
- **Authentication Flow**: Improved BigQuery connection handling
  - Support for both ADC and service account keys
  - Automatic fallback to default credentials
  - Clear authentication status in run script

### Fixed
- **Flow Rate Trends**: Overview tab now displays real sensor data instead of empty charts
- **Node Status**: Fixed hardcoded "No Data" to show actual node metrics
- **BigQuery Authentication**: Resolved MalformedError with Application Default Credentials
- **Data Access**: Fixed attribute access for sensor readings (flow_rate, pressure, volume)
- **Custom Date Range**: Properly handles date selection and passes to data fetchers
- **Poetry Dependencies**: All required packages properly installed in virtual environment

### Improved
- **Performance**: Optimized data fetching with proper async handling
- **User Feedback**: Added success messages and data counters
- **Code Quality**: Removed unused synthetic data generation methods
- **Documentation**: Updated README with clear setup instructions

## [1.0.0.0] - 2025-07-04

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
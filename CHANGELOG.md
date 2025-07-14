# Changelog






## [v1.2.8.0] - 2025-07-14

- 🐛 fix: add psycopg2-binary dependency for PostgreSQL fallback functionality
- ✨ feat: add Enhanced Overview to navigation sidebar\n\n- Add Enhanced Overview navigation link to sidebar between Dashboard and Monitoring\n- Use layout/grid icon to represent comprehensive system overview\n- Enables easy access to the migrated Enhanced System Overview dashboard
- ✨ feat: complete testing setup and implementation for Enhanced System Overview
- 🐛 fix: remove unused setAlerts variable to fix linting error
- ✨ feat: complete Enhanced System Overview dashboard implementation
- ✨ feat: implement FlowAnalyticsChart component with time series, distribution and correlation analysis

## [v1.2.7.0] - 2025-07-14

- ✨ feat: add Next.js frontend with authentication and mock backend

## [v1.2.6.0] - 2025-07-14

- ✨ feat: implement comprehensive API testing framework with 126 tests
- ✨ feat: Complete KPI service implementation with comprehensive business logic
- ✨ feat: implement comprehensive report generation system
- ✨ feat: implement advanced forecasting endpoints with time series analysis
- ✨ feat: implement comprehensive water quality monitoring endpoints
- ✨ feat: implement comprehensive consumption patterns endpoints
- ✨ feat: add comprehensive Pydantic schemas for all API endpoints

## [v1.2.5.0] - 2025-07-13

- ✨ feat: add LocalAnomalyDetector fallback to API-based AnomalyTab
- ✨ feat: force complete cache refresh with enhanced UI
- 🐛 fix: resolve performance monitor import error
- ✨ feat: finalize working anomaly detection with proper caching
- ✨ feat: force cache refresh to show working anomaly detection
- 🐛 fix: fix probability normalization in synthetic anomaly generation
- 🐛 fix: force cache refresh to enable local anomaly detection
- 📚 docs: add comprehensive anomaly detection implementation documentation
- 🐛 fix: correct DTO parameter mapping for anomaly detection
- ✨ feat: implement working local anomaly detection system

## [v1.2.4.0] - 2025-07-13

- ✅ test: fix efficiency component test issues and floating point precision
- ✨ feat: upgrade API efficiency tab to use enhanced Sprint 2 components
- 📚 docs: add comprehensive documentation for efficiency components
- ✨ feat: add comprehensive unit tests for efficiency UI components
- ✨ feat: implement drill-down filters with district/node multi-select
- ✨ feat: create KpiCard component for efficiency metrics with status indicators
- ✨ feat: create EfficiencyTrend chart component with 95% target line and rich tooltips
- ✨ feat: refactor EfficiencyTab to use DataFetcher with loading states
- ✨ feat: add efficiency data fetcher with 30s cache and trend methods
- 📚 docs: document new efficiency endpoint
- ✨ feat: create comprehensive CI pipeline for efficiency service
- ✨ feat: create comprehensive efficiency service tests with 16 test cases
- ✨ feat: integrate efficiency router with main FastAPI app
- ✨ feat: create efficiency REST endpoint with comprehensive validation
- ✨ feat: create Pydantic response schemas for efficiency endpoint
- ✨ feat: create efficiency service with get_efficiency_summary function
- 📚 docs: document live network efficiency pipeline
- 🐛 fix: correct Redis cache initialization method
- 📚 docs: document live network efficiency pipeline
- ✨ feat: create comprehensive schema validation script for network efficiency table
- ✨ feat: create comprehensive 90-day backfill script for network efficiency data
- ✨ feat: add network efficiency ETL scheduling via cron.yaml and Python scheduler
- ✨ feat: create network efficiency meter collection script without dry_run
- ♻️ refactor: remove obsolete test scripts for anomaly detection, API integration, data loading, and flow data verification
- ♻️ refactor: update PostgresManager to use base table for time series data retrieval

## [v1.2.3.14] - 2025-07-12

### Critical Bug Fixes
- fix(hybrid-service): restructure tier logic to use PostgreSQL as primary data source
  - Removed failing BigQuery tier dependency for wide date ranges
  - PostgreSQL now serves as primary data source for all queries (contains complete ETL-synced dataset)
  - Eliminated "No data from..." error messages and fallback confusion
  - Streamlined data flow: PostgreSQL → Redis (fallback only)
  - Fixed async event loop and connection pool conflicts

- fix(consumption): resolve decimal.Decimal to float conversion errors  
  - Fixed "unsupported operand type(s) for '*': 'decimal.Decimal' and 'float'" errors
  - Added pd.to_numeric() conversion for PostgreSQL decimal values before calculations
  - Fixed pandas Series to scalar function mapping for hourly factor calculations
  - Consumption calculations now work properly with mixed data types

### Performance Improvements
- Enhanced time range handling for better weekly data distribution
  - Updated default time ranges to show full 7-day patterns instead of 24-hour snapshots
  - Improved consumption pattern visualization across all days of the week
  - Better data distribution in heatmaps and weekly trend charts

### UI/UX Improvements
- Cleaned up debug logging and error messages for production use
- Re-enabled Streamlit caching for improved dashboard performance
- Removed confusing BigQuery error messages from user interface
- Enhanced consumption data range display with realistic weekly patterns

### Data Architecture Fixes
- Simplified three-tier architecture to focus on PostgreSQL warm storage
- Removed dependency on BigQuery for operational dashboard queries
- Fixed PostgreSQL connection pool management for better stability
- Enhanced error handling for database connection edge cases

### Technical Changes
- Updated HybridDataService.get_node_data() to prioritize PostgreSQL queries
- Fixed pandas operations for PostgreSQL decimal data types
- Improved async context handling in Streamlit environment
- Enhanced consumption tab data processing pipeline

## [v1.2.3.13] - 2025-07-12

### Bug Fixes
- fix(heatmap): resolve consumption heatmap data aggregation error
  - Fixed "agg function failed [how->mean,dtype->object]" error in consumption heatmap
  - Added explicit numeric data type conversion before pandas aggregation
  - Enhanced handling of mixed data types with proper NaN validation
  - Improved timestamp conversion for datetime operations
  - Heatmap now properly displays consumption patterns instead of all zeros

### Technical Changes
- Updated consumption heatmap calculation to handle data type conversion properly
- Added robust error handling for non-numeric columns in aggregation
- Enhanced data validation to prevent aggregation of object-type columns

## [v1.2.3.12] - 2025-07-12

### Critical Bug Fixes
- fix(auth): resolve PostgreSQL authentication failure in HybridDataService
  - Fixed hardcoded wrong database credentials in HybridDataService initialization
  - Updated connection parameters to use correct processing database (abbanoa_processing)
  - Resolved "password authentication failed for user 'postgres'" error
  - HybridDataService now properly connects to localhost:5434/abbanoa_processing with abbanoa_user credentials

- fix(imports): resolve performance_monitor import error
  - Added missing global performance_monitor instance in performance_monitor.py module
  - Fixed "cannot import name 'performance_monitor'" ImportError that prevented dashboard startup
  - Dashboard now imports performance monitoring functionality correctly

- fix(connections): resolve PostgreSQL connection pool issues
  - Disabled background sync tasks in Streamlit context to prevent event loop conflicts
  - Added connection validation before query execution
  - Resolved "Event loop is closed" and "Connection was closed in the middle of operation" errors
  - Improved error handling and retry logic for database operations

### UI/UX Improvements
- feat(theme): implement white/light theme for dashboard
  - Created .streamlit/config.toml with light theme configuration
  - Updated custom CSS to force white backgrounds and professional appearance
  - Added Inter font family and blue accent colors (#1f77b4)
  - Improved contrast and readability with dark text on white background

- fix(consumption): update node mapping to use correct database IDs
  - Updated consumption tab to use actual numeric node IDs from processing database
  - Fixed node mapping from string-based to numeric IDs (281492, 211514, etc.)
  - Updated SQL query to use main sensor_readings table instead of non-existent aggregates
  - Consumption tab now retrieves and displays real sensor data successfully

### Performance Improvements
- Enhanced connection pool management with proper validation
- Reduced async task conflicts through better context detection
- Improved query performance with correct database targeting
- Optimized background task scheduling to avoid Streamlit conflicts

### Data Access Fixes
- Fixed fallback data retrieval method to use correct database connection
- Updated consumption tab SQL queries to use existing sensor_readings table
- Added proper error handling for database connection issues
- Enhanced data retrieval with 192 sensor readings across 8 nodes

### Technical Changes
- Updated postgres_manager.py to respect environment variable configurations
- Enhanced hybrid_data_service.py with better Streamlit context detection
- Improved consumption_tab.py with correct database connection parameters
- Added global performance monitor instance for dashboard functionality
- Updated theme configuration with professional white theme styling

## [v1.2.3.11] - 2025-07-12

### Bug Fixes
- fix(arch): replace BigQuery direct access with HybridDataService in consumption tab
  - Fixed critical architecture violation where consumption tab was directly querying BigQuery
  - Implemented proper three-tier architecture (Redis → PostgreSQL → BigQuery) for operational dashboards
  - Fixed BigQuery project ID 'None' error that was preventing data access
  - Added architecture notification to show users the intelligent data routing
  - Significantly improved dashboard performance by using warm storage (PostgreSQL) instead of slow BigQuery queries
  - Fixed constructor parameters for ConsumptionTab component
  - Updated app.py to use new ConsumptionTab constructor without dependency injection parameters

### Technical Changes
- Replaced direct `SensorDataRepository` with `HybridDataService` in consumption tab
- Removed BigQuery repository dependencies from consumption analysis
- Enhanced error handling and fallback mechanisms for data access
- Added visual indicators showing three-tier architecture usage
- Improved data fetching to respect architectural boundaries

### Performance Improvements
- Dashboard queries now use PostgreSQL warm storage for operational data
- Avoided slow BigQuery queries through intelligent tier routing
- Better response times for consumption pattern analysis
- Reduced database load through proper architectural layering

### Documentation
- docs: update documentation for consumption tab architecture fix

## [v1.2.3.10] - 2025-07-12

### Bug Fixes
- fix(data): use historical data range and fix node selection in consumption patterns
  - Fixed empty data issue by using actual historical data range (November 2024 - March 2025) instead of current dates
  - Fixed node selection logic to properly handle "All Nodes" selection
  - Consumption patterns tab now displays real data with correct metrics and visualizations
  - Resolves showing 0.0 m³ for all consumption metrics and empty charts

### Documentation
- docs: update documentation for consumption patterns data range fix

## [v1.2.3.9] - 2025-07-12

### Bug Fixes
- fix(ui): add missing UUID import to consumption patterns tab
  - Fixed NameError where 'UUID' was not defined in consumption patterns analysis
  - Added missing `from uuid import UUID` import statement
  - Consumption patterns tab now loads correctly without errors
  - Resolves "Error fetching consumption data: name 'UUID' is not defined" error

### Documentation
- docs: update documentation for consumption patterns UUID import fix

## [v1.2.3.8] - 2025-07-12

### Bug Fixes
- fix(ui): remove invalid selected_nodes parameter from EfficiencyTab render call
  - Fixed TypeError where EfficiencyTab.render() was receiving unexpected keyword argument 'selected_nodes'
  - Removed selected_nodes parameter from efficiency tab call to match method signature
  - EfficiencyTab.render() only accepts time_range parameter
  - Resolves "TypeError: EfficiencyTab.render() got an unexpected keyword argument 'selected_nodes'" error

### Documentation
- docs: update documentation for EfficiencyTab render method signature fix

## [v1.2.3.7] - 2025-07-12

### Bug Fixes
- fix(viz): move opacity property to trace level for scattermapbox lines
  - Fixed invalid 'opacity' property in Plotly scattermapbox line configuration
  - Moved opacity from line dict to trace level where it belongs
  - Resolves "Invalid property specified for object of type plotly.graph_objs.scattermapbox.Line: 'opacity'" error
  - Geographic visualization now renders correctly without property errors

### Documentation
- docs: update documentation for Plotly scattermapbox opacity property fix

## [v1.2.3.6] - 2025-07-11

### Bug Fixes
- fix(ui): add state validation to district filter to prevent ValueError
  - Added validation for session state district_id against available districts
  - Prevents ValueError when invalid district names exist in session state
  - Gracefully defaults to first district when invalid state is encountered
  - Resolves crash when 'selargius' district name existed in session state

### Documentation
- docs: update documentation for district filter state validation fix

## [v1.2.3.5] - 2025-07-11

### Bug Fixes
- fix(streamlit): resolve ModuleNotFoundError by correcting sys.path
  - Added missing __init__.py files to make directories proper Python packages
  - Updated run_dashboard.sh to properly set PYTHONPATH
  - Created alternative launch scripts for better reliability
  - Ensured dashboard can run in both API and standalone modes

### Documentation
- docs: clarify run instructions after path fix
  - Added troubleshooting section for ModuleNotFoundError
  - Updated run commands to use the provided scripts
  - Explained why the error occurs and how to fix it

## [v1.2.3.4] - 2025-07-11

### Bug Fixes
- fix(anomaly-tab): add required time_range and selected_nodes arguments

### Documentation
- docs: update documentation for anomaly tab render arguments fix

## [v1.2.3.3] - 2025-07-11

### Bug Fixes
- fix(sidebar): use correct get_nodes method instead of generic get

### Documentation
- docs: update documentation for APIClient method fix

## [v1.2.3.2] - 2025-07-11

### Bug Fixes
- fix(overview): use timezone-aware datetime for comparisons

### Documentation
- docs: update documentation for timezone-aware datetime fix

## [v1.2.3.1] - 2025-07-11

### Bug Fixes
- fix(overview): handle division by zero when no nodes exist

### Documentation
- docs: update documentation for division by zero fix

## [v1.2.3.0] - 2025-07-11

### Features
- feat(processing): add containerized processing services with ML management
- feat(dashboard): integrate dashboard with processing services API
- feat(hybrid-architecture): implement PostgreSQL/TimescaleDB layer
- feat(etl): implement BigQuery to PostgreSQL ETL pipeline
- feat(dashboard): integrate hybrid architecture with Streamlit app
- feat: Add comprehensive performance monitoring and optimization
- feat: Implement caching to improve dashboard performance

### Bug Fixes
- fix(dashboard): complete node integration with sidebar updates
- fix(dashboard): update overview tab to display all 9 nodes
- fix(dashboard): handle missing sensor_readings_ml table gracefully
- fix: Resolve UnhashableParamError in Streamlit cache
- fix: Resolve import error in DataOptimizer
- fix: Initialize session state properly in PerformanceMonitor
- fix(etl): correct BigQuery table references and JSON serialization

### Documentation
- docs: reorganize and update documentation for v2.0.0 architecture
- docs: add comprehensive documentation for hybrid architecture

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

*   **V1.1.0 (2024-07-26):** Refactoring of the BigQuery module, improved queries, and new CI/CD pipeline for automated testing and deployment.
*   **V1.0.4 (2024-07-25):** Improved data normalization and handling of Quartucciu and Selargius datasets. Fixed bugs in the ML pipeline.
*   **V1.0.3 (2024-07-24):** Added new data quality analysis and reporting features. Enhanced anomaly detection algorithms.
*   **V1.0.2 (2024-07-23):** Dashboard performance optimization.
*   **V1.0.1 (2024-07-22):** Initial release with basic forecasting and data visualization capabilities.

## Future Developments

*   Integration with real-time data sources for live monitoring.
*   Advanced anomaly detection models with lower latency.
*   Expansion of the forecasting models to include more variables.

---

*This project is developed and maintained by AI-Gen Solutions.*
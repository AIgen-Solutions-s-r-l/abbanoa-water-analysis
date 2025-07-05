# Release Notes

## Summary of Manual Changes

This release includes enhancements to the Streamlit dashboard, adding time range filtering capabilities and real-time alert monitoring functionality.

### Affected Components

1. **Streamlit Dashboard Components**
   - `src/presentation/streamlit/components/anomaly_tab.py`
   - `src/presentation/streamlit/components/consumption_tab.py`
   - `src/presentation/streamlit/components/overview_tab.py`

### Changes Made

#### 1. Anomaly Tab Enhancements
- Added time range parameter to visualization methods:
  - `_render_anomaly_timeline(time_range)`
  - `_render_anomaly_types_chart(time_range)`
  - `_render_affected_nodes_chart(time_range)`
  - `_render_anomaly_list(time_range)`
- Improved anomaly data fetching to respect selected time ranges
- Enhanced real-time anomaly detection integration

#### 2. Consumption Tab Improvements
- Enhanced date range handling to respect actual data boundaries (Nov 13, 2024 - Mar 31, 2025)
- Fixed edge cases where requested time ranges could exceed available data
- Improved data validation to ensure queries stay within valid date ranges

#### 3. Overview Tab Real-Time Alerts
- Implemented comprehensive real-time alert system with severity levels:
  - **Critical**: Low pressure alerts (< 2.0 bar)
  - **Warning**: Flow spikes, high pressure, stale data
  - **Info**: Low flow periods, limited data points
- Added intelligent alert detection based on:
  - Pressure thresholds and anomalies
  - Flow rate deviations and spikes
  - Data quality and freshness checks
  - Node connectivity status
- Styled alerts with color-coded visual indicators

### Testing Performed

1. **Unit Tests**: All 34 unit tests passing
2. **Code Quality**: 
   - Applied black formatting to all Python files
   - Applied isort import sorting
   - Addressed flake8 linting warnings
3. **Manual Testing**:
   - Verified time range filtering works correctly
   - Confirmed alerts display properly with test data
   - Validated date boundary handling

### Known Limitations

- Some flake8 warnings remain (mostly line length)
- Alert thresholds are currently hardcoded and may need configuration
- Real-time alerts depend on data freshness in BigQuery

### Migration Requirements

None - these are non-breaking changes that enhance existing functionality.

### Code Style Updates

This release also includes comprehensive code formatting:
- Applied black formatter to ensure consistent style
- Organized imports with isort
- Improved code readability and maintainability
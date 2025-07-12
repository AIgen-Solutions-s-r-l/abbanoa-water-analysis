# Flake8 Violation Analysis Summary

## Overview
- **Total violations:** 1,397
- **Files with violations:** 96
- **Estimated effort:** ~8 hours (480 minutes)

## Top 10 Files with Most Violations

| File | Violations | Main Issues |
|------|------------|-------------|
| `src/presentation/streamlit/components/consumption_tab.py` | 68 | E501 (60), F401 (5), F841 (2), W291 (1) |
| `src/processing/service/ml_manager.py` | 54 | E501 (46), W291 (7), F401 (1) |
| `src/presentation/streamlit/components/enhanced_overview_tab.py` | 45 | E501 (38), F401 (5), W291 (1), F841 (1) |
| `src/presentation/streamlit/app.py` | 41 | E501 (36), F401 (3), W291 (2) |
| `src/presentation/streamlit/config/theme.py` | 41 | W293 (38), E501 (2), F841 (1) |
| `src/presentation/streamlit/components/efficiency_tab.py` | 40 | E501 (27), F401 (5), F811 (4), F541 (2), F841 (2) |
| `src/presentation/streamlit/components/kpi_dashboard_tab.py` | 39 | E501 (27), W293 (6), F401 (5), E722 (1) |
| `src/presentation/streamlit/components/water_quality_tab.py` | 35 | E501 (31), F401 (4) |
| `src/infrastructure/database/postgres_manager.py` | 31 | E501 (16), W291 (10), F401 (2), F841 (2), F541 (1) |
| `src/presentation/streamlit/components/anomaly_tab.py` | 31 | E501 (27), F401 (2), E722 (1), F841 (1) |

## Violation Type Distribution

| Error Code | Count | Percentage | Description |
|------------|-------|------------|-------------|
| E501 | 991 | 70.9% | Line too long (> 79 characters) |
| F401 | 181 | 13.0% | Module imported but unused |
| W291 | 97 | 6.9% | Trailing whitespace |
| W293 | 67 | 4.8% | Blank line contains whitespace |
| F841 | 34 | 2.4% | Local variable assigned but never used |
| F541 | 12 | 0.9% | f-string without placeholders |
| F811 | 8 | 0.6% | Redefinition of unused name |
| E722 | 3 | 0.2% | Bare except clause |
| E203 | 3 | 0.2% | Whitespace before colon |
| F821 | 1 | 0.1% | Undefined name |

## Module-Level Breakdown

| Module | Total Violations | Files Affected |
|--------|------------------|----------------|
| presentation | 727 | 31 |
| infrastructure | 321 | 23 |
| tests | 108 | 9 |
| processing | 94 | 4 |
| domain | 74 | 16 |
| application | 42 | 9 |
| api | 24 | 1 |
| config | 5 | 2 |
| shared | 2 | 1 |

## Priority Fix Order

### Priority 1: Critical Errors (F-series)
These errors can affect functionality and should be fixed first:

1. **`src/presentation/streamlit/components/reports_tab.py`** (14 critical errors)
   - F401: 4 (imported but unused)
   - F841: 10 (local variable assigned but never used)

2. **`src/presentation/streamlit/components/efficiency_tab.py`** (13 critical errors)
   - F401: 5, F541: 2, F811: 4, F841: 2

3. **`src/presentation/streamlit/components/sidebar_filters.py`** (9 critical errors)
   - F401: 6, F841: 3

4. **`src/presentation/streamlit/components/overview_tab.py`** (8 critical errors)
   - F401: 5, F811: 3

5. **`src/infrastructure/di_container.py`** (7 critical errors)
   - F401: 7

### Priority 2: Module-by-Module Style Fixes
After critical errors, fix style issues by tackling entire modules:

1. **Presentation module** (727 violations)
   - Focus on streamlit components first
   - Many E501 (line length) issues

2. **Infrastructure module** (321 violations)
   - Database and cache managers need attention
   - Mix of style and some critical errors

3. **Tests module** (108 violations)
   - Lower priority but important for maintainability
   - Performance tests have the most issues

### Quick Wins
Files with only E501 (line length) violations are easiest to fix:
- `src/presentation/api/endpoints/forecast_endpoint.py` (15 violations)
- `src/infrastructure/repositories/sensor_reading_repository.py` (11 violations)
- `src/domain/value_objects/quality_metrics.py` (8 violations)

## Recommendations

1. **Immediate Actions:**
   - Fix all F-series errors (critical functionality issues)
   - Set up pre-commit hooks to prevent new violations
   - Configure IDE/editor to show flake8 warnings

2. **Short-term (1-2 days):**
   - Fix all critical errors in presentation and infrastructure modules
   - Address quick wins (E501-only files)
   - Update CI/CD to fail on F-series errors

3. **Medium-term (1 week):**
   - Complete style fixes for presentation module
   - Address infrastructure module violations
   - Add flake8 to development workflow

4. **Configuration Considerations:**
   - Consider increasing line length limit to 100-120 characters (E501 is 71% of violations)
   - Add flake8 configuration file with project-specific rules
   - Set up automatic formatting with tools like Black
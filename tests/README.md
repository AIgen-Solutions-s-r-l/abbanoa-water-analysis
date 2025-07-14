# Water Infrastructure API Testing Suite

This directory contains a comprehensive testing framework for the Water Infrastructure API system, covering all 77 endpoints across 6 major API groups. The testing suite ensures production readiness through multiple layers of validation.

## 📁 Directory Structure

```
tests/
├── conftest.py                     # Global test configuration and fixtures
├── unit/                          # Unit tests for individual services
│   ├── test_consumption_service.py
│   ├── test_water_quality_service.py
│   ├── test_forecasting_service.py
│   ├── test_reports_service.py
│   ├── test_kpis_service.py
│   └── test_filters_service.py
├── integration/                   # API endpoint integration tests
│   ├── test_consumption_api.py
│   ├── test_water_quality_api.py
│   ├── test_forecasting_api.py
│   ├── test_reports_api.py
│   ├── test_kpis_api.py
│   └── test_filters_api.py
├── performance/                   # Performance and load tests
│   └── test_api_performance.py
├── e2e/                          # End-to-end workflow tests
│   └── test_complete_workflows.py
├── fixtures/                     # Test data and fixtures
├── utils/                        # Testing utilities
└── reports/                      # Generated test reports
```

## 🧪 Test Categories

### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual service methods in isolation
- **Coverage**: All business logic in service classes
- **Mock Strategy**: Mock external dependencies (database, APIs)
- **Execution Time**: Fast (< 1 second per test)
- **Test Count**: ~500+ tests across 6 services

**Key Features:**
- Service method validation
- Business logic verification
- Error handling scenarios
- Edge case testing
- Data validation
- Private method testing

### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test complete API request/response cycles
- **Coverage**: All 77 API endpoints
- **Mock Strategy**: Mock data services, test API layer
- **Execution Time**: Medium (1-5 seconds per test)
- **Test Count**: ~200+ tests across 6 API groups

**Key Features:**
- HTTP status code validation
- Response schema validation
- Request parameter validation
- Error response handling
- Authentication testing
- Pagination testing

### 3. Performance Tests (`tests/performance/`)
- **Purpose**: Validate performance under load
- **Coverage**: All critical API endpoints
- **Load Testing**: Concurrent requests, stress testing
- **Execution Time**: Long (10-60 seconds per test)
- **Test Count**: ~50+ performance scenarios

**Key Features:**
- Response time validation
- Throughput measurement
- Memory usage monitoring
- Concurrent request handling
- Database connection pooling
- Cache performance
- Resource cleanup

### 4. End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete business workflows
- **Coverage**: Cross-service workflows
- **Integration**: Multiple APIs working together
- **Execution Time**: Long (30-120 seconds per test)
- **Test Count**: ~30+ complete workflows

**Key Features:**
- Daily monitoring workflow
- Incident response workflow
- Predictive maintenance workflow
- Regulatory compliance workflow
- Executive dashboard workflow
- Data integration workflow

## 🚀 Getting Started

### Installation

1. **Install testing dependencies:**
```bash
pip install -r requirements-test.txt
```

2. **Set up test environment:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
mkdir -p tests/reports
```

### Quick Start

1. **Run smoke tests (fastest validation):**
```bash
python run_tests.py --mode smoke
```

2. **Run unit tests:**
```bash
python run_tests.py --mode unit
```

3. **Run integration tests:**
```bash
python run_tests.py --mode integration
```

4. **Run full test suite:**
```bash
python run_tests.py --mode full
```

### Advanced Usage

1. **Run tests for specific service:**
```bash
python run_tests.py --service consumption
python run_tests.py --service quality
python run_tests.py --service kpis
```

2. **Run performance tests:**
```bash
python run_tests.py --mode performance
```

3. **Run tests in parallel:**
```bash
python run_tests.py --parallel
```

4. **Generate coverage report:**
```bash
python run_tests.py --coverage
```

## 📊 Test Configuration

### Pytest Configuration (`pytest.ini`)

The testing framework is configured with:
- **Coverage**: 80% minimum threshold
- **Reporting**: HTML, XML, and JUnit formats
- **Markers**: Organized test categorization
- **Async Support**: Full asyncio testing
- **Timeout**: 300 seconds maximum per test

### Performance Thresholds

| Metric | Threshold | Notes |
|--------|-----------|-------|
| Response Time | 5000ms | Maximum acceptable response time |
| Memory Usage | 512MB | Maximum memory increase during tests |
| Throughput | 100 RPS | Minimum requests per second |
| Error Rate | 1% | Maximum acceptable error rate |
| P95 Response Time | 3000ms | 95th percentile response time |
| P99 Response Time | 4000ms | 99th percentile response time |

## 🎯 Test Markers

Tests are organized using pytest markers for selective execution:

```bash
# Run by test type
pytest -m unit
pytest -m integration
pytest -m performance
pytest -m e2e

# Run by API group
pytest -m consumption
pytest -m quality
pytest -m forecasting
pytest -m reports
pytest -m kpis
pytest -m filtering

# Run by characteristics
pytest -m slow
pytest -m smoke
pytest -m security
```

## 📈 Test Data Strategy

### Mock Data Generation
- **Realistic Data**: Generated with proper patterns and relationships
- **Large Datasets**: 100K+ records for performance testing
- **Time Series**: Chronological data with trends and seasonality
- **Edge Cases**: Boundary conditions and error scenarios

### Test Fixtures
- **Hybrid Service Mocks**: Simulated data service responses
- **Performance Data**: Large datasets for load testing
- **Error Scenarios**: Failure condition simulation
- **Time Ranges**: Standard date ranges for consistency

## 🔍 Test Execution Modes

### 1. Development Mode
```bash
# Quick validation during development
python run_tests.py --mode smoke
pytest tests/unit/test_consumption_service.py -v
```

### 2. CI/CD Mode
```bash
# Comprehensive testing for CI/CD
python run_tests.py --mode full --parallel
```

### 3. Performance Mode
```bash
# Performance validation
python run_tests.py --mode performance
pytest tests/performance/ -v --tb=short
```

### 4. Debug Mode
```bash
# Detailed debugging
pytest tests/unit/test_specific.py -v -s --pdb
```

## 📊 Reporting and Analysis

### Generated Reports

1. **HTML Reports**: Interactive test results
   - Location: `tests/reports/`
   - Includes: Pass/fail status, execution times, error details

2. **Coverage Reports**: Code coverage analysis
   - Location: `htmlcov/`
   - Includes: Line coverage, branch coverage, missing lines

3. **Performance Reports**: Response time and throughput analysis
   - Location: `tests/reports/performance-report.html`
   - Includes: Response time distributions, memory usage, throughput metrics

4. **JUnit XML**: CI/CD integration
   - Location: `tests/reports/*.xml`
   - Compatible with Jenkins, GitHub Actions, etc.

### Key Metrics Tracked

- **Test Coverage**: Line and branch coverage percentages
- **Response Times**: Mean, median, P95, P99 response times
- **Throughput**: Requests per second under load
- **Memory Usage**: Peak memory consumption
- **Error Rates**: Percentage of failed requests
- **Test Execution Time**: Total time for test suites

## 🛠️ Fixtures and Utilities

### Global Fixtures (`conftest.py`)
- Service instances for all API services
- Mock data generators with realistic patterns
- Performance tracking utilities
- Test configuration objects
- Database and API mocking utilities

### Test Utilities
- **APITestUtils**: Common API testing patterns
- **PerformanceTracker**: Response time measurement
- **ErrorSimulator**: Failure condition simulation
- **TestDataGenerator**: Realistic test data creation

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

2. **Async Test Issues**
```bash
# Install asyncio support
pip install pytest-asyncio
```

3. **Coverage Issues**
```bash
# Install coverage extras
pip install coverage[toml]
```

4. **Performance Test Failures**
```bash
# Increase timeout for slow environments
pytest tests/performance/ --timeout=600
```

### Debug Commands

1. **Verbose output:**
```bash
pytest tests/ -v -s
```

2. **Stop on first failure:**
```bash
pytest tests/ -x
```

3. **Run specific test with debugger:**
```bash
pytest tests/unit/test_consumption_service.py::TestConsumptionService::test_method -v -s --pdb
```

4. **Show test durations:**
```bash
pytest tests/ --durations=10
```

## 📋 Testing Checklist

### Before Committing Code
- [ ] All unit tests pass
- [ ] Integration tests pass for modified APIs
- [ ] Code coverage meets 80% threshold
- [ ] No performance regressions
- [ ] All linting checks pass

### Before Deployment
- [ ] Full test suite passes
- [ ] Performance tests meet thresholds
- [ ] End-to-end workflows complete successfully
- [ ] Security tests pass
- [ ] Load tests demonstrate acceptable performance

### Regular Maintenance
- [ ] Update test data quarterly
- [ ] Review and update performance thresholds
- [ ] Add tests for new features
- [ ] Refactor tests for maintainability
- [ ] Update dependencies

## 🎯 Testing Best Practices

1. **Test Organization**
   - One test file per service
   - Descriptive test names
   - Logical test grouping
   - Consistent fixture usage

2. **Mock Strategy**
   - Mock external dependencies
   - Use realistic test data
   - Test error conditions
   - Verify mock interactions

3. **Performance Testing**
   - Set realistic thresholds
   - Test under various loads
   - Monitor resource usage
   - Test degradation scenarios

4. **Maintenance**
   - Regular test review
   - Update for API changes
   - Refactor for clarity
   - Remove obsolete tests

## 📞 Support

For questions about the testing framework:
1. Check this documentation
2. Review test examples in the codebase
3. Run tests with verbose output for debugging
4. Consult team testing guidelines

## 🔄 Continuous Integration

This testing suite is designed for seamless CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Test Suite
  run: |
    pip install -r requirements-test.txt
    python run_tests.py --mode full --parallel
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: tests/reports/coverage.xml
```

The comprehensive testing framework ensures our Water Infrastructure API meets enterprise-grade quality standards with 77 endpoints fully tested across multiple dimensions of functionality, performance, and reliability. 
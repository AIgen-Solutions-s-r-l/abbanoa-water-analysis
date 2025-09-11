# Error Scenario Tests Documentation

## Overview
This module provides comprehensive error scenario testing for all API endpoints, covering 4xx and 5xx error responses in mock mode as required by Issue #11.

## Test Coverage

### Client Errors (4xx)

#### 400 Bad Request
- Invalid query parameters (negative values, excessive ranges)
- Missing required fields in POST requests
- Invalid data types
- Empty required fields

#### 404 Not Found
- Non-existent resources (nodes, zones, reports)
- Invalid resource IDs
- Deleted or archived resources

#### 422 Unprocessable Entity
- Type validation errors
- Schema validation failures
- Business logic violations

### Server Errors (5xx)

#### 500 Internal Server Error
- Database connection failures
- Query execution errors
- Unexpected exceptions
- Calculation errors

#### 503 Service Unavailable
- Database timeout
- Service dependencies down
- Resource exhaustion

### Authentication/Authorization Errors

#### 401 Unauthorized
- Missing authentication
- Invalid tokens
- Expired sessions

#### 403 Forbidden
- Insufficient permissions
- Resource access denied

## Test Organization

### Test Classes
- `TestBadRequestErrors` - 400 scenarios
- `TestNotFoundErrors` - 404 scenarios
- `TestServerErrors` - 500 scenarios
- `TestAuthenticationErrors` - 401/403 scenarios
- `TestValidationErrors` - 422 scenarios
- `TestTimeoutErrors` - Timeout scenarios
- `TestCascadingErrors` - Multiple failure scenarios

### Parameterized Tests
Using `@pytest.mark.parametrize` for:
- Testing multiple endpoints with same error type
- Different parameter combinations
- Various error conditions

## Running Tests

### All Error Tests
```bash
python3 -m pytest tests/integration/test_error_scenarios_comprehensive.py -v
```

### Specific Error Category
```bash
# Test only 404 errors
python3 -m pytest tests/integration/test_error_scenarios_comprehensive.py::TestNotFoundErrors -v

# Test only 500 errors
python3 -m pytest tests/integration/test_error_scenarios_comprehensive.py::TestServerErrors -v
```

### With Coverage
```bash
coverage run -m pytest tests/integration/test_error_scenarios_comprehensive.py
coverage report --include="src/presentation/api/endpoints/*"
```

### In CI Pipeline
```bash
./scripts/run_error_tests.sh
```

## Mock Mode Configuration

### Environment Variables
- `API_MODE=mock` - Enable mock mode
- `MOCK_ERRORS=true` - Enable error simulation
- `API_BASE` - API base URL

### Mock Strategies
1. **Database Errors**: Mock `get_db_connection` to raise exceptions
2. **Validation Errors**: Send invalid data types/formats
3. **Not Found**: Query non-existent resources
4. **Timeouts**: Simulate slow responses

## Test Patterns

### Database Error Simulation
```python
@patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
def test_database_error(mock_get_db_connection):
    mock_get_db_connection.side_effect = asyncpg.PostgresConnectionError("Failed")
    # Test endpoint behavior
```

### Validation Error Testing
```python
@pytest.mark.parametrize("params", [
    {"hours": -1},  # Negative value
    {"hours": "not_a_number"},  # Type error
])
def test_validation(params):
    resp = httpx.get(url, params=params)
    assert resp.status_code in [400, 422]
```

### Cascading Failures
```python
def test_partial_failure():
    # Mock partial success/failure
    mock_conn.fetchrow.side_effect = [
        data,  # First query succeeds
        Exception("Failed"),  # Second fails
    ]
```

## Expected Behaviors

### Error Response Format
All error responses should include:
```json
{
    "detail": "Error description",
    "status_code": 400,
    "headers": {}
}
```

### FastAPI Validation Errors (422)
```json
{
    "detail": [
        {
            "loc": ["query", "param_name"],
            "msg": "Error message",
            "type": "error_type"
        }
    ]
}
```

## CI Integration

### GitHub Actions
The error tests are integrated in `.github/workflows/api-integration.yml`:
- Runs after standard integration tests
- Uses mock mode to avoid database dependencies
- Non-blocking (failures logged but don't fail CI)

### Local CI Simulation
```bash
export API_MODE=mock
export MOCK_ERRORS=true
./scripts/run_error_tests.sh
```

## Maintenance

### Adding New Error Tests
1. Identify error scenario
2. Add test to appropriate class
3. Use parameterization for multiple endpoints
4. Update documentation

### Updating for New Endpoints
1. Add endpoint to parameterized tests
2. Create specific error scenarios if needed
3. Verify error handling implementation

## Best Practices

1. **Use Mocks**: Always mock external dependencies
2. **Test Boundaries**: Include edge cases and limits
3. **Parameterize**: Reduce code duplication
4. **Document Expected**: Clear assertions about expected behavior
5. **Non-Breaking**: Error tests shouldn't break CI for unimplemented features

## Future Enhancements

- [ ] Add performance degradation tests
- [ ] Test error recovery mechanisms
- [ ] Add chaos engineering scenarios
- [ ] Test circuit breaker patterns
- [ ] Add distributed tracing for errors
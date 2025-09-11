# Centralized API Core Utilities

## Overview
This module provides centralized configuration and utilities for all API endpoints, eliminating code duplication and providing consistent error handling across the application.

## Modules

### `database.py`
Centralized database configuration and connection management.

#### Key Components:
- **DatabaseConfig**: Centralized configuration from environment variables
- **get_db_connection()**: Async function to get database connection
- **get_db_pool()**: Create connection pool for better performance
- **@with_db_connection**: Decorator for automatic connection management
- **DatabaseConnectionManager**: Context manager for connections

#### Usage Examples:

```python
from src.presentation.api.core.database import get_db_connection

# Simple connection
async def my_endpoint():
    conn = await get_db_connection()
    try:
        result = await conn.fetch("SELECT ...")
        return result
    finally:
        await conn.close()

# With decorator
from src.presentation.api.core.database import with_db_connection

@with_db_connection
async def my_endpoint(conn, param1, param2):
    result = await conn.fetch("SELECT ...")
    return result  # Connection auto-closed

# With context manager
from src.presentation.api.core.database import DatabaseConnectionManager

async def my_endpoint():
    async with DatabaseConnectionManager() as conn:
        result = await conn.fetch("SELECT ...")
        return result  # Connection auto-closed
```

### `error_handling.py`
Centralized error handling decorators and utilities.

#### Key Components:
- **@handle_database_errors**: Decorator for database error handling
- **@handle_api_errors**: Generic API error handling with custom defaults
- **ErrorResponse**: Standard error response helpers

#### Usage Examples:

```python
from src.presentation.api.core.error_handling import handle_database_errors

@router.get("/endpoint")
@handle_database_errors
async def my_endpoint():
    conn = await get_db_connection()
    # Database errors automatically converted to HTTP responses
    
# Custom error handling
from src.presentation.api.core.error_handling import handle_api_errors

@handle_api_errors(default_status=503, default_message="Service unavailable")
async def my_endpoint():
    # Custom error handling

# Standard error responses
from src.presentation.api.core.error_handling import ErrorResponse

if not resource:
    raise ErrorResponse.not_found("Resource")
```

## Benefits

### Before (Duplicated Code)
Each router file had:
```python
# Repeated in every router
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'abbanoa_processing'),
    'user': os.getenv('POSTGRES_USER', 'abbanoa_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'abbanoa_secure_pass')
}

async def get_db_connection():
    return await asyncpg.connect(**DB_CONFIG)
```

### After (Centralized)
```python
from src.presentation.api.core.database import get_db_connection
from src.presentation.api.core.error_handling import handle_database_errors

@router.get("/endpoint")
@handle_database_errors
async def my_endpoint():
    conn = await get_db_connection()
    # Use connection...
```

## Advantages
1. **DRY Principle**: No code duplication
2. **Single Source of Truth**: One place to update configuration
3. **Consistent Error Handling**: Same error responses across all endpoints
4. **Easier Testing**: Mock one module instead of many
5. **Better Maintainability**: Changes in one place affect all endpoints

## Migration Guide

### Refactoring Existing Routers
1. Remove local `DB_CONFIG` dictionary
2. Remove local `get_db_connection()` function
3. Update imports:
```python
from src.presentation.api.core.database import get_db_connection
from src.presentation.api.core.error_handling import handle_database_errors
```
4. Add decorators to endpoints using database:
```python
@router.get("/endpoint")
@handle_database_errors
async def my_endpoint():
    ...
```
5. Replace `HTTPException(status_code=404, ...)` with `ErrorResponse.not_found(...)`

## Environment Variables
Configuration is read from environment:
- `POSTGRES_HOST` (default: localhost)
- `POSTGRES_PORT` (default: 5432)
- `POSTGRES_DB` (default: abbanoa_processing)
- `POSTGRES_USER` (default: abbanoa_user)
- `POSTGRES_PASSWORD` (default: abbanoa_secure_pass)

## Error Handling

### Automatic Conversions
- `asyncpg.PostgresConnectionError` → 503 Service Unavailable
- `asyncpg.PostgresError` → 500 Internal Server Error
- `asyncpg.DataError` → 400 Bad Request
- `ValueError` → 400 Bad Request
- `KeyError` → 400 Bad Request (missing field)
- Other exceptions → 500 Internal Server Error

### Custom Error Responses
Use `ErrorResponse` class for consistent error formats:
- `ErrorResponse.bad_request(detail)`
- `ErrorResponse.not_found(resource)`
- `ErrorResponse.unauthorized(detail)`
- `ErrorResponse.forbidden(detail)`
- `ErrorResponse.conflict(detail)`
- `ErrorResponse.internal_server_error(detail)`
- `ErrorResponse.service_unavailable(detail)`

## Testing

### Mocking in Tests
```python
from unittest.mock import patch, AsyncMock

@patch('src.presentation.api.core.database.get_db_connection')
def test_my_endpoint(mock_get_db_connection):
    mock_conn = AsyncMock()
    mock_get_db_connection.return_value = mock_conn
    # Test endpoint...
```

## Files Refactored
- ✅ dashboard_router.py
- ✅ anomaly_router.py
- ⏳ infrastructure_router.py
- ⏳ network_router.py
- ⏳ nodes_router.py
- ⏳ pressure_router.py
- ⏳ efficiency_router.py
- ⏳ consumption_analytics_router.py
- ⏳ reports_router.py

## Related Issues
- Issue #13: Extract mock gating to shared helper/decorator
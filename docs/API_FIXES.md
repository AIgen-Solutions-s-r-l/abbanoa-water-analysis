# API Fixes and Updates

## Status Endpoint Timezone Fix (2025-07-11)

### Issue
The `/api/v1/status` endpoint was returning HTTP 500 with error:
```
{"detail":"can't subtract offset-naive and offset-aware datetimes"}
```

### Root Cause
PostgreSQL returns timezone-aware datetime objects (with UTC timezone), but the code was comparing them with naive datetime objects from `datetime.now()`.

### Solution
1. Added `timezone` import to the API module
2. Updated all `datetime.now()` calls to `datetime.now(timezone.utc)`
3. Added proper timezone handling in the status endpoint when comparing timestamps
4. Added volume mount for source code in docker-compose to enable hot-reloading during development

### Changes Made
- Updated `src/api/main.py` to use timezone-aware datetime objects throughout
- Added `- ./src:/app/src:ro` volume mount to the API service in `docker-compose.processing.yml`

### Testing
All API endpoints now return successful responses:
- `/health` - 200 OK
- `/api/v1/nodes` - 200 OK
- `/api/v1/dashboard/summary` - 200 OK
- `/api/v1/status` - 200 OK (previously 500)

The dashboard at https://curator.aigensolutions.it is now fully functional without authentication errors.
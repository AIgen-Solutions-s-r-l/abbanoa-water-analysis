# API Wait/Retry Mechanism Documentation

## Overview
Robust retry mechanism with exponential backoff for waiting for API readiness in CI/CD pipelines. Replaces fixed `sleep` delays with intelligent polling.

## Scripts

### `wait_for_api.sh`
Full-featured wait script with detailed logging and diagnostics.

**Usage:**
```bash
./scripts/wait_for_api.sh [URL] [MAX_ATTEMPTS] [INITIAL_WAIT]
```

**Parameters:**
- `URL`: API health endpoint (default: `http://localhost:8000/health`)
- `MAX_ATTEMPTS`: Maximum retry attempts (default: 30)
- `INITIAL_WAIT`: Initial wait time in seconds (default: 1)

**Features:**
- Exponential backoff (1s → 2s → 4s → 8s cap)
- Colored output for better visibility
- Diagnostic information on failure
- Process checking with `lsof`
- Total time tracking

### `ci_wait_for_api.sh`
Lightweight version optimized for CI environments.

**Usage:**
```bash
./scripts/ci_wait_for_api.sh [URL] [MAX_WAIT_SECONDS]
```

**Features:**
- Progressive wait strategy (faster initially)
- Minimal dependencies
- Compact output for CI logs
- Basic diagnostics on failure

## CI Integration

### GitHub Actions
The retry mechanism is integrated directly in `.github/workflows/api-integration.yml`:

```yaml
- name: Wait for API to be ready
  run: |
    MAX_ATTEMPTS=30
    WAIT_TIME=1
    while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
      if curl -sf "$API_URL" > /dev/null 2>&1; then
        echo "✅ API ready after attempt $ATTEMPT"
        break
      fi
      # Exponential backoff logic...
    done
```

## Benefits

### Before (Fixed Sleep)
```bash
sleep 5  # Always waits 5 seconds
```
- ⏱️ Fixed 5-second wait regardless of actual startup time
- ❌ May fail if API takes > 5 seconds
- ❌ Wastes time if API starts in < 5 seconds

### After (Retry with Backoff)
```bash
./scripts/wait_for_api.sh
```
- ✅ Exits immediately when API is ready (saves CI time)
- ✅ Handles variable startup times
- ✅ Provides diagnostic info on failure
- ✅ Configurable timeout and retry strategy

## Retry Strategy

### Exponential Backoff
```
Attempt 1: Wait 1s
Attempt 2: Wait 2s  
Attempt 3: Wait 4s
Attempt 4: Wait 8s (capped)
Attempt 5+: Wait 8s (max)
```

### Total Wait Times
- Best case (API ready immediately): ~0s
- Typical case (API ready in 2-3s): 2-3s
- Worst case (30 attempts): ~90s

## Exit Codes
- `0`: API is ready
- `1`: Timeout - API not ready after max attempts
- `130`: Script interrupted (SIGINT/SIGTERM)

## Examples

### Local Development
```bash
# Start API and wait for it
uvicorn app:app &
./scripts/wait_for_api.sh

# Custom endpoint and timeout
./scripts/wait_for_api.sh http://localhost:3000/status 60 2
```

### CI Pipeline
```bash
# In GitHub Actions or other CI
nohup start-server &
./scripts/ci_wait_for_api.sh http://localhost:8000/health 30
```

### Docker Compose
```bash
docker-compose up -d api
./scripts/wait_for_api.sh http://localhost:8000/health
docker-compose run tests
```

## Troubleshooting

### API Never Becomes Ready
1. Check if process is running: `ps aux | grep uvicorn`
2. Check port binding: `lsof -i :8000`
3. Check logs: `tail -f logs/api.log`
4. Try manual curl: `curl -v http://localhost:8000/health`

### Script Times Out Too Early
Increase max attempts:
```bash
./scripts/wait_for_api.sh http://localhost:8000/health 60 1
```

### Different Health Endpoint
Specify custom URL:
```bash
./scripts/wait_for_api.sh http://localhost:8000/api/v1/status
```

## Best Practices

1. **Use in CI/CD**: Replace all fixed `sleep` commands
2. **Set Reasonable Timeouts**: 30-60s for most services
3. **Check Correct Endpoint**: Use actual health/ready endpoint
4. **Log Output**: Capture script output for debugging
5. **Handle Failures**: Add fallback or diagnostic commands

## Related
- Issue #12: Replace sleep with retry probe in API workflow
- CI/CD best practices for service readiness
- Health check endpoint implementation
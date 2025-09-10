# Rollback Plan - v2.4.0

## Overview
This document provides step-by-step instructions for rolling back v2.4.0 (Quality Metrics Configuration) if critical issues are discovered post-deployment.

## Rollback Triggers

### Automatic Triggers
- [ ] Error rate > 5% for 2 minutes
- [ ] P95 latency > 1000ms for 5 minutes
- [ ] Health check failures > 3 consecutive
- [ ] Pod crash loops detected

### Manual Triggers
- [ ] Configuration loading failures
- [ ] Incorrect threshold values causing business impact
- [ ] Performance degradation > 20%
- [ ] Critical bug in configuration validation

## Rollback Strategies

### Strategy 1: Instant Rollback with PM2 (< 30 seconds)

**Use when**: Services are running but configuration is problematic

```bash
# 1. Restore previous PM2 saved state
pm2 resurrect

# 2. Reload with previous environment
pm2 reload ecosystem.config.js --update-env

# 3. Verify services
pm2 status
pm2 logs --lines 50

# 4. Check health
curl -f http://localhost:8000/health
```

### Strategy 2: Git Revert (< 5 minutes)

**Use when**: Code changes need to be reverted

```bash
# 1. Identify merge commit
MERGE_COMMIT=$(git log --merges -n 1 --pretty=format:"%H")

# 2. Revert the merge
git revert -m 1 $MERGE_COMMIT

# 3. Push revert
git push origin main

# 4. Redeploy
pm2 deploy ecosystem.config.js production

# 5. Verify deployment
pm2 status
curl -f http://localhost:8000/health
```

### Strategy 3: Configuration Override (< 2 minutes)

**Use when**: Only configuration values need adjustment

```bash
# 1. Override problematic configuration values
export QUALITY_THRESHOLDS_TEMPERATURE__OPTIMAL=15.0
export QUALITY_THRESHOLDS_PRESSURE__MINIMUM=2.0
export QUALITY_THRESHOLDS_COMPLIANCE__QUALITY_WARNING=90.0

# 2. Reload services
pm2 reload all --update-env

# 3. Verify configuration
python3 -c "
from src.config.quality_thresholds import get_quality_config, reset_config
reset_config()
config = get_quality_config()
print(f'Temperature: {config.temperature.optimal}')
print(f'Pressure: {config.pressure.minimum}')
"

# 4. Monitor services
pm2 monit
```

### Strategy 4: Full Restoration (< 30 minutes)

**Use when**: Database or system-wide issues

```bash
# 1. Stop all services
pm2 stop all

# 2. Backup current state
tar -czf backup_$(date +%s).tar.gz /var/www/abbanoa-water-analysis

# 3. Checkout previous version
git checkout v2.3.0

# 4. Restore database if needed
if [ -f "backup/db-latest.sql" ]; then
    psql $DATABASE_URL < backup/db-latest.sql
fi

# 5. Reinstall dependencies
pip install -r requirements.txt
cd frontend && npm ci && cd ..

# 6. Start services
pm2 start ecosystem.config.js

# 7. Verify system
./scripts/health_check.sh
```

## Verification Steps

After rollback, verify:

### 1. Service Health
```bash
# Check PM2 processes
pm2 status

# Check API health
curl -f http://localhost:8000/health

# Check frontend
curl -f http://localhost:3001
```

### 2. Configuration Status
```bash
# Verify configuration is loading
python3 -c "
from src.config.quality_thresholds import get_quality_config
config = get_quality_config()
print('Config loaded successfully')
print(f'Using defaults: {config.temperature.optimal == 15.0}')
"
```

### 3. Metrics
```bash
# Check error rates
pm2 web
# Access http://localhost:9615

# Check logs for errors
pm2 logs --err --lines 100
```

### 4. Database
```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT COUNT(*) FROM sensor_readings;"
```

## Communication Plan

### During Rollback

**Slack Alert**:
```
🔄 ROLLBACK IN PROGRESS - v2.4.0
Reason: [Brief description]
Impact: [Services affected]
ETA: [Estimated completion time]
Status: https://status.abbanoa.example.com
```

### After Rollback

**Team Notification**:
```
✅ ROLLBACK COMPLETE - v2.4.0
Duration: [Time taken]
Current Version: [Reverted version]
Services: All operational
Next Steps: Root cause analysis scheduled

Incident Report: [Link to document]
```

## Post-Rollback Actions

1. **Create Incident Report**
   - Document timeline
   - Identify root cause
   - List affected services
   - Calculate impact metrics

2. **Root Cause Analysis**
   - Schedule within 24 hours
   - Include all stakeholders
   - Document findings

3. **Fix Forward Plan**
   - Address identified issues
   - Add missing tests
   - Update rollback procedures

4. **Update Documentation**
   - Revise deployment procedures
   - Update configuration guide
   - Add lessons learned

## Emergency Contacts

- **Platform Team Lead**: [Contact]
- **DevOps On-Call**: [Pager]
- **Product Owner**: [Contact]
- **CTO**: [Contact for P0 incidents]

## Rollback Testing

Test rollback procedures monthly:
1. Deploy to staging
2. Execute rollback
3. Verify recovery
4. Document issues
5. Update procedures

## Configuration Backup

Before deployment, backup current configuration:
```bash
# Backup configuration
cp config/quality_thresholds.yaml config/quality_thresholds.yaml.backup

# Backup environment
env | grep QUALITY_THRESHOLDS > env_backup.txt
```

## Monitoring During Rollback

Key metrics to watch:
- Error rate
- Response time
- Memory usage
- CPU utilization
- Active connections
- Configuration load errors

## Success Criteria

Rollback is successful when:
- [ ] All services are running
- [ ] Error rate < 0.5%
- [ ] P95 latency < 200ms
- [ ] Health checks passing
- [ ] No configuration errors
- [ ] Users can access all features

---

**Document Version**: 1.0
**Last Updated**: December 10, 2024
**Owner**: Platform Team
# 🚨 Rollback Quick Reference

## Emergency Rollback (< 2 minutes)

### 1. Stop Current Version
```bash
pm2 stop all
# OR
docker-compose down
```

### 2. Rollback Code
```bash
# Get previous version
git checkout v2.9.0  # Replace with last stable version
# OR
git revert HEAD && git push
```

### 3. Restart Services
```bash
pm2 restart all
# OR
docker-compose up -d
```

### 4. Verify
```bash
curl http://localhost:8000/health
pm2 status
```

---

## Rollback Decision Tree

```
System Down?
├─ YES → Emergency Rollback (above)
└─ NO → Check Error Rate
    ├─ > 5% → Rollback Code
    └─ < 5% → Check Performance
        ├─ Degraded → Scale Up First
        └─ OK → Monitor & Debug

Database Issues?
├─ Connection Failed → Restart DB
├─ Migration Failed → Rollback Migration
└─ Data Corrupted → Restore Backup
```

## Common Scenarios

### Scenario 1: API Returns 500 Errors
```bash
# Quick fix
pm2 restart abbanoa-postgres-api
# If persists
git checkout HEAD~1
pm2 restart all
```

### Scenario 2: Database Migration Failed
```bash
psql -U abbanoa_user -d abbanoa_processing
\i migrations/rollback/latest_rollback.sql
\q
pm2 restart all
```

### Scenario 3: Frontend Not Loading
```bash
cd frontend
git checkout HEAD~1
npm run build
pm2 restart abbanoa-frontend
```

### Scenario 4: High Memory Usage
```bash
pm2 restart all --update-env
# If persists
pm2 delete all
pm2 start ecosystem.config.js
```

## Verification Checklist
- [ ] Health endpoint responds: `curl localhost:8000/health`
- [ ] Dashboard loads: `curl localhost:3001`
- [ ] No errors in logs: `pm2 logs --err --lines 50`
- [ ] Database accessible: `psql -c "SELECT 1"`
- [ ] Redis running: `redis-cli ping`

## Contact for Help
- **On-Call**: Check PagerDuty
- **Slack**: #incidents
- **Escalation**: DevOps Lead

---
*Print this page and keep near your workstation*
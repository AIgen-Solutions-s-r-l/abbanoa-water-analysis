# Product/Engineering Tasks Backlog

Legend: [ ] TODO · [x] Done · P0=Critical, P1=High, P2=Medium

## P0 – Critical
- [ ] API: Fix `/api/v1/dashboard/summary` queries to match real DB schema (`water_infrastructure.*` or current tables). Acceptance: 200 OK with non-empty payload on staging DB.
- [ ] API: Fix `/api/v1/anomalies` queries to match real DB schema. Acceptance: 200 OK with ≤500ms p95 on staging.
- [ ] Secrets: Remove hardcoded DB creds from `app_postgres.py`; move to PM2 env/secrets. Acceptance: PM2 config holds POSTGRES_* and service boots.
- [ ] Health: Add `/health` deep check (DB connectivity + migrations ok). Acceptance: returns 200 with status/details.

## P1 – High
- [ ] UI Error Handling: Show clear errors and retry/backoff (no mock) for Dashboard/Anomalies widgets. Acceptance: 3 failed calls → user-visible banner + retry.
- [ ] Observability: Structured logging + request-id on API; log error rate. Acceptance: logs include trace ids, endpoint, latency.
- [ ] CI/CD: Pipeline runs FE build, BE tests, API smoke against staging DB. Acceptance: green pipeline required for merge to main.
- [ ] Rate limiting: Add light rate limit on `/api/proxy/v1/*`. Acceptance: burst control without blocking normal UX.

## P2 – Medium
- [ ] Performance: Review indices and add EXPLAIN plan docs for dashboard/anomalies queries. Acceptance: p95 < 300ms with realistic dataset.
- [ ] Security: Add auth (API key/JWT) for `/api/v1/*` as per policy. Acceptance: protected endpoints, 401/403 paths covered by tests.
- [ ] Cleanup: Remove remaining legacy artifacts (sqlalchemy_server, Dockerfile.sqlalchemy, ecosystem entries, docs). Acceptance: repo free of unused code; docs updated.
- [ ] Docs: Update README/DEPLOYMENT_NOTES with env vars, runbook, and PM2 steps. Acceptance: newcomer can deploy in ≤30 minutes.
- [ ] Release management: Changelog + semantic version bump; tag release. Acceptance: created Git tag and release notes.

## Nice-to-have
- [ ] Frontend telemetry: basic Web Vitals + error boundaries reporting.
- [ ] Feature flags for toggling new analytics endpoints per env.

## Notes
- Owner(s): PM to assign per squad.
- Environments: dev (PM2), staging (TimescaleDB), prod.
- Definition of Done: code, tests, docs, CI green, deployed to staging.



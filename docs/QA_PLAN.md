# QA Plan: API Integration (Mock Mode)

Scope:
- Add USE_MOCK_API gate in endpoints for CI.
- Add GitHub Actions workflow to run black-box API tests without real DB.

Verification Steps:
1) CI triggers on PR; workflow api-integration runs.
2) API starts with USE_MOCK_API=true; health endpoint 200.
3) Tests in tests/integration/test_dashboard_anomalies_int.py pass.

Risks/Notes:
- Mock only in CI via env; no production impact.

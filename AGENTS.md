# Repository Guidelines

## Project Structure & Modules
- Backend Python in `src/` (FastAPI, DDD layers: `api/`, `application/`, `domain/`, `infrastructure/`, `schemas/`, `shared/`).
- Frontend in `frontend/` (Next.js). Tests in `tests/` with `unit/`, `integration/`, `e2e/`. Docs in `docs/`. Ops in `docker/`, `config/`, `nginx/`, `k8s/`.
- Config and scripts: `Makefile`, `pyproject.toml`, `pytest.ini`, `scripts/`, `sql/`.

## Build, Test, and Dev Commands
- Install dev env: `make setup-dev` (poetry + pre-commit).
- Run backend locally: `uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000` or `pm2 start config/ecosystem.config.js`.
- Quality suite: `make quality` (format, lint, type-check, security, tests).
- Individual tasks: `make format`, `make lint`, `make type-check`, `make security`.
- Tests (backend): `make test`, `make test-unit`, `make test-integration`, `make test-e2e`, `make test-coverage`.
- Frontend: `cd frontend && npm install && npm run dev` (build: `npm run build`, tests: `npm test`).

## Coding Style & Naming
- Python formatting: Black (88 cols) and isort; lint with flake8/pylint; type-check with mypy.
- Python naming: snake_case for modules/functions, PascalCase for classes; keep files focused (see `PROTOCOL.yaml`, 500-line hard limit).
- Frontend: ESLint + TypeScript; keep components small and typed.
- Env: copy `.env.example` to `.env`; never commit secrets (see `credentials/`).

## Testing Guidelines
- Runner: pytest with coverage; default addopts in `pytest.ini` (HTML/XML reports to `tests/reports/`).
- Structure tests under `tests/unit`, `tests/integration`, `tests/e2e`; filename `test_<feature>.py`.
- Coverage: target 90% lines (policy); project enforces thresholds in config. Run: `pytest --cov=src --cov-report=html`.
- Use fixtures under `tests/fixtures`; avoid real network/time; prefer factories.

## Commit & Pull Requests
- Commits: Conventional Commits (e.g., `feat(api): add anomaly predictions endpoint`).
- PRs must include: clear description, linked issues, test evidence (commands/output or screenshots of coverage report), and any schema/API changes.
- CI expects green quality gates; run `make ci` locally before opening a PR.

## Security & Ops Tips
- Run `make security` (Bandit, Safety) before PR.
- Docker compose files in `docker/` for local stacks; Nginx config in `nginx/`.
- Logs in `logs/`; rotate/clean with `make clean` for local dev.

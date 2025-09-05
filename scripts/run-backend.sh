#!/bin/bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd src
exec poetry run uvicorn presentation.api.app_postgres:app --reload --host 0.0.0.0 --port 8000
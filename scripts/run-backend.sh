#!/bin/bash
cd src
poetry run uvicorn presentation.api.app_postgres:app --reload --host 0.0.0.0 --port 8000 
#!/bin/bash

# Set up environment variables
export PYTHONUNBUFFERED=1
export PATH="/root/.local/bin:$PATH"

# Install uvicorn if not installed
pip3 install --user uvicorn

# Change to src directory and run the app
cd src
python3 -m uvicorn presentation.api.app_postgres:app --reload --host 0.0.0.0 --port 8000 
#!/bin/bash

# Run the API server for Abbanoa Water Infrastructure

echo "Starting Abbanoa Water Infrastructure API..."

# Check for Google Cloud credentials
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS not set"
    
    # Try to find application default credentials
    if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
        export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
        echo "Using application default credentials from: $GOOGLE_APPLICATION_CREDENTIALS"
    else
        echo "Please set up authentication:"
        echo "Run: gcloud auth application-default login"
        echo "Or set: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'"
    fi
else
    echo "Using credentials from: $GOOGLE_APPLICATION_CREDENTIALS"
fi

# Set Google Cloud project
export GOOGLE_CLOUD_PROJECT="abbanoa-464816"

# Use poetry environment with dependencies installed
echo "Starting API server on http://localhost:8000"
poetry run uvicorn src.presentation.api.app:app --reload --host 0.0.0.0 --port 8000
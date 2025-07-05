#!/bin/bash
cd /home/alessio/Customers/Abbanoa
export PYTHONPATH=/home/alessio/Customers/Abbanoa:$PYTHONPATH

# Set BigQuery environment variables
export BIGQUERY_PROJECT_ID="abbanoa-464816"
export BIGQUERY_DATASET_ID="water_infrastructure"

# Set Google Cloud authentication
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    # Check if application default credentials exist
    if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
        export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
        echo "Using Application Default Credentials from: $GOOGLE_APPLICATION_CREDENTIALS"
    else
        echo "Warning: GOOGLE_APPLICATION_CREDENTIALS not set. BigQuery may not work."
        echo "Please run: gcloud auth application-default login"
        echo "Or set: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'"
    fi
else
    echo "Using credentials from: $GOOGLE_APPLICATION_CREDENTIALS"
fi

# Use poetry environment with dependencies installed
echo "Using poetry environment..."
poetry run streamlit run src/presentation/streamlit/app.py --server.port 8502 --server.address 0.0.0.0
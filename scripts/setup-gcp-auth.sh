#!/bin/bash
# Script to set up permanent GCP authentication for BigQuery

set -e

PROJECT_ID="abbanoa-464816"
SERVICE_ACCOUNT_NAME="bigquery-service-account"
KEY_FILE="bigquery-service-account-key.json"

echo "Setting up GCP Service Account for BigQuery access..."

# 1. Create service account
echo "Creating service account..."
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="BigQuery Service Account for Water Infrastructure" \
    --project=${PROJECT_ID}

# 2. Grant necessary permissions
echo "Granting BigQuery permissions..."
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# BigQuery Data Editor (read/write)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.dataEditor"

# BigQuery Job User (run queries)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.jobUser"

# Storage Object Viewer (for reading data)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectViewer"

# 3. Create and download key
echo "Creating service account key..."
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

echo "Service account key created: ${KEY_FILE}"
echo ""
echo "IMPORTANT SECURITY NOTES:"
echo "1. Keep this key file secure and never commit it to git"
echo "2. Add ${KEY_FILE} to .gitignore"
echo "3. Store it in a secure location"
echo "4. Set proper file permissions: chmod 600 ${KEY_FILE}"
echo ""
echo "To use this key:"
echo "1. For Docker: -v \$(pwd)/${KEY_FILE}:/app/credentials.json:ro"
echo "2. Environment: export GOOGLE_APPLICATION_CREDENTIALS=\$(pwd)/${KEY_FILE}"
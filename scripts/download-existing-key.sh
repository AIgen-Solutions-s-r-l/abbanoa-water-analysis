#!/bin/bash
# Script to download key for existing service account

set -e

PROJECT_ID="abbanoa-464816"
SERVICE_ACCOUNT_NAME="bigquery-service-account"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="bigquery-service-account-key.json"

echo "Downloading key for existing service account: ${SERVICE_ACCOUNT_EMAIL}"

# First, let's check if the service account exists and has keys
echo "Checking existing keys..."
gcloud iam service-accounts keys list \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

# Create a new key
echo ""
echo "Creating new key..."
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

if [ -f "${KEY_FILE}" ]; then
    echo ""
    echo "✅ Service account key created successfully: ${KEY_FILE}"
    
    # Set proper permissions
    chmod 600 ${KEY_FILE}
    echo "✅ Set secure permissions on key file"
    
    # Verify the key
    echo ""
    echo "Verifying the key..."
    python3 scripts/verify_bigquery_auth.py
else
    echo "❌ Failed to create key file"
    exit 1
fi
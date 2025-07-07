#!/bin/bash
# Fixed script to set up permanent GCP authentication for BigQuery

set -e

PROJECT_ID="abbanoa-464816"
SERVICE_ACCOUNT_NAME="bigquery-service-account"
KEY_FILE="bigquery-service-account-key.json"

echo "Setting up GCP Service Account for BigQuery access..."

# Check if service account already exists
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} >/dev/null 2>&1; then
    echo "Service account already exists: ${SERVICE_ACCOUNT_EMAIL}"
else
    echo "Creating service account..."
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
        --display-name="BigQuery Service Account for Water Infrastructure" \
        --project=${PROJECT_ID}
    
    echo "Waiting for service account propagation..."
    sleep 10
fi

echo "Granting BigQuery permissions..."

# Grant BigQuery Data Editor (read/write)
echo "Granting BigQuery Data Editor role..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.dataEditor" \
    --quiet

sleep 2

# Grant BigQuery Job User (run queries)
echo "Granting BigQuery Job User role..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.jobUser" \
    --quiet

sleep 2

# Grant Storage Object Viewer (for reading data)
echo "Granting Storage Object Viewer role..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectViewer" \
    --quiet

sleep 2

# Check if key file already exists
if [ -f "${KEY_FILE}" ]; then
    echo "Key file already exists: ${KEY_FILE}"
    echo "To create a new key, delete the existing file first."
else
    echo "Creating service account key..."
    gcloud iam service-accounts keys create ${KEY_FILE} \
        --iam-account=${SERVICE_ACCOUNT_EMAIL} \
        --project=${PROJECT_ID}

    # Set proper permissions
    chmod 600 ${KEY_FILE}
    
    echo "Service account key created: ${KEY_FILE}"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo "Key File: ${KEY_FILE}"
echo ""
echo "IMPORTANT SECURITY NOTES:"
echo "1. Keep this key file secure and never commit it to git"
echo "2. The key file is already added to .gitignore"
echo "3. Set proper file permissions: chmod 600 ${KEY_FILE}"
echo "4. Store it in a secure location"
echo ""
echo "To use this key:"
echo "1. For Docker: ./docker-run-api-with-auth.sh"
echo "2. Environment: export GOOGLE_APPLICATION_CREDENTIALS=\$(pwd)/${KEY_FILE}"
echo ""
echo "Test authentication:"
echo "python3 -c \"
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '${KEY_FILE}'
from google.cloud import bigquery
client = bigquery.Client()
print('✅ Authentication successful!')
print(f'Project: {client.project}')
\"
"
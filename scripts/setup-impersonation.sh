#!/bin/bash
# Setup service account impersonation as a workaround

set -e

SERVICE_ACCOUNT="bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com"

echo "=== Setting up Service Account Impersonation ==="
echo ""
echo "This allows you to use the service account without a key file"
echo ""

# Grant yourself permission to impersonate the service account
echo "Granting impersonation permissions..."
gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT} \
    --member="user:$(gcloud config get-value account)" \
    --role="roles/iam.serviceAccountTokenCreator" \
    --project=abbanoa-464816

echo "✅ Permissions granted"
echo ""

# Set up impersonation in gcloud
echo "Configuring gcloud to impersonate the service account..."
gcloud config set auth/impersonate_service_account ${SERVICE_ACCOUNT}

echo "✅ Impersonation configured"
echo ""

# Test the setup
echo "Testing BigQuery access with impersonation..."
bq ls --project_id=abbanoa-464816 --max_results=1

if [ $? -eq 0 ]; then
    echo "✅ BigQuery access working with impersonation!"
else
    echo "❌ BigQuery access failed"
    exit 1
fi

echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Update docker-compose.processing.yml to mount your gcloud config:"
echo "   volumes:"
echo "     - ~/.config/gcloud:/root/.config/gcloud:ro"
echo ""
echo "2. Remove GOOGLE_APPLICATION_CREDENTIALS from environment variables"
echo ""
echo "3. Restart the containers"
echo ""
echo "Note: This uses your personal credentials to impersonate the service account."
echo "For production, you should get the organization policy updated."
# Manual GCP Authentication Setup

Since automated script requires interactive authentication, follow these manual steps:

## Step 1: Authenticate with gcloud

```bash
# Login to gcloud (this will open a browser)
gcloud auth login

# Set the project
gcloud config set project abbanoa-464816

# Verify authentication
gcloud auth list
gcloud config get-value project
```

## Step 2: Create Service Account

```bash
# Create the service account
gcloud iam service-accounts create bigquery-service-account \
    --display-name="BigQuery Service Account for Water Infrastructure" \
    --project=abbanoa-464816
```

## Step 3: Grant Necessary Permissions

```bash
# Set the service account email
SERVICE_ACCOUNT_EMAIL="bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com"

# Grant BigQuery Data Editor (read/write)
gcloud projects add-iam-policy-binding abbanoa-464816 \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.dataEditor"

# Grant BigQuery Job User (run queries)
gcloud projects add-iam-policy-binding abbanoa-464816 \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.jobUser"

# Grant Storage Object Viewer (for reading data)
gcloud projects add-iam-policy-binding abbanoa-464816 \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectViewer"
```

## Step 4: Create and Download Service Account Key

```bash
# Create the key file
gcloud iam service-accounts keys create bigquery-service-account-key.json \
    --iam-account=bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com \
    --project=abbanoa-464816
```

## Step 5: Secure the Key File

```bash
# Set proper permissions (read-only for owner)
chmod 600 bigquery-service-account-key.json

# Verify the file was created
ls -la bigquery-service-account-key.json
```

## Step 6: Test the Authentication

```bash
# Test with gcloud
gcloud auth activate-service-account --key-file=bigquery-service-account-key.json
gcloud auth list

# Test with Python (optional)
python3 -c "
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'bigquery-service-account-key.json'
from google.cloud import bigquery
client = bigquery.Client()
print('✅ Authentication successful!')
print(f'Project: {client.project}')
"
```

## Step 7: Run Docker with Authentication

Once you have the key file, you can run:

```bash
# Using the convenience script
./docker-run-api-with-auth.sh

# Or manually with docker
docker run -d \
    --name abbanoa-api \
    -p 8000:8000 \
    -v "$(pwd)/bigquery-service-account-key.json:/app/credentials.json:ro" \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
    -e GOOGLE_CLOUD_PROJECT=abbanoa-464816 \
    -e BIGQUERY_PROJECT_ID=abbanoa-464816 \
    -e BIGQUERY_DATASET_ID=water_infrastructure \
    -e LOG_LEVEL=INFO \
    abbanoa-api:latest
```

## Important Security Notes

1. **Never commit the key file to Git** - it's already in .gitignore
2. **Keep the key secure** - treat it like a password
3. **Rotate regularly** - recommended every 90 days
4. **Use least privilege** - only grant necessary permissions

## After Setup

The key file `bigquery-service-account-key.json` will provide permanent access to BigQuery without daily refresh requirements.

To verify everything works:
1. Run the Docker container with authentication
2. Test the API: `curl http://localhost:8000/health`
3. Test forecast endpoint: `curl "http://localhost:8000/api/v1/forecasts/DIST_001/flow_rate?horizon=7"`
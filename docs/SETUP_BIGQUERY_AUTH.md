# Setting Up BigQuery Authentication

This guide will help you create real Google Cloud credentials for the Abbanoa water infrastructure project.

## Prerequisites

- Access to Google Cloud Console (https://console.cloud.google.com)
- Project ID: `abbanoa-464816`
- Billing enabled on the project
- Owner or IAM Admin permissions

## Option 1: Using gcloud CLI (Recommended)

1. **Login to gcloud**:
   ```bash
   gcloud auth login
   ```

2. **Set the project**:
   ```bash
   gcloud config set project abbanoa-464816
   ```

3. **Run the setup script**:
   ```bash
   cd ~/Customers/Abbanoa
   ./scripts/setup-gcp-auth.sh
   ```

   This script will:
   - Create a service account named `bigquery-service-account`
   - Grant necessary BigQuery permissions
   - Download the key file as `bigquery-service-account-key.json`

## Option 2: Manual Setup via Console

1. **Navigate to Service Accounts**:
   - Go to https://console.cloud.google.com/iam-admin/serviceaccounts
   - Select project `abbanoa-464816`

2. **Create Service Account**:
   - Click "CREATE SERVICE ACCOUNT"
   - Name: `bigquery-service-account`
   - Description: "BigQuery Service Account for Water Infrastructure"
   - Click "CREATE AND CONTINUE"

3. **Grant Permissions**:
   Add these roles:
   - `BigQuery Data Editor`
   - `BigQuery Job User`
   - `Storage Object Viewer`
   - Click "CONTINUE"

4. **Create Key**:
   - Click "CREATE KEY"
   - Choose JSON format
   - Save as `bigquery-service-account-key.json` in the project root

## Option 3: Using Existing User Credentials (Quick Test)

If you just want to test the system with your personal credentials:

1. **Login with application default credentials**:
   ```bash
   gcloud auth application-default login
   ```

2. **Update docker-compose.processing.yml**:
   ```yaml
   volumes:
     - ~/.config/gcloud:/root/.config/gcloud:ro
   ```

3. **Remove GOOGLE_APPLICATION_CREDENTIALS from .env files**

## After Setup

1. **Verify the key file**:
   ```bash
   ls -la bigquery-service-account-key.json
   ```

2. **Test BigQuery access**:
   ```bash
   python3 -c "
   from google.cloud import bigquery
   client = bigquery.Client(project='abbanoa-464816')
   print('BigQuery client created successfully!')
   "
   ```

3. **Restart the processing service**:
   ```bash
   docker compose -f docker-compose.processing.yml restart processing
   ```

4. **Check logs**:
   ```bash
   docker compose -f docker-compose.processing.yml logs processing -f
   ```

## Security Best Practices

1. **Never commit the key file to git**:
   - Already added to `.gitignore`
   
2. **Set proper permissions**:
   ```bash
   chmod 600 bigquery-service-account-key.json
   ```

3. **Rotate keys regularly**:
   - Delete old keys from the console
   - Generate new keys every 90 days

4. **Use Secret Manager for production**:
   - Store keys in Google Secret Manager
   - Reference them in your deployment

## Troubleshooting

### Error: "Reauthentication is needed"
- Your gcloud credentials have expired
- Run: `gcloud auth login`

### Error: "Permission denied"
- Check service account has correct roles
- Verify project ID is correct

### Error: "Invalid JWT Signature"
- The key file is corrupted or invalid
- Regenerate the key from the console

### Error: "Project not found"
- Ensure billing is enabled
- Check you have access to the project

## Next Steps

Once authentication is working:
1. The processing service will automatically start fetching data
2. Data will be processed and stored in PostgreSQL
3. The dashboard will show real metrics
4. ML models will begin training

For support, contact: a.rocchi@aigensolutions.it
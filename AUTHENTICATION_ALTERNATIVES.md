# Authentication Alternatives (Service Account Keys Blocked)

## Issue
Your GCP organization has a policy that prevents service account key creation:
```
Key creation is not allowed on this service account.
constraints/iam.disableServiceAccountKeyCreation
```

This is a security best practice, but we need alternative authentication methods.

## ✅ Solution 1: User Impersonation (Recommended for Development)

### Setup
```bash
# Install the gcloud component for impersonation
gcloud components install gcloud-auth-plugin

# Configure impersonation
gcloud config set auth/impersonate_service_account bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com

# Test access
gcloud auth print-access-token
```

### Grant Impersonation Permission
```bash
# Grant yourself permission to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding \
    bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com \
    --member="user:a.rocchi@aigensolutions.it" \
    --role="roles/iam.serviceAccountTokenCreator"
```

### Docker Usage with Impersonation
```bash
# Get current user credentials
gcloud auth application-default login

# Run Docker with user credentials mounted
docker run -d \
    --name abbanoa-api \
    -p 8000:8000 \
    -v ~/.config/gcloud:/home/apiuser/.config/gcloud:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS=/home/apiuser/.config/gcloud/application_default_credentials.json \
    -e GOOGLE_CLOUD_PROJECT=abbanoa-464816 \
    -e BIGQUERY_PROJECT_ID=abbanoa-464816 \
    -e BIGQUERY_DATASET_ID=water_infrastructure \
    -e LOG_LEVEL=INFO \
    abbanoa-api:latest
```

## ✅ Solution 2: Workload Identity Federation (Best for Production)

### Setup GitHub Actions Federation
```bash
# Create workload identity pool
gcloud iam workload-identity-pools create github-pool \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Create GitHub provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"

# Grant service account impersonation to GitHub
gcloud iam service-accounts add-iam-policy-binding \
    bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/314319558231/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_REPO"
```

### GitHub Actions Workflow
```yaml
name: Deploy API
on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    
    steps:
    - uses: actions/checkout@v4
    
    - uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: 'projects/314319558231/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
        service_account: 'bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com'
    
    - name: Build and deploy
      run: |
        docker build -t gcr.io/abbanoa-464816/abbanoa-api:latest .
        docker push gcr.io/abbanoa-464816/abbanoa-api:latest
```

## ✅ Solution 3: Google Cloud Run (Best for Production Deployment)

### Deploy to Cloud Run
```bash
# Build and push image
docker build -f Dockerfile.api.simple -t gcr.io/abbanoa-464816/abbanoa-api:latest .
docker push gcr.io/abbanoa-464816/abbanoa-api:latest

# Deploy with service account attached
gcloud run deploy abbanoa-api \
    --image gcr.io/abbanoa-464816/abbanoa-api:latest \
    --service-account bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com \
    --set-env-vars BIGQUERY_DATASET_ID=water_infrastructure,LOG_LEVEL=INFO \
    --region europe-west1 \
    --allow-unauthenticated \
    --max-instances 10 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900
```

### Benefits of Cloud Run
- ✅ No credential files needed
- ✅ Automatic scaling
- ✅ Built-in authentication
- ✅ HTTPS endpoints
- ✅ Pay-per-use pricing

## ✅ Solution 4: Request Org Policy Exception

If you need service account keys, request an exception:

### Contact your GCP administrator to:
1. **Temporarily disable** the constraint for your project
2. **Create an exception** for specific service accounts
3. **Grant you** the `Organization Policy Administrator` role

### Command to disable constraint (Admin only):
```bash
# Create policy file
cat > disable-sa-key-policy.yaml << EOF
constraint: constraints/iam.disableServiceAccountKeyCreation
enforcedValue: false
EOF

# Apply policy
gcloud resource-manager org-policies set-policy disable-sa-key-policy.yaml --project=abbanoa-464816
```

## 🔧 Current Working Solution

Let me set up **Solution 1 (User Impersonation)** for immediate use:

```bash
# 1. Grant yourself impersonation permission
gcloud iam service-accounts add-iam-policy-binding \
    bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com \
    --member="user:a.rocchi@aigensolutions.it" \
    --role="roles/iam.serviceAccountTokenCreator"

# 2. Set up impersonation
gcloud config set auth/impersonate_service_account bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com

# 3. Generate application default credentials
gcloud auth application-default login

# 4. Test authentication
python3 -c "
from google.cloud import bigquery
client = bigquery.Client()
print('✅ Authentication successful!')
print(f'Project: {client.project}')
"
```

## Summary

Since service account keys are blocked, I recommend:

1. **For Development**: Use Solution 1 (User Impersonation)
2. **For Production**: Use Solution 3 (Cloud Run) 
3. **For CI/CD**: Use Solution 2 (Workload Identity Federation)

This is actually MORE secure than service account keys since:
- No permanent credentials to manage
- Automatic token rotation
- Better audit trail
- Follows Google Cloud security best practices
#!/bin/bash
# Alternative authentication setup using user credentials

set -e

echo "=== Setting up authentication using your user credentials ==="
echo ""
echo "This will use your personal Google account for BigQuery access"
echo "This is suitable for development/testing"
echo ""

# Check current auth status
echo "Current authentication status:"
gcloud auth list

echo ""
echo "Step 1: Login to Google Cloud (if needed)"
echo "This will open a browser window for authentication"
read -p "Press Enter to continue..."

gcloud auth login

echo ""
echo "Step 2: Set up Application Default Credentials"
echo "This will open another browser window"
read -p "Press Enter to continue..."

gcloud auth application-default login

echo ""
echo "Step 3: Verify access to BigQuery"
gcloud config set project abbanoa-464816

echo ""
echo "Testing BigQuery access..."
bq ls -j --project_id=abbanoa-464816 --max_results=1

if [ $? -eq 0 ]; then
    echo "✅ BigQuery access confirmed!"
else
    echo "❌ BigQuery access failed"
    exit 1
fi

echo ""
echo "Step 4: Update Docker configuration"
echo ""
echo "To use your credentials with Docker, add this to docker-compose.processing.yml:"
echo ""
echo "  processing:"
echo "    volumes:"
echo "      - ~/.config/gcloud:/root/.config/gcloud:ro"
echo ""
echo "And remove GOOGLE_APPLICATION_CREDENTIALS from the environment section"
echo ""
read -p "Would you like me to update docker-compose.processing.yml automatically? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup current file
    cp docker-compose.processing.yml docker-compose.processing.yml.backup
    
    # Update the file
    echo "Updating docker-compose.processing.yml..."
    
    # This is a bit tricky with sed, so let's create a Python script for it
    python3 - <<EOF
import yaml

with open('docker-compose.processing.yml', 'r') as f:
    data = yaml.safe_load(f)

# Update processing service
if 'services' in data and 'processing' in data['services']:
    # Add gcloud volume
    if 'volumes' not in data['services']['processing']:
        data['services']['processing']['volumes'] = []
    
    # Check if gcloud volume already exists
    gcloud_volume = "~/.config/gcloud:/root/.config/gcloud:ro"
    volumes = data['services']['processing']['volumes']
    
    # Remove the service account key volume if it exists
    volumes = [v for v in volumes if 'bigquery-service-account-key.json' not in v]
    
    # Add gcloud volume if not exists
    if not any('/.config/gcloud' in v for v in volumes):
        volumes.append(gcloud_volume)
    
    data['services']['processing']['volumes'] = volumes
    
    # Remove GOOGLE_APPLICATION_CREDENTIALS from environment
    if 'environment' in data['services']['processing']:
        env = data['services']['processing']['environment']
        if 'GOOGLE_APPLICATION_CREDENTIALS' in env:
            del env['GOOGLE_APPLICATION_CREDENTIALS']

# Update API service similarly
if 'services' in data and 'api' in data['services']:
    if 'volumes' not in data['services']['api']:
        data['services']['api']['volumes'] = []
    
    volumes = data['services']['api']['volumes']
    volumes = [v for v in volumes if 'bigquery-service-account-key.json' not in v]
    
    if not any('/.config/gcloud' in v for v in volumes):
        volumes.append("~/.config/gcloud:/root/.config/gcloud:ro")
    
    data['services']['api']['volumes'] = volumes
    
    if 'environment' in data['services']['api']:
        env = data['services']['api']['environment']
        if 'GOOGLE_APPLICATION_CREDENTIALS' in env:
            del env['GOOGLE_APPLICATION_CREDENTIALS']

# Write back
with open('docker-compose.processing.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print("✅ Updated docker-compose.processing.yml")
EOF

    echo ""
    echo "✅ Configuration updated!"
    echo "Backup saved as docker-compose.processing.yml.backup"
fi

echo ""
echo "Step 5: Update .env files"
echo ""
echo "Remove or comment out GOOGLE_APPLICATION_CREDENTIALS from:"
echo "  - .env"
echo "  - .env.processing"
echo ""

# Offer to update .env files
read -p "Would you like me to comment out GOOGLE_APPLICATION_CREDENTIALS in .env files? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i.backup 's/^GOOGLE_APPLICATION_CREDENTIALS=/#GOOGLE_APPLICATION_CREDENTIALS=/' .env
    sed -i.backup 's/^GOOGLE_APPLICATION_CREDENTIALS=/#GOOGLE_APPLICATION_CREDENTIALS=/' .env.processing
    echo "✅ Updated .env files (backups created with .backup extension)"
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Restart the Docker containers:"
echo "   docker compose -f docker-compose.processing.yml down"
echo "   docker compose -f docker-compose.processing.yml up -d"
echo ""
echo "2. Check the logs:"
echo "   docker compose -f docker-compose.processing.yml logs -f processing"
echo ""
echo "Note: This uses your personal credentials. For production, you should:"
echo "  - Contact your Google Cloud admin to enable service account key creation"
echo "  - Or use Workload Identity Federation"
echo ""
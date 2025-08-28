#!/bin/bash

# Database export script for Google Cloud SQL PostgreSQL
# This script exports the Abbanoa database in a format compatible with Google Cloud SQL

# Load environment variables
source .env

# Set export variables
EXPORT_DATE=$(date +%Y%m%d_%H%M%S)
EXPORT_DIR="./database_exports"
EXPORT_FILE="${EXPORT_DIR}/abbanoa_db_export_${EXPORT_DATE}.sql"

# Create export directory if it doesn't exist
mkdir -p ${EXPORT_DIR}

echo "Starting database export for Google Cloud SQL..."
echo "Database: ${POSTGRES_DB}"
echo "Host: ${POSTGRES_HOST}:${POSTGRES_PORT}"
echo "Export file: ${EXPORT_FILE}"

# Export database using pg_dump with Google Cloud SQL compatible options
# --no-owner: Don't output commands to set ownership (GCP handles this)
# --no-acl: Don't output commands to set access privileges (GCP handles this)
# --format=plain: Plain SQL format (required for Cloud SQL)
# --create: Include CREATE DATABASE statement
# --clean: Include DROP statements before CREATE
# --if-exists: Use IF EXISTS for DROP statements
PGPASSWORD=${POSTGRES_PASSWORD} pg_dump \
    -h ${POSTGRES_HOST} \
    -p ${POSTGRES_PORT} \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    --no-owner \
    --no-acl \
    --format=plain \
    --create \
    --clean \
    --if-exists \
    --encoding=UTF8 \
    --verbose \
    > ${EXPORT_FILE}

# Check if export was successful
if [ $? -eq 0 ]; then
    echo "Database export completed successfully!"
    echo "Export file: ${EXPORT_FILE}"
    
    # Get file size
    FILE_SIZE=$(ls -lh ${EXPORT_FILE} | awk '{print $5}')
    echo "File size: ${FILE_SIZE}"
    
    # Create a compressed version for easier transfer
    echo "Creating compressed version..."
    gzip -c ${EXPORT_FILE} > ${EXPORT_FILE}.gz
    COMPRESSED_SIZE=$(ls -lh ${EXPORT_FILE}.gz | awk '{print $5}')
    echo "Compressed file: ${EXPORT_FILE}.gz (${COMPRESSED_SIZE})"
    
    echo ""
    echo "Next steps for Google Cloud SQL import:"
    echo "1. Upload the SQL file to a Google Cloud Storage bucket"
    echo "2. Use Cloud Console or gcloud CLI to import:"
    echo "   gcloud sql import sql INSTANCE_NAME gs://BUCKET_NAME/$(basename ${EXPORT_FILE}) --database=DATABASE_NAME"
    echo ""
    echo "Note: Make sure your Cloud SQL instance has:"
    echo "- PostgreSQL version compatible with the export (check pg_dump version)"
    echo "- Sufficient storage for the imported data"
    echo "- Required extensions installed"
else
    echo "Error: Database export failed!"
    exit 1
fi
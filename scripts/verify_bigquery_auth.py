#!/usr/bin/env python3
"""
Script to verify BigQuery authentication is working correctly.
"""

import os
import sys
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

def verify_bigquery_auth():
    """Verify BigQuery authentication and access."""
    print("=== BigQuery Authentication Verification ===\n")
    
    # Check for credentials
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "bigquery-service-account-key.json")
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        print("\nPlease follow the setup guide in docs/SETUP_BIGQUERY_AUTH.md")
        return False
    
    print(f"✅ Found credentials file: {creds_path}")
    
    try:
        # Load credentials
        if creds_path.endswith('.json'):
            credentials = service_account.Credentials.from_service_account_file(creds_path)
            print("✅ Loaded service account credentials")
        else:
            print("❌ Invalid credentials file format")
            return False
        
        # Create BigQuery client
        project_id = "abbanoa-464816"
        client = bigquery.Client(project=project_id, credentials=credentials)
        print(f"✅ Created BigQuery client for project: {project_id}")
        
        # Test dataset access
        dataset_id = "water_infrastructure"
        dataset_ref = client.dataset(dataset_id)
        try:
            dataset = client.get_dataset(dataset_ref)
            print(f"✅ Can access dataset: {dataset_id}")
        except Exception as e:
            print(f"❌ Cannot access dataset {dataset_id}: {str(e)}")
            return False
        
        # Test query execution
        print("\n📊 Testing query execution...")
        query = """
        SELECT 
            table_name,
            creation_time,
            row_count
        FROM `abbanoa-464816.water_infrastructure.__TABLES__`
        ORDER BY creation_time DESC
        LIMIT 5
        """
        
        try:
            results = client.query(query).result()
            print("✅ Query executed successfully")
            
            print("\n📋 Recent tables in dataset:")
            for row in results:
                print(f"  - {row.table_name}: {row.row_count} rows (created: {row.creation_time})")
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            return False
        
        # Test specific table access
        print("\n🔍 Checking sensor data tables...")
        sensor_query = """
        SELECT 
            COUNT(*) as total_records,
            MIN(timestamp) as oldest_record,
            MAX(timestamp) as newest_record
        FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
        """
        
        try:
            results = client.query(sensor_query).result()
            for row in results:
                if row.total_records > 0:
                    print(f"✅ Found {row.total_records} records")
                    print(f"  - Oldest: {row.oldest_record}")
                    print(f"  - Newest: {row.newest_record}")
                else:
                    print("⚠️  No data found in sensor_readings_ml table")
        except Exception as e:
            print(f"⚠️  Cannot access sensor_readings_ml: {str(e)}")
        
        print("\n✅ BigQuery authentication is working correctly!")
        print("\n🚀 Next steps:")
        print("1. Restart the processing service:")
        print("   docker compose -f docker-compose.processing.yml restart processing")
        print("2. Monitor the logs:")
        print("   docker compose -f docker-compose.processing.yml logs -f processing")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("\nPlease check:")
        print("1. The credentials file is valid")
        print("2. The service account has the correct permissions")
        print("3. The project ID is correct")
        return False

if __name__ == "__main__":
    success = verify_bigquery_auth()
    sys.exit(0 if success else 1)
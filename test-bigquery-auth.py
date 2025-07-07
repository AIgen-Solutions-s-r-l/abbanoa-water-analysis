#!/usr/bin/env python3
"""Test BigQuery authentication with impersonation."""

import os
from google.cloud import bigquery
from google.auth import default

def test_bigquery_auth():
    """Test BigQuery authentication and access."""
    try:
        # Get default credentials
        credentials, project = default()
        print(f"✅ Using project: {project}")
        print(f"✅ Credentials type: {type(credentials).__name__}")
        
        # Create BigQuery client
        client = bigquery.Client(credentials=credentials, project=project)
        print(f"✅ BigQuery client created for project: {client.project}")
        
        # List datasets
        datasets = list(client.list_datasets())
        print(f"✅ Found {len(datasets)} datasets:")
        for dataset in datasets:
            print(f"   - {dataset.dataset_id}")
        
        # Test query on the water_infrastructure dataset
        if any(d.dataset_id == "water_infrastructure" for d in datasets):
            print("\n🔍 Testing query on water_infrastructure dataset...")
            
            query = """
            SELECT table_name, table_type
            FROM `abbanoa-464816.water_infrastructure.INFORMATION_SCHEMA.TABLES`
            LIMIT 5
            """
            
            job_config = bigquery.QueryJobConfig(
                use_query_cache=True,
                timeout_ms=10000,  # 10 seconds
            )
            
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()
            
            print("✅ Query successful! Found tables:")
            for row in results:
                print(f"   - {row.table_name} ({row.table_type})")
                
        else:
            print("⚠️  water_infrastructure dataset not found")
            
        print("\n🎉 Authentication test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["GOOGLE_CLOUD_PROJECT"] = "abbanoa-464816"
    
    test_bigquery_auth()
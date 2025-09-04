#!/usr/bin/env python3
"""
Test database connection
"""

import psycopg2
import os

def test_connection():
    """Test database connection with different configurations."""
    
    configs = [
        {
            'host': 'localhost',
            'port': 5432,
            'database': 'abbanoa_processing',
            'user': 'abbanoa_user',
            'password': 'abbanoa_secure_pass'
        },
        {
            'host': '127.0.0.1',
            'port': 5432,
            'database': 'abbanoa_processing',
            'user': 'abbanoa_user',
            'password': 'abbanoa_secure_pass'
        }
    ]
    
    for i, config in enumerate(configs):
        print(f"Testing config {i+1}: {config['host']}:{config['port']}")
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sensor_readings")
            count = cursor.fetchone()[0]
            print(f"✅ Connection successful! Found {count} readings")
            cursor.close()
            conn.close()
            return config
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    
    return None

if __name__ == "__main__":
    working_config = test_connection()
    if working_config:
        print(f"\nWorking configuration: {working_config}")
    else:
        print("\nNo working configuration found")

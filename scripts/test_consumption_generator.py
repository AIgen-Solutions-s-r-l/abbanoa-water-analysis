#!/usr/bin/env python3
"""
Test script for the Synthetic Water Consumption Dataset Generator

This script runs a smaller version of the generator to validate functionality
before running the full 50,000 user dataset generation.

Author: AI Water Management System
Date: 2025-01-28
"""

import sys
import os
from datetime import datetime
import pandas as pd

# Add current directory to path to import the generator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_consumption_dataset import WaterConsumptionGenerator

def test_small_dataset():
    """
    Test the generator with a small dataset to validate functionality.
    """
    print("🧪 Testing Water Consumption Dataset Generator")
    print("=" * 50)
    
    # Test configuration (much smaller for validation)
    START_DATE = '2024-01-01'
    END_DATE = '2024-01-31'  # Just January 2024
    NUM_USERS = 100  # Small number for testing
    OUTPUT_DIR = 'test_consumption_data'
    BATCH_SIZE = 50
    
    print(f"📊 Test Parameters:")
    print(f"   • Users: {NUM_USERS}")
    print(f"   • Date range: {START_DATE} to {END_DATE}")
    print(f"   • Output: {OUTPUT_DIR}")
    print()
    
    try:
        # Initialize generator
        generator = WaterConsumptionGenerator(
            start_date=START_DATE,
            end_date=END_DATE,
            num_users=NUM_USERS
        )
        
        print(f"✅ Generator initialized successfully")
        print(f"   • Total days: {generator.num_days}")
        print(f"   • Expected records: {NUM_USERS * generator.num_days:,}")
        print()
        
        # Generate small dataset
        generator.generate_dataset(output_dir=OUTPUT_DIR, batch_size=BATCH_SIZE)
        
        # Validate results
        validate_output(OUTPUT_DIR, NUM_USERS, generator.num_days)
        
        print("\n🎉 Test completed successfully!")
        print(f"📁 Test data saved in: {OUTPUT_DIR}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

def validate_output(output_dir: str, expected_users: int, expected_days: int):
    """
    Validate the generated output files.
    """
    print("🔍 Validating output...")
    
    # Check if output directory exists
    if not os.path.exists(output_dir):
        raise ValueError(f"Output directory {output_dir} does not exist")
    
    # List CSV files
    csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    print(f"   • Found {len(csv_files)} CSV files")
    
    total_records = 0
    user_ids = set()
    
    # Validate each CSV file
    for csv_file in csv_files:
        file_path = os.path.join(output_dir, csv_file)
        df = pd.read_csv(file_path)
        
        total_records += len(df)
        user_ids.update(df['user_id'].unique())
        
        # Validate columns
        expected_columns = ['user_id', 'date', 'user_type', 'district', 
                          'temperature_c', 'is_holiday', 'consumption_liters']
        
        for col in expected_columns:
            if col not in df.columns:
                raise ValueError(f"Missing column {col} in {csv_file}")
        
        # Validate data types and ranges
        if df['consumption_liters'].min() < 0:
            raise ValueError(f"Negative consumption found in {csv_file}")
        
        if df['temperature_c'].min() < -10 or df['temperature_c'].max() > 50:
            raise ValueError(f"Unrealistic temperature range in {csv_file}")
        
        print(f"   • {csv_file}: {len(df):,} records ✅")
    
    # Final validation
    expected_total_records = expected_users * expected_days
    
    print(f"   • Total records: {total_records:,}")
    print(f"   • Expected records: {expected_total_records:,}")
    print(f"   • Unique users: {len(user_ids)}")
    print(f"   • Expected users: {expected_users}")
    
    if total_records != expected_total_records:
        raise ValueError(f"Record count mismatch: {total_records} vs {expected_total_records}")
    
    if len(user_ids) != expected_users:
        raise ValueError(f"User count mismatch: {len(user_ids)} vs {expected_users}")
    
    print("✅ All validations passed!")

def show_sample_data(output_dir: str):
    """
    Display sample data from the generated files.
    """
    print("\n📋 Sample Data Preview:")
    print("-" * 30)
    
    csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    if csv_files:
        sample_file = os.path.join(output_dir, csv_files[0])
        df = pd.read_csv(sample_file)
        
        print(f"File: {csv_files[0]}")
        print(df.head(10))
        
        print(f"\n📊 Summary Statistics:")
        print(f"   • User types: {df['user_type'].value_counts().to_dict()}")
        print(f"   • Districts: {df['district'].value_counts().to_dict()}")
        print(f"   • Avg consumption: {df['consumption_liters'].mean():.2f} L/day")
        print(f"   • Temperature range: {df['temperature_c'].min():.1f}°C to {df['temperature_c'].max():.1f}°C")
        print(f"   • Holiday days: {df['is_holiday'].sum()}")

if __name__ == "__main__":
    test_small_dataset()
    
    # Show sample if test passed
    try:
        show_sample_data('test_consumption_data')
    except Exception as e:
        print(f"Could not show sample data: {e}") 
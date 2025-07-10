#!/usr/bin/env python3
"""
Simplified backup data processor focused on extracting essential sensor data.
"""

import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from google.cloud import bigquery
from tqdm import tqdm
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ID = "abbanoa-464816"
DATASET_ID = "water_infrastructure"
BACKUP_DIR = Path(__file__).parent.parent / "RAWDATA" / "NEW_DATA" / "BACKUP"

def parse_data_log_simple(file_path: Path, node_id: str) -> pd.DataFrame:
    """Parse DATA_LOG files with simple approach."""
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        lines = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        
        if not lines:
            return pd.DataFrame()
        
        data = []
        for line in lines:
            parts = line.strip().split(';')
            if len(parts) < 10:
                continue
                
            # Extract date/time (usually in positions 1 and 2)
            try:
                if '/' in parts[1]:  # Date column
                    date_str = parts[1]
                    time_str = parts[2] if len(parts) > 2 else "00:00:00"
                    
                    # Parse Italian date format DD/MM/YYYY
                    dt = datetime.strptime(f"{date_str} {time_str}", "%Y/%m/%d %H:%M:%S")
                    
                    # Look for numeric values that could be pressure, flow, temperature
                    values = []
                    for i in range(3, min(20, len(parts))):
                        try:
                            val = float(parts[i].replace(',', '.'))
                            if 0 <= val <= 100:  # Reasonable sensor range
                                values.append(val)
                        except:
                            continue
                    
                    if values:
                        # Assume common patterns
                        pressure = values[0] if len(values) > 0 else None
                        flow = values[1] if len(values) > 1 else None
                        temp = values[2] if len(values) > 2 else None
                        
                        data.append({
                            'timestamp': dt,
                            'node_id': node_id,
                            'pressure': pressure,
                            'flow_rate': flow,
                            'temperature': temp
                        })
            except:
                continue
        
        if data:
            df = pd.DataFrame(data)
            # Remove duplicates
            df = df.drop_duplicates(subset=['timestamp'])
            return df
            
    except Exception as e:
        logger.debug(f"Error parsing {file_path}: {e}")
    
    return pd.DataFrame()

def main():
    """Main processing function."""
    logger.info("Starting simplified backup data processing")
    
    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID, location="EU")
    
    # Ensure table exists
    table_id = f"{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml"
    
    # Get all backup directories
    backup_dirs = sorted([d for d in BACKUP_DIR.iterdir() if d.is_dir()])
    logger.info(f"Found {len(backup_dirs)} backup directories")
    
    # Process each directory
    all_data = []
    
    for backup_dir in tqdm(backup_dirs, desc="Processing directories"):
        # Find CSV files
        csv_files = list(backup_dir.glob("*DATA_LOG.csv"))
        
        for csv_file in csv_files:
            # Extract node ID from filename
            match = re.match(r'(\d{6})_', csv_file.name)
            if match:
                node_id = match.group(1)
                
                # Parse the file
                df = parse_data_log_simple(csv_file, node_id)
                
                if not df.empty:
                    # Add metadata
                    df['district_id'] = 'selargius'
                    df['node_name'] = f"Node {node_id}"
                    df['node_type'] = 'distribution' if node_id in ['215542', '215600', '273933'] else 'monitoring'
                    df['source_file'] = csv_file.name
                    df['data_quality_score'] = 0.8  # Default score
                    df['is_interpolated'] = False
                    df['ingestion_timestamp'] = datetime.now()
                    
                    all_data.append(df)
    
    if all_data:
        # Combine all data
        final_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Total records to load: {len(final_df)}")
        logger.info(f"Unique nodes: {final_df['node_id'].nunique()}")
        logger.info(f"Date range: {final_df['timestamp'].min()} to {final_df['timestamp'].max()}")
        
        # Load to BigQuery
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )
        
        try:
            job = client.load_table_from_dataframe(
                final_df, table_id, job_config=job_config
            )
            job.result()  # Wait for the job to complete
            logger.info(f"Successfully loaded {len(final_df)} records to BigQuery")
        except Exception as e:
            logger.error(f"Error loading to BigQuery: {e}")
            # Save to CSV as backup
            final_df.to_csv('backup_sensor_data.csv', index=False)
            logger.info("Data saved to backup_sensor_data.csv")
    else:
        logger.warning("No data extracted from backup files")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
ETL script to import SCADA CSV data into PostgreSQL with TimescaleDB
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import os
import sys
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': os.environ.get('POSTGRES_PORT', '5432'),
    'database': os.environ.get('POSTGRES_DB', 'abbanoa_processing'),
    'user': os.environ.get('POSTGRES_USER', 'abbanoa_user'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'abbanoa_dev_pass')
}

# Node mapping from CSV columns to database node_ids
NODE_MAPPING = {
    'VIA_SANT_ANNA': {
        'columns': {
            'temperature': '(SELARGIUS) NODO VIA SANT ANNA - TEMPERATURA INTERNA',
            'flow_rate': '(SELARGIUS) NODO VIA SANT ANNA - PORTATA W ISTANTANEA DIRETTA',
            'total_flow': '(SELARGIUS) NODO VIA SANT ANNA - PORTATA W TOTALE DIRETTA',
            'pressure': '(SELARGIUS) NODO VIA SANT ANNA - PRESSIONE USCITA'
        },
        'node_name': 'Nodo Via Sant Anna',
        'node_type': 'distribution',
        'location': 'Selargius'
    },
    'VIA_SENECA': {
        'columns': {
            'temperature': '(SELARGIUS) NODO VIA SENECA - TEMPERATURA INTERNA',
            'flow_rate': '(SELARGIUS) NODO VIA SENECA - PORTATA W ISTANTANEA DIRETTA',
            'total_flow': '(SELARGIUS) NODO VIA SENECA - PORTATA W TOTALE DIRETTA',
            'pressure': '(SELARGIUS) NODO VIA SENECA - PRESSIONE USCITA'
        },
        'node_name': 'Nodo Via Seneca',
        'node_type': 'distribution',
        'location': 'Selargius'
    },
    'SERBATOIO_SELARGIUS': {
        'columns': {
            'flow_rate': '(SELARGIUS) SERBATOIO SELARGIUS - PORTATA USCITA',
            'total_flow': '(SELARGIUS) SERBATOIO SELARGIUS - PORTATA USCITA MQ'
        },
        'node_name': 'Serbatoio Selargius',
        'node_type': 'reservoir',
        'location': 'Selargius'
    },
    'SERBATOIO_CUCCURU_LINU': {
        'columns': {
            'flow_rate': '(QUARTUCCIU) SERBATOIO CUCCURU LINU - PORTATA SELARGIUS',
            'total_flow': '(QUARTUCCIU) SERBATOIO CUCCURU LINU - TOTALIZZATORE PORTATA SELARGIUS'
        },
        'node_name': 'Serbatoio Cuccuru Linu',
        'node_type': 'reservoir',
        'location': 'Quartucciu'
    }
}

def connect_to_db():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to PostgreSQL")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

def create_or_update_nodes(conn):
    """Create or update node records in the database"""
    cursor = conn.cursor()
    
    for node_id, node_info in NODE_MAPPING.items():
        try:
            # Insert or update node
            cursor.execute("""
                INSERT INTO water_infrastructure.nodes 
                (node_id, node_name, node_type, location_name, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (node_id) DO UPDATE
                SET node_name = EXCLUDED.node_name,
                    node_type = EXCLUDED.node_type,
                    location_name = EXCLUDED.location_name,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                node_id,
                node_info['node_name'],
                node_info['node_type'],
                node_info['location'],
                True
            ))
            logger.info(f"Created/Updated node: {node_id}")
        except Exception as e:
            logger.error(f"Error creating node {node_id}: {e}")
            raise
    
    conn.commit()
    logger.info("All nodes created/updated successfully")

def parse_italian_date(date_str: str, time_str: str) -> datetime:
    """Parse Italian date format DD/MM/YYYY with time HH:MM:SS"""
    datetime_str = f"{date_str} {time_str}"
    return datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")

def clean_numeric_value(value):
    """Clean and convert numeric values, handling Italian decimal format"""
    if pd.isna(value) or value == '' or value == 0:
        return None
    # Replace comma with dot for decimal separator
    if isinstance(value, str):
        value = value.replace(',', '.')
    try:
        return float(value)
    except:
        return None

def process_csv_data(csv_path: str) -> List[Tuple]:
    """Process CSV file and prepare data for insertion"""
    logger.info(f"Reading CSV file: {csv_path}")
    
    # Read CSV with Italian format
    df = pd.read_csv(csv_path, sep=';', skiprows=1)  # Skip units row
    
    # Read the header row to get column names
    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(';')
    
    df.columns = header
    
    logger.info(f"Loaded {len(df)} rows from CSV")
    
    all_records = []
    
    for idx, row in df.iterrows():
        try:
            # Parse timestamp
            timestamp = parse_italian_date(row['DATA'], row['ORA'])
            
            # Process each node's data
            for node_id, node_info in NODE_MAPPING.items():
                record = {
                    'timestamp': timestamp,
                    'node_id': node_id,
                    'temperature': None,
                    'flow_rate': None,
                    'pressure': None,
                    'total_flow': None,
                    'quality_score': None,
                    'is_interpolated': False
                }
                
                # Extract values for this node
                for field, column_name in node_info['columns'].items():
                    if column_name in row:
                        value = clean_numeric_value(row[column_name])
                        if field == 'total_flow':
                            # Total flow is cumulative, we might want to calculate the difference
                            record['total_flow'] = value
                        else:
                            record[field] = value
                
                # Calculate a basic quality score based on data completeness (0-1 scale for DECIMAL(3,2))
                non_null_count = sum(1 for k, v in record.items() 
                                   if k not in ['timestamp', 'node_id', 'quality_score', 'is_interpolated'] 
                                   and v is not None)
                record['quality_score'] = round((non_null_count / 4.0), 2)  # 0-1 scale, not percentage
                
                all_records.append((
                    record['timestamp'],
                    record['node_id'],
                    record['temperature'],
                    record['flow_rate'],
                    record['pressure'],
                    record['total_flow'],
                    record['quality_score'],
                    record['is_interpolated'],
                    None  # raw_data (JSONB)
                ))
                
        except Exception as e:
            logger.warning(f"Error processing row {idx}: {e}")
            continue
    
    logger.info(f"Processed {len(all_records)} sensor reading records")
    return all_records

def insert_sensor_readings(conn, records: List[Tuple]):
    """Batch insert sensor readings into the database"""
    cursor = conn.cursor()
    
    # Prepare the insert query
    insert_query = """
        INSERT INTO water_infrastructure.sensor_readings 
        (timestamp, node_id, temperature, flow_rate, pressure, total_flow, 
         quality_score, is_interpolated, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp, node_id) DO UPDATE
        SET temperature = EXCLUDED.temperature,
            flow_rate = EXCLUDED.flow_rate,
            pressure = EXCLUDED.pressure,
            total_flow = EXCLUDED.total_flow,
            quality_score = EXCLUDED.quality_score,
            is_interpolated = EXCLUDED.is_interpolated
    """
    
    try:
        # Batch insert for better performance
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            execute_batch(cursor, insert_query, batch, page_size=100)
            conn.commit()
            logger.info(f"Inserted batch {i//batch_size + 1}/{(len(records) + batch_size - 1)//batch_size}")
        
        logger.info(f"Successfully inserted {len(records)} sensor readings")
    except Exception as e:
        logger.error(f"Error inserting sensor readings: {e}")
        conn.rollback()
        raise

def calculate_daily_aggregates(conn):
    """Calculate daily aggregates for all nodes"""
    cursor = conn.cursor()
    
    try:
        # Get distinct dates and nodes
        cursor.execute("""
            SELECT DISTINCT DATE(timestamp) as date, node_id
            FROM water_infrastructure.sensor_readings
            ORDER BY date, node_id
        """)
        
        date_nodes = cursor.fetchall()
        
        for date, node_id in date_nodes:
            cursor.execute("""
                SELECT water_infrastructure.calculate_daily_aggregates(%s, %s)
            """, (date, node_id))
        
        conn.commit()
        logger.info(f"Calculated daily aggregates for {len(date_nodes)} date-node combinations")
    except Exception as e:
        logger.error(f"Error calculating daily aggregates: {e}")
        conn.rollback()

def main():
    """Main ETL process"""
    csv_path = "/app/DATA/Report Scada dal 14-11-24 al 19-06-25.csv"
    
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)
    
    # Connect to database
    conn = connect_to_db()
    
    try:
        # Step 1: Create or update nodes
        logger.info("Step 1: Creating/updating nodes...")
        create_or_update_nodes(conn)
        
        # Step 2: Process CSV data
        logger.info("Step 2: Processing CSV data...")
        records = process_csv_data(csv_path)
        
        # Step 3: Insert sensor readings
        logger.info("Step 3: Inserting sensor readings...")
        insert_sensor_readings(conn, records)
        
        # Step 4: Calculate daily aggregates
        logger.info("Step 4: Calculating daily aggregates...")
        calculate_daily_aggregates(conn)
        
        # Verify the import
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total_records,
                   COUNT(DISTINCT node_id) as nodes,
                   MIN(timestamp) as first_reading,
                   MAX(timestamp) as last_reading
            FROM water_infrastructure.sensor_readings
        """)
        
        result = cursor.fetchone()
        logger.info(f"""
        Import Summary:
        - Total records: {result[0]}
        - Nodes: {result[1]}
        - Date range: {result[2]} to {result[3]}
        """)
        
        logger.info("ETL process completed successfully!")
        
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
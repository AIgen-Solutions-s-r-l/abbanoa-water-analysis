#!/usr/bin/env python3
"""
Direct sync sensor data from BigQuery sensor_readings_ml to PostgreSQL.
"""

import asyncio
import sys
from datetime import datetime, timedelta
import logging

# Add project root to path
sys.path.append('/home/alessio/Customers/Abbanoa')

from google.cloud import bigquery
from src.infrastructure.database.postgres_manager import get_postgres_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def sync_sensor_data():
    """Sync sensor data directly from BigQuery to PostgreSQL."""
    logger.info("Starting direct sensor data sync")
    
    # Initialize connections
    postgres_manager = await get_postgres_manager()
    bigquery_client = bigquery.Client()
    
    # Query to get all sensor data
    query = """
    SELECT 
        node_id,
        timestamp,
        flow_rate,
        pressure,
        temperature,
        volume,
        district_id,
        node_name,
        node_type,
        data_quality_score
    FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
    WHERE timestamp >= '2024-11-01'
    ORDER BY timestamp
    LIMIT 100000
    """
    
    logger.info("Querying BigQuery for sensor data...")
    query_job = bigquery_client.query(query)
    results = query_job.result()
    
    # Convert to list for batch processing
    rows = list(results)
    total_rows = len(rows)
    logger.info(f"Found {total_rows} rows to sync")
    
    if total_rows == 0:
        logger.warning("No data found in BigQuery")
        return
    
    # Process in batches
    batch_size = 1000
    processed = 0
    
    async with postgres_manager.acquire() as conn:
        # Create temporary table matching actual schema
        await conn.execute("""
            CREATE TEMP TABLE temp_sensor_readings (
                timestamp TIMESTAMPTZ,
                node_id VARCHAR(50),
                temperature NUMERIC(5,2),
                flow_rate NUMERIC(10,2),
                pressure NUMERIC(6,2),
                total_flow NUMERIC(12,2),
                quality_score NUMERIC(3,2),
                is_interpolated BOOLEAN DEFAULT false,
                raw_data JSONB
            )
        """)
        
        for i in range(0, total_rows, batch_size):
            batch = rows[i:i+batch_size]
            
            # Prepare batch data
            values = []
            for row in batch:
                import json
                raw_data = json.dumps({
                    'district_id': row.district_id,
                    'node_name': row.node_name,
                    'node_type': row.node_type
                })
                values.append((
                    row.timestamp,
                    row.node_id,
                    float(row.temperature) if row.temperature is not None else None,
                    float(row.flow_rate) if row.flow_rate is not None else None,
                    float(row.pressure) if row.pressure is not None else None,
                    float(row.volume) if row.volume is not None else None,  # Use volume as total_flow
                    float(row.data_quality_score) if row.data_quality_score is not None else 1.0,
                    False,  # is_interpolated
                    raw_data
                ))
            
            # Insert batch into temp table
            await conn.executemany("""
                INSERT INTO temp_sensor_readings 
                (timestamp, node_id, temperature, flow_rate, pressure, 
                 total_flow, quality_score, is_interpolated, raw_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
            """, values)
            
            processed += len(batch)
            logger.info(f"Processed {processed}/{total_rows} rows")
        
        # Insert into actual table
        inserted = await conn.fetch("""
            INSERT INTO water_infrastructure.sensor_readings 
            (timestamp, node_id, temperature, flow_rate, pressure, 
             total_flow, quality_score, is_interpolated, raw_data)
            SELECT * FROM temp_sensor_readings
        """)
        
        logger.info(f"Inserted {total_rows} records")
        
    logger.info("Sync completed successfully!")
    
    # Verify the data
    async with postgres_manager.acquire() as conn:
        count = await conn.fetchval("""
            SELECT COUNT(*) FROM water_infrastructure.sensor_readings
        """)
        min_date = await conn.fetchval("""
            SELECT MIN(timestamp) FROM water_infrastructure.sensor_readings
        """)
        max_date = await conn.fetchval("""
            SELECT MAX(timestamp) FROM water_infrastructure.sensor_readings
        """)
        
        logger.info(f"PostgreSQL now has {count} records")
        logger.info(f"Date range: {min_date} to {max_date}")


async def main():
    """Main function."""
    try:
        await sync_sensor_data()
        logger.info("✅ Direct sensor data sync completed successfully!")
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
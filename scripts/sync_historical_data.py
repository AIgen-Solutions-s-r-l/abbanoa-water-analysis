#!/usr/bin/env python3
"""
Script to sync historical data from BigQuery to PostgreSQL.

This script loads historical data for the specified time range,
enabling the dashboard to display data for longer periods like 1 year.
"""

import asyncio
import sys
from datetime import datetime, timedelta
import logging

# Add project root to path
sys.path.append('/home/alessio/Customers/Abbanoa')

from src.infrastructure.etl.bigquery_to_postgres_etl import BigQueryToPostgresETL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def sync_historical_data(days_back: int = 365):
    """
    Sync historical data from BigQuery to PostgreSQL.
    
    Args:
        days_back: Number of days of historical data to sync
    """
    logger.info(f"Starting historical data sync for {days_back} days")
    
    # Initialize ETL pipeline
    etl = BigQueryToPostgresETL()
    await etl.initialize()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    logger.info(f"Syncing data from {start_date} to {end_date}")
    
    # Run historical sync
    stats = await etl.sync_historical_data(start_date, end_date)
    
    # Log results
    logger.info("Historical sync completed:")
    logger.info(f"  Total records: {stats.get('total_records', 0)}")
    logger.info(f"  Processed records: {stats.get('processed_records', 0)}")
    logger.info(f"  Failed records: {stats.get('failed_records', 0)}")
    logger.info(f"  Duration: {stats.get('duration', 'N/A')}")
    
    return stats


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync historical data from BigQuery to PostgreSQL')
    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days of historical data to sync (default: 365)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh even if data exists'
    )
    
    args = parser.parse_args()
    
    try:
        # Run sync
        stats = await sync_historical_data(days_back=args.days)
        
        if stats.get('processed_records', 0) > 0:
            logger.info("✅ Historical data sync completed successfully!")
            logger.info("You should now be able to view data for the selected time range in the dashboard.")
        else:
            logger.warning("⚠️ No records were processed. Check if:")
            logger.warning("1. BigQuery contains data for the requested time range")
            logger.warning("2. The data might already be synced (use --force to re-sync)")
            
    except Exception as e:
        logger.error(f"❌ Historical sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
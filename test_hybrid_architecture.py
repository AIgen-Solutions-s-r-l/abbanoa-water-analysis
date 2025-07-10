#!/usr/bin/env python3
"""
Test script for the hybrid architecture implementation.
This script validates all components of the three-tier data architecture.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HybridArchitectureTest:
    """Test suite for hybrid architecture components."""
    
    def __init__(self):
        self.results = {
            "redis": {"status": "not_tested", "details": {}},
            "postgres": {"status": "not_tested", "details": {}},
            "bigquery": {"status": "not_tested", "details": {}},
            "etl": {"status": "not_tested", "details": {}},
            "hybrid_service": {"status": "not_tested", "details": {}},
            "dashboard": {"status": "not_tested", "details": {}}
        }
        
    async def run_all_tests(self):
        """Run all tests in sequence."""
        print("🧪 Starting Hybrid Architecture Tests")
        print("=" * 60)
        
        # Test 1: Redis
        await self.test_redis()
        
        # Test 2: PostgreSQL
        await self.test_postgres()
        
        # Test 3: BigQuery
        await self.test_bigquery()
        
        # Test 4: ETL Pipeline
        await self.test_etl_pipeline()
        
        # Test 5: Hybrid Data Service
        await self.test_hybrid_service()
        
        # Test 6: Dashboard
        await self.test_dashboard()
        
        # Print summary
        self.print_summary()
        
    async def test_redis(self):
        """Test Redis connection and basic operations."""
        print("\n📍 Testing Redis...")
        
        try:
            from src.infrastructure.cache.redis_cache_manager import RedisCacheManager
            
            # Initialize Redis manager
            redis_manager = RedisCacheManager()
            
            # Test 1: Connection
            redis_manager.redis_client.ping()
            self.results["redis"]["details"]["connection"] = "✅ Connected"
            
            # Test 2: Write operation
            test_key = "test:hybrid:timestamp"
            test_value = datetime.now().isoformat()
            redis_manager.redis_client.set(test_key, test_value)
            self.results["redis"]["details"]["write"] = "✅ Write successful"
            
            # Test 3: Read operation
            retrieved = redis_manager.redis_client.get(test_key)
            if retrieved == test_value:
                self.results["redis"]["details"]["read"] = "✅ Read successful"
            else:
                self.results["redis"]["details"]["read"] = "❌ Read failed"
                
            # Test 4: TTL operation
            redis_manager.redis_client.expire(test_key, 60)
            ttl = redis_manager.redis_client.ttl(test_key)
            if ttl > 0:
                self.results["redis"]["details"]["ttl"] = f"✅ TTL set ({ttl}s)"
            else:
                self.results["redis"]["details"]["ttl"] = "❌ TTL failed"
                
            # Test 5: Cleanup
            redis_manager.redis_client.delete(test_key)
            
            self.results["redis"]["status"] = "passed"
            print("✅ Redis tests passed")
            
        except Exception as e:
            self.results["redis"]["status"] = "failed"
            self.results["redis"]["details"]["error"] = str(e)
            print(f"❌ Redis tests failed: {e}")
            
    async def test_postgres(self):
        """Test PostgreSQL/TimescaleDB connection and operations."""
        print("\n📍 Testing PostgreSQL/TimescaleDB...")
        
        try:
            from src.infrastructure.database.postgres_manager import get_postgres_manager
            
            # Get PostgreSQL manager
            postgres = await get_postgres_manager()
            
            # Test 1: Connection
            async with postgres.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                self.results["postgres"]["details"]["connection"] = "✅ Connected"
                self.results["postgres"]["details"]["version"] = version.split(',')[0]
                
                # Test 2: TimescaleDB extension
                timescale = await conn.fetchval(
                    "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb')"
                )
                if timescale:
                    self.results["postgres"]["details"]["timescaledb"] = "✅ TimescaleDB installed"
                else:
                    self.results["postgres"]["details"]["timescaledb"] = "❌ TimescaleDB not found"
                    
                # Test 3: Check hypertables
                hypertables = await conn.fetch("""
                    SELECT hypertable_name, num_chunks 
                    FROM timescaledb_information.hypertables
                    WHERE hypertable_schema = 'water_infrastructure'
                """)
                self.results["postgres"]["details"]["hypertables"] = f"✅ {len(hypertables)} hypertables found"
                
                # Test 4: Check continuous aggregates
                aggregates = await conn.fetch("""
                    SELECT view_name 
                    FROM timescaledb_information.continuous_aggregates
                    WHERE view_schema = 'water_infrastructure'
                """)
                self.results["postgres"]["details"]["aggregates"] = f"✅ {len(aggregates)} continuous aggregates"
                
                # Test 5: Sample data check
                count = await conn.fetchval("""
                    SELECT COUNT(*) 
                    FROM water_infrastructure.sensor_readings
                    WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
                """)
                self.results["postgres"]["details"]["recent_data"] = f"📊 {count} readings (last 7 days)"
                
            self.results["postgres"]["status"] = "passed"
            print("✅ PostgreSQL tests passed")
            
        except Exception as e:
            self.results["postgres"]["status"] = "failed"
            self.results["postgres"]["details"]["error"] = str(e)
            print(f"❌ PostgreSQL tests failed: {e}")
            
    async def test_bigquery(self):
        """Test BigQuery connection."""
        print("\n📍 Testing BigQuery...")
        
        try:
            from src.infrastructure.bigquery.bigquery_client import BigQueryClient
            
            # Initialize BigQuery client
            bq_client = BigQueryClient()
            
            # Test connection with a simple query
            query = f"""
            SELECT COUNT(*) as count
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.sensor_readings`
            WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
            """
            
            result = bq_client.client.query(query).result()
            for row in result:
                count = row.count
                
            self.results["bigquery"]["status"] = "passed"
            self.results["bigquery"]["details"]["connection"] = "✅ Connected"
            self.results["bigquery"]["details"]["recent_data"] = f"📊 {count} readings (last 24h)"
            print("✅ BigQuery tests passed")
            
        except Exception as e:
            self.results["bigquery"]["status"] = "failed"
            self.results["bigquery"]["details"]["error"] = str(e)
            print(f"❌ BigQuery tests failed: {e}")
            
    async def test_etl_pipeline(self):
        """Test ETL pipeline functionality."""
        print("\n📍 Testing ETL Pipeline...")
        
        try:
            from src.infrastructure.database.postgres_manager import get_postgres_manager
            
            postgres = await get_postgres_manager()
            
            # Check ETL job history
            async with postgres.acquire() as conn:
                recent_jobs = await conn.fetch("""
                    SELECT job_name, status, started_at, records_processed
                    FROM water_infrastructure.etl_jobs
                    WHERE started_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    ORDER BY started_at DESC
                    LIMIT 5
                """)
                
                if recent_jobs:
                    self.results["etl"]["details"]["recent_jobs"] = f"✅ {len(recent_jobs)} jobs in last 24h"
                    
                    # Check job success rate
                    success_count = sum(1 for job in recent_jobs if job['status'] == 'completed')
                    success_rate = (success_count / len(recent_jobs)) * 100
                    self.results["etl"]["details"]["success_rate"] = f"📊 {success_rate:.0f}% success rate"
                else:
                    self.results["etl"]["details"]["recent_jobs"] = "⚠️ No recent jobs found"
                    
            # Test small sync
            from src.infrastructure.etl.bigquery_to_postgres_etl import BigQueryToPostgresETL
            
            print("  Running test sync (last 1 hour)...")
            etl = BigQueryToPostgresETL(batch_size=1000)
            await etl.initialize()
            
            stats = await etl.sync_recent_data(hours_back=1, force_refresh=True)
            
            self.results["etl"]["details"]["test_sync"] = f"✅ Synced {stats['processed_records']} records"
            self.results["etl"]["status"] = "passed"
            print("✅ ETL tests passed")
            
        except Exception as e:
            self.results["etl"]["status"] = "failed"
            self.results["etl"]["details"]["error"] = str(e)
            print(f"❌ ETL tests failed: {e}")
            
    async def test_hybrid_service(self):
        """Test hybrid data service functionality."""
        print("\n📍 Testing Hybrid Data Service...")
        
        try:
            from src.infrastructure.data.hybrid_data_service import get_hybrid_data_service
            
            # Get hybrid service
            service = await get_hybrid_data_service()
            
            # Test 1: Get system metrics
            metrics = await service.get_system_metrics("24h")
            if metrics:
                self.results["hybrid_service"]["details"]["system_metrics"] = "✅ Retrieved system metrics"
                self.results["hybrid_service"]["details"]["active_nodes"] = f"📊 {metrics.get('active_nodes', 0)} active nodes"
            else:
                self.results["hybrid_service"]["details"]["system_metrics"] = "❌ No metrics retrieved"
                
            # Test 2: Get latest readings
            latest = await service.get_latest_readings()
            if latest:
                self.results["hybrid_service"]["details"]["latest_readings"] = f"✅ Retrieved {len(latest)} node readings"
            else:
                self.results["hybrid_service"]["details"]["latest_readings"] = "❌ No readings retrieved"
                
            # Test 3: Test tiered query
            if latest:
                node_id = list(latest.keys())[0]
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=1)
                
                data = await service.get_node_data(node_id, start_time, end_time)
                if data is not None and not data.empty:
                    self.results["hybrid_service"]["details"]["tiered_query"] = f"✅ Retrieved {len(data)} rows"
                else:
                    self.results["hybrid_service"]["details"]["tiered_query"] = "❌ No data retrieved"
                    
            self.results["hybrid_service"]["status"] = "passed"
            print("✅ Hybrid service tests passed")
            
        except Exception as e:
            self.results["hybrid_service"]["status"] = "failed"
            self.results["hybrid_service"]["details"]["error"] = str(e)
            print(f"❌ Hybrid service tests failed: {e}")
            
    async def test_dashboard(self):
        """Test dashboard connectivity."""
        print("\n📍 Testing Dashboard...")
        
        try:
            import requests
            
            # Check if dashboard is running
            response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
            
            if response.status_code == 200:
                self.results["dashboard"]["status"] = "passed"
                self.results["dashboard"]["details"]["health"] = "✅ Dashboard is running"
            else:
                self.results["dashboard"]["status"] = "failed"
                self.results["dashboard"]["details"]["health"] = f"❌ Unexpected status: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            self.results["dashboard"]["status"] = "not_running"
            self.results["dashboard"]["details"]["health"] = "⚠️ Dashboard not running (start with 'streamlit run src/presentation/streamlit/app.py')"
        except Exception as e:
            self.results["dashboard"]["status"] = "failed"
            self.results["dashboard"]["details"]["error"] = str(e)
            
        print(f"{'✅' if self.results['dashboard']['status'] == 'passed' else '⚠️'} Dashboard tests completed")
        
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        all_passed = True
        
        for component, result in self.results.items():
            status = result["status"]
            icon = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
            
            print(f"\n{icon} {component.upper()}: {status}")
            
            for key, value in result["details"].items():
                print(f"  - {key}: {value}")
                
            if status != "passed":
                all_passed = False
                
        print("\n" + "=" * 60)
        
        if all_passed:
            print("🎉 ALL TESTS PASSED! The hybrid architecture is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the details above.")
            
        print("\n📝 Next Steps:")
        if self.results["redis"]["status"] != "passed":
            print("  1. Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
        if self.results["postgres"]["status"] != "passed":
            print("  2. Start PostgreSQL: docker-compose up -d postgres")
            print("     Then initialize: docker exec -i abbanoa-postgres psql -U postgres < src/infrastructure/database/postgres_schema.sql")
        if self.results["etl"]["status"] != "passed":
            print("  3. Run initial sync: python -m src.infrastructure.etl.bigquery_to_postgres_etl")
        if self.results["dashboard"]["status"] != "passed":
            print("  4. Start dashboard: streamlit run src/presentation/streamlit/app.py")


async def main():
    """Main test runner."""
    tester = HybridArchitectureTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
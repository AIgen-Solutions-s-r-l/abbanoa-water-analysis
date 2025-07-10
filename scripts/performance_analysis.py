#!/usr/bin/env python3
"""
Performance analysis script for the Abbanoa dashboard.

This script tests different time ranges and components to identify performance bottlenecks.
"""

import asyncio
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from uuid import UUID

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.di_container import Container


class PerformanceAnalyzer:
    """Performance analyzer for dashboard components."""
    
    def __init__(self):
        """Initialize the performance analyzer."""
        self.container = Container()
        self.container.config.from_dict({
            "bigquery": {
                "project_id": "abbanoa-464816",
                "dataset_id": "water_infrastructure",
                "credentials_path": None,
                "location": "EU",
            }
        })
        self.sensor_repo = self.container.sensor_reading_repository()
        
        # Node mappings for testing
        self.node_mapping = {
            "Primary Station": UUID("00000000-0000-0000-0000-000000000001"),
            "Secondary Station": UUID("00000000-0000-0000-0000-000000000002"),
            "Distribution A": UUID("00000000-0000-0000-0000-000000000003"),
            "Distribution B": UUID("00000000-0000-0000-0000-000000000004"),
            "Junction C": UUID("00000000-0000-0000-0000-000000000005"),
            "Supply Control": UUID("00000000-0000-0000-0000-000000000006"),
            "Pressure Station": UUID("00000000-0000-0000-0000-000000000007"),
            "Remote Point": UUID("00000000-0000-0000-0000-000000000008"),
        }
        
        # Time ranges to test
        self.time_ranges = {
            "Last 6 Hours": timedelta(hours=6),
            "Last 24 Hours": timedelta(hours=24),
            "Last 3 Days": timedelta(days=3),
            "Last Week": timedelta(days=7),
            "Last Month": timedelta(days=30),
            "Last Year": timedelta(days=365),
        }
    
    def measure_time(self, func_name: str):
        """Decorator to measure execution time."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    print(f"❌ Error in {func_name}: {error}")
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                print(f"⏱️  {func_name}: {execution_time:.2f}s {'✅' if success else '❌'}")
                
                return result, execution_time, success
            return wrapper
        return decorator
    
    async def test_single_node_performance(self, node_name: str, node_id: UUID, time_range_name: str, delta: timedelta):
        """Test performance for a single node and time range."""
        print(f"\n📊 Testing {node_name} - {time_range_name}")
        
        # Calculate time window
        data_end = datetime(2025, 3, 31, 23, 59, 59)
        data_start = datetime(2024, 11, 13, 0, 0, 0)
        end_time = min(data_end, datetime.now())
        start_time = max(data_start, end_time - delta)
        
        @self.measure_time(f"Fetch {node_name} data")
        async def fetch_node_data():
            readings = await self.sensor_repo.get_by_node_id(
                node_id=node_id,
                start_time=start_time,
                end_time=end_time,
            )
            return readings
        
        readings, exec_time, success = await fetch_node_data()
        
        if success and readings:
            print(f"   📈 Retrieved {len(readings)} readings")
            print(f"   🕒 Time range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
            
            # Calculate data processing time
            @self.measure_time(f"Process {node_name} data")
            async def process_data():
                flows = []
                pressures = []
                for reading in readings:
                    # Simulate data processing
                    flow_val = reading.flow_rate
                    if hasattr(flow_val, "value"):
                        flow_val = flow_val.value
                    if flow_val and flow_val > 0:
                        flows.append(float(flow_val))
                    
                    pressure_val = reading.pressure
                    if hasattr(pressure_val, "value"):
                        pressure_val = pressure_val.value
                    if pressure_val and pressure_val > 0:
                        pressures.append(float(pressure_val))
                
                return len(flows), len(pressures)
            
            result, process_time, success = await process_data()
            if success and result:
                flow_count, pressure_count = result
                print(f"   💧 Processed {flow_count} flow readings, {pressure_count} pressure readings")
            else:
                flow_count, pressure_count = 0, 0
            
            return {
                'node_name': node_name,
                'time_range': time_range_name,
                'fetch_time': exec_time,
                'process_time': process_time,
                'total_time': exec_time + process_time,
                'record_count': len(readings),
                'flow_count': flow_count,
                'pressure_count': pressure_count,
                'success': True
            }
        else:
            return {
                'node_name': node_name,
                'time_range': time_range_name,
                'fetch_time': exec_time if success else 0,
                'process_time': 0,
                'total_time': exec_time if success else 0,
                'record_count': 0,
                'flow_count': 0,
                'pressure_count': 0,
                'success': False
            }
    
    async def test_all_nodes_performance(self, time_range_name: str, delta: timedelta):
        """Test performance for all nodes for a specific time range."""
        print(f"\n🔍 Testing all nodes - {time_range_name}")
        print("=" * 60)
        
        results = []
        total_start_time = time.time()
        
        for node_name, node_id in self.node_mapping.items():
            result = await self.test_single_node_performance(node_name, node_id, time_range_name, delta)
            results.append(result)
        
        total_time = time.time() - total_start_time
        
        # Summary statistics
        successful_results = [r for r in results if r['success']]
        if successful_results:
            total_records = sum(r['record_count'] for r in successful_results)
            avg_fetch_time = sum(r['fetch_time'] for r in successful_results) / len(successful_results)
            max_fetch_time = max(r['fetch_time'] for r in successful_results)
            
            print(f"\n📋 Summary for {time_range_name}:")
            print(f"   ⏱️  Total time: {total_time:.2f}s")
            print(f"   📊 Successful nodes: {len(successful_results)}/{len(results)}")
            print(f"   📈 Total records: {total_records:,}")
            print(f"   ⚡ Avg fetch time: {avg_fetch_time:.2f}s")
            print(f"   🔥 Max fetch time: {max_fetch_time:.2f}s")
            
            if max_fetch_time > 10:
                print(f"   ⚠️  WARNING: Maximum fetch time exceeds 10 seconds!")
            if total_time > 30:
                print(f"   ⚠️  WARNING: Total time for all nodes exceeds 30 seconds!")
        
        return results, total_time
    
    async def run_comprehensive_analysis(self):
        """Run comprehensive performance analysis."""
        print("🚀 Starting Comprehensive Performance Analysis")
        print("=" * 60)
        
        all_results = []
        
        for time_range_name, delta in self.time_ranges.items():
            results, total_time = await self.test_all_nodes_performance(time_range_name, delta)
            
            # Add total time to each result
            for result in results:
                result['total_all_nodes_time'] = total_time
            
            all_results.extend(results)
            
            # Wait between tests to avoid overwhelming the system
            if time_range_name != list(self.time_ranges.keys())[-1]:  # Not the last one
                print("\n⏳ Waiting 5 seconds before next test...")
                await asyncio.sleep(5)
        
        # Generate final report
        self.generate_report(all_results)
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate a comprehensive performance report."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PERFORMANCE REPORT")
        print("=" * 80)
        
        # Group by time range
        time_range_stats = {}
        for result in results:
            time_range = result['time_range']
            if time_range not in time_range_stats:
                time_range_stats[time_range] = []
            time_range_stats[time_range].append(result)
        
        # Analyze each time range
        print("\n🔍 Performance by Time Range:")
        print("-" * 50)
        
        bottlenecks = []
        
        for time_range, range_results in time_range_stats.items():
            successful = [r for r in range_results if r['success']]
            if successful:
                avg_time = sum(r['total_time'] for r in successful) / len(successful)
                max_time = max(r['total_time'] for r in successful)
                total_records = sum(r['record_count'] for r in successful)
                total_all_nodes_time = successful[0]['total_all_nodes_time']
                
                print(f"\n📅 {time_range}:")
                print(f"   ⏱️  Avg node time: {avg_time:.2f}s")
                print(f"   🔥 Max node time: {max_time:.2f}s")
                print(f"   🕒 Total all nodes: {total_all_nodes_time:.2f}s")
                print(f"   📈 Total records: {total_records:,}")
                print(f"   📊 Records/second: {total_records/total_all_nodes_time:.0f}")
                
                # Identify bottlenecks
                if max_time > 15:
                    bottlenecks.append(f"⚠️  {time_range}: Individual node taking {max_time:.2f}s")
                if total_all_nodes_time > 60:
                    bottlenecks.append(f"⚠️  {time_range}: Total time {total_all_nodes_time:.2f}s exceeds 1 minute")
                if total_records > 100000:
                    bottlenecks.append(f"⚠️  {time_range}: Large dataset ({total_records:,} records)")
        
        # Recommendations
        print("\n🚀 PERFORMANCE RECOMMENDATIONS:")
        print("-" * 50)
        
        if bottlenecks:
            print("\n❌ Issues Found:")
            for bottleneck in bottlenecks:
                print(f"   {bottleneck}")
            
            print("\n💡 Recommendations:")
            print("   1. Implement data sampling for time ranges > 1 month")
            print("   2. Add pagination for large datasets")
            print("   3. Consider data aggregation for long time periods")
            print("   4. Optimize BigQuery queries with better indexing")
            print("   5. Implement progressive loading (show partial results)")
            print("   6. Add data compression for large transfers")
        else:
            print("✅ No major performance issues detected!")
            print("   System is performing within acceptable limits.")
        
        # Specific recommendations for 1 year
        year_results = time_range_stats.get("Last Year", [])
        if year_results:
            year_successful = [r for r in year_results if r['success']]
            if year_successful:
                year_total_time = year_successful[0]['total_all_nodes_time']
                year_records = sum(r['record_count'] for r in year_successful)
                
                print(f"\n📅 Specific Analysis for 'Last Year':")
                print(f"   🕒 Total loading time: {year_total_time:.2f}s")
                print(f"   📊 Total records: {year_records:,}")
                
                if year_total_time > 30:
                    print(f"   ⚠️  CRITICAL: 1-year data takes {year_total_time:.2f}s to load")
                    print("   🔧 Urgent recommendations:")
                    print("      - Implement data sampling (e.g., daily averages instead of raw data)")
                    print("      - Add time-based data aggregation")
                    print("      - Consider caching pre-computed yearly summaries")
                    print("      - Limit 1-year view to summary metrics only")


async def main():
    """Main function to run performance analysis."""
    analyzer = PerformanceAnalyzer()
    
    print("🔧 Initializing performance analyzer...")
    
    try:
        await analyzer.run_comprehensive_analysis()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 
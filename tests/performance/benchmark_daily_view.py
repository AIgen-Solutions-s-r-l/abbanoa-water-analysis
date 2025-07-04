#!/usr/bin/env python3
"""
Performance Benchmarks for vw_daily_timeseries View
Purpose: Validate query performance meets SLA requirements
Owner: Data Engineering Team
Created: 2025-07-04

Performance Requirements:
- Query 5 years of data: < 1 second
- Query single month: < 100ms  
- Query with filters: < 500ms
- Concurrent query handling
"""

import time
import asyncio
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BigQueryBenchmark:
    """Performance benchmark suite for BigQuery views."""
    
    def __init__(self, project_id: str = "abbanoa-464816", dataset_id: str = "water_infrastructure"):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.view_name = "vw_daily_timeseries"
        self.results = {}
        
    def run_query_benchmark(self, query: str, description: str, expected_time_ms: int, iterations: int = 5) -> Dict:
        """Run a query multiple times and collect performance metrics."""
        
        logger.info(f"Running benchmark: {description}")
        execution_times = []
        row_counts = []
        bytes_processed = []
        
        for i in range(iterations):
            logger.info(f"  Iteration {i+1}/{iterations}")
            
            # Configure query job
            job_config = QueryJobConfig()
            job_config.use_query_cache = False  # Disable cache for accurate timing
            job_config.use_legacy_sql = False
            
            start_time = time.perf_counter()
            
            try:
                # Execute query
                query_job = self.client.query(query, job_config=job_config)
                results = query_job.result()
                
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000
                
                # Collect metrics
                execution_times.append(execution_time_ms)
                row_counts.append(query_job.num_dml_affected_rows or len(list(results)))
                bytes_processed.append(query_job.total_bytes_processed or 0)
                
                logger.info(f"    Execution time: {execution_time_ms:.2f}ms")
                
            except Exception as e:
                logger.error(f"    Query failed: {str(e)}")
                execution_times.append(float('inf'))
                row_counts.append(0)
                bytes_processed.append(0)
        
        # Calculate statistics
        avg_time = statistics.mean(execution_times)
        median_time = statistics.median(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        # Performance assessment
        passed = avg_time <= expected_time_ms
        
        benchmark_result = {
            'description': description,
            'query': query,
            'iterations': iterations,
            'avg_execution_time_ms': avg_time,
            'median_execution_time_ms': median_time,
            'min_execution_time_ms': min_time,
            'max_execution_time_ms': max_time,
            'std_dev_ms': std_dev,
            'expected_time_ms': expected_time_ms,
            'performance_passed': passed,
            'avg_rows_returned': statistics.mean(row_counts),
            'avg_bytes_processed': statistics.mean(bytes_processed),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"  Results: avg={avg_time:.2f}ms, expected<={expected_time_ms}ms, passed={passed}")
        
        return benchmark_result
    
    def benchmark_full_dataset_query(self) -> Dict:
        """Benchmark querying the full 5-year dataset."""
        
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT date_utc) as unique_dates,
            COUNT(DISTINCT district_id) as unique_districts,
            COUNT(DISTINCT metric_type) as unique_metrics,
            MIN(date_utc) as earliest_date,
            MAX(date_utc) as latest_date
        FROM `{self.project_id}.{self.dataset_id}.{self.view_name}`
        WHERE date_utc >= DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 5 YEAR)
        """
        
        return self.run_query_benchmark(
            query=query,
            description="Full 5-year dataset aggregation",
            expected_time_ms=1000,  # < 1 second
            iterations=3
        )
    
    def benchmark_single_month_query(self) -> Dict:
        """Benchmark querying a single month of data."""
        
        query = f"""
        SELECT 
            date_utc,
            district_id,
            metric_type,
            avg_value,
            min_value,
            max_value,
            count_readings,
            data_quality_flag
        FROM `{self.project_id}.{self.dataset_id}.{self.view_name}`
        WHERE date_utc BETWEEN '2024-01-01' AND '2024-01-31'
        ORDER BY date_utc, district_id, metric_type
        """
        
        return self.run_query_benchmark(
            query=query,
            description="Single month detailed query",
            expected_time_ms=100,  # < 100ms
            iterations=5
        )
    
    def benchmark_filtered_query(self) -> Dict:
        """Benchmark querying with multiple filters."""
        
        query = f"""
        SELECT 
            date_utc,
            district_id,
            metric_type,
            avg_value,
            percentile_50,
            percentile_95,
            data_quality_flag,
            gap_filled_flag
        FROM `{self.project_id}.{self.dataset_id}.{self.view_name}`
        WHERE date_utc BETWEEN '2023-06-01' AND '2023-12-31'
            AND district_id IN ('DIST_001', 'DIST_002')
            AND metric_type = 'flow_rate'
            AND data_quality_flag = 'GOOD'
            AND avg_value IS NOT NULL
        ORDER BY date_utc DESC
        """
        
        return self.run_query_benchmark(
            query=query,
            description="Filtered query with conditions",
            expected_time_ms=500,  # < 500ms
            iterations=5
        )
    
    def benchmark_aggregation_query(self) -> Dict:
        """Benchmark complex aggregation query."""
        
        query = f"""
        SELECT 
            district_id,
            metric_type,
            EXTRACT(YEAR FROM date_utc) as year,
            EXTRACT(MONTH FROM date_utc) as month,
            AVG(avg_value) as monthly_avg,
            MIN(min_value) as monthly_min,
            MAX(max_value) as monthly_max,
            AVG(data_completeness_pct) as avg_completeness,
            COUNT(CASE WHEN data_quality_flag = 'GOOD' THEN 1 END) / COUNT(*) as quality_ratio
        FROM `{self.project_id}.{self.dataset_id}.{self.view_name}`
        WHERE date_utc >= DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 2 YEAR)
            AND avg_value IS NOT NULL
        GROUP BY district_id, metric_type, EXTRACT(YEAR FROM date_utc), EXTRACT(MONTH FROM date_utc)
        ORDER BY district_id, metric_type, year, month
        """
        
        return self.run_query_benchmark(
            query=query,
            description="Monthly aggregation query",
            expected_time_ms=800,  # < 800ms
            iterations=3
        )
    
    def benchmark_concurrent_queries(self, num_concurrent: int = 5) -> Dict:
        """Benchmark concurrent query execution."""
        
        base_query = f"""
        SELECT 
            COUNT(*) as record_count,
            AVG(avg_value) as overall_avg
        FROM `{self.project_id}.{self.dataset_id}.{self.view_name}`
        WHERE date_utc BETWEEN DATE_SUB(CURRENT_DATE('UTC'), INTERVAL {{}} DAY)
            AND DATE_SUB(CURRENT_DATE('UTC'), INTERVAL {{}} DAY)
        """
        
        # Generate different queries with different date ranges
        queries = []
        for i in range(num_concurrent):
            start_days = 365 + (i * 30)
            end_days = 365 + ((i + 1) * 30)
            query = base_query.format(start_days, end_days)
            queries.append((f"Concurrent query {i+1}", query))
        
        logger.info(f"Running {num_concurrent} concurrent queries")
        
        start_time = time.perf_counter()
        execution_times = []
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            # Submit all queries
            future_to_query = {
                executor.submit(self._execute_single_query, query): desc 
                for desc, query in queries
            }
            
            # Collect results
            for future in as_completed(future_to_query):
                query_desc = future_to_query[future]
                try:
                    exec_time = future.result()
                    execution_times.append(exec_time)
                    logger.info(f"  {query_desc}: {exec_time:.2f}ms")
                except Exception as e:
                    logger.error(f"  {query_desc} failed: {str(e)}")
                    execution_times.append(float('inf'))
        
        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000
        
        return {
            'description': f'Concurrent execution ({num_concurrent} queries)',
            'num_concurrent_queries': num_concurrent,
            'total_execution_time_ms': total_time_ms,
            'avg_individual_time_ms': statistics.mean(execution_times),
            'max_individual_time_ms': max(execution_times),
            'min_individual_time_ms': min(execution_times),
            'all_queries_completed': all(t != float('inf') for t in execution_times),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _execute_single_query(self, query: str) -> float:
        """Execute a single query and return execution time in milliseconds."""
        
        job_config = QueryJobConfig()
        job_config.use_query_cache = False
        job_config.use_legacy_sql = False
        
        start_time = time.perf_counter()
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        end_time = time.perf_counter()
        
        return (end_time - start_time) * 1000
    
    def benchmark_query_plan_analysis(self) -> Dict:
        """Analyze query execution plan for optimization insights."""
        
        query = f"""
        SELECT 
            date_utc,
            district_id,
            metric_type,
            avg_value,
            count_readings
        FROM `{self.project_id}.{self.dataset_id}.{self.view_name}`
        WHERE date_utc BETWEEN '2024-01-01' AND '2024-03-31'
            AND district_id = 'DIST_001'
        """
        
        job_config = QueryJobConfig()
        job_config.dry_run = True
        job_config.use_legacy_sql = False
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            
            return {
                'description': 'Query plan analysis',
                'estimated_bytes_processed': query_job.total_bytes_processed,
                'estimated_bytes_billed': query_job.total_bytes_billed,
                'query_plan_available': hasattr(query_job, 'query_plan'),
                'cache_hit': query_job.cache_hit,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query plan analysis failed: {str(e)}")
            return {
                'description': 'Query plan analysis',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def run_all_benchmarks(self) -> Dict:
        """Run comprehensive benchmark suite."""
        
        logger.info("Starting comprehensive BigQuery view benchmark suite")
        
        benchmarks = {
            'full_dataset': self.benchmark_full_dataset_query(),
            'single_month': self.benchmark_single_month_query(),
            'filtered_query': self.benchmark_filtered_query(),
            'aggregation_query': self.benchmark_aggregation_query(),
            'concurrent_queries': self.benchmark_concurrent_queries(),
            'query_plan': self.benchmark_query_plan_analysis()
        }
        
        # Overall assessment
        performance_tests = ['full_dataset', 'single_month', 'filtered_query', 'aggregation_query']
        all_passed = all(
            benchmarks[test].get('performance_passed', False) 
            for test in performance_tests
        )
        
        benchmarks['summary'] = {
            'total_benchmarks': len(benchmarks) - 1,  # Exclude summary itself
            'performance_tests_passed': sum(
                1 for test in performance_tests 
                if benchmarks[test].get('performance_passed', False)
            ),
            'all_performance_tests_passed': all_passed,
            'concurrent_queries_successful': benchmarks['concurrent_queries']['all_queries_completed'],
            'benchmark_completion_time': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Benchmark suite completed. Overall pass: {all_passed}")
        
        return benchmarks
    
    def save_results_to_bigquery(self, results: Dict) -> None:
        """Save benchmark results to BigQuery for historical tracking."""
        
        # Flatten results for BigQuery storage
        flattened_results = []
        
        for benchmark_name, result in results.items():
            if benchmark_name == 'summary':
                continue
                
            flattened_result = {
                'benchmark_name': benchmark_name,
                'view_name': self.view_name,
                'project_id': self.project_id,
                'dataset_id': self.dataset_id,
                'execution_timestamp': result.get('timestamp', datetime.utcnow().isoformat()),
                **{k: v for k, v in result.items() if k != 'query'}  # Exclude query text for storage
            }
            flattened_results.append(flattened_result)
        
        # Insert into BigQuery table (create if not exists)
        table_id = f"{self.project_id}.{self.dataset_id}.view_performance_benchmarks"
        
        try:
            df = pd.DataFrame(flattened_results)
            df.to_gbq(
                destination_table=table_id,
                project_id=self.project_id,
                if_exists='append',
                table_schema=[
                    {'name': 'benchmark_name', 'type': 'STRING'},
                    {'name': 'view_name', 'type': 'STRING'},
                    {'name': 'project_id', 'type': 'STRING'},
                    {'name': 'dataset_id', 'type': 'STRING'},
                    {'name': 'execution_timestamp', 'type': 'TIMESTAMP'},
                    {'name': 'avg_execution_time_ms', 'type': 'FLOAT'},
                    {'name': 'performance_passed', 'type': 'BOOLEAN'},
                ]
            )
            logger.info(f"Benchmark results saved to {table_id}")
            
        except Exception as e:
            logger.error(f"Failed to save results to BigQuery: {str(e)}")


def main():
    """Main execution function."""
    
    # Initialize benchmark suite
    benchmark = BigQueryBenchmark()
    
    # Run all benchmarks
    results = benchmark.run_all_benchmarks()
    
    # Print summary
    print("\n" + "="*80)
    print("BIGQUERY VIEW PERFORMANCE BENCHMARK RESULTS")
    print("="*80)
    
    for name, result in results.items():
        if name == 'summary':
            continue
            
        print(f"\n{name.upper()}:")
        print(f"  Description: {result.get('description', 'N/A')}")
        
        if 'avg_execution_time_ms' in result:
            print(f"  Avg Execution Time: {result['avg_execution_time_ms']:.2f}ms")
            print(f"  Expected Time: {result.get('expected_time_ms', 'N/A')}ms")
            print(f"  Performance Passed: {result.get('performance_passed', 'N/A')}")
        
        if 'total_execution_time_ms' in result:
            print(f"  Total Execution Time: {result['total_execution_time_ms']:.2f}ms")
            print(f"  All Queries Completed: {result.get('all_queries_completed', 'N/A')}")
    
    # Print overall summary
    summary = results['summary']
    print(f"\nOVERALL SUMMARY:")
    print(f"  Performance Tests Passed: {summary['performance_tests_passed']}/{len(['full_dataset', 'single_month', 'filtered_query', 'aggregation_query'])}")
    print(f"  All Performance Tests Passed: {summary['all_performance_tests_passed']}")
    print(f"  Concurrent Queries Successful: {summary['concurrent_queries_successful']}")
    
    # Save results
    try:
        benchmark.save_results_to_bigquery(results)
    except Exception as e:
        logger.warning(f"Could not save to BigQuery: {e}")
    
    # Exit with appropriate code
    if summary['all_performance_tests_passed']:
        print("\n✅ All performance benchmarks PASSED")
        exit(0)
    else:
        print("\n❌ Some performance benchmarks FAILED")
        exit(1)


if __name__ == "__main__":
    main()
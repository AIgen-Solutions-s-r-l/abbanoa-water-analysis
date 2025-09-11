#!/usr/bin/env python3
"""Job management CLI for running and monitoring scheduled jobs"""

import asyncio
import argparse
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jobs.reconciliation_job import ReconciliationJob
from src.jobs.batch_prediction_job import BatchPredictionJob
from src.jobs.cleanup_job import CleanupJob
from src.jobs.job_monitor import JobMonitor
from src.jobs.health_check import HealthCheckJob
from src.jobs.base_job import BaseJob


class JobCLI:
    """Command-line interface for job management"""
    
    def __init__(self):
        self.available_jobs = {
            "reconciliation": ReconciliationJob,
            "batch_prediction": BatchPredictionJob,
            "cleanup": CleanupJob,
            "monitor": JobMonitor,
            "health_check": HealthCheckJob
        }
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description="Job Management CLI for Abbanoa Water Analysis",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run specific job
  python job_cli.py run reconciliation
  
  # Run health check
  python job_cli.py run health_check
  
  # List all available jobs
  python job_cli.py list
  
  # Check job status
  python job_cli.py status
  
  # Run all jobs in sequence
  python job_cli.py run-all
            """
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Run command
        run_parser = subparsers.add_parser("run", help="Run a specific job")
        run_parser.add_argument("job", choices=list(self.available_jobs.keys()), help="Job to run")
        run_parser.add_argument("--timeout", type=int, help="Override job timeout (minutes)")
        run_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        
        # List command
        subparsers.add_parser("list", help="List all available jobs")
        
        # Status command  
        status_parser = subparsers.add_parser("status", help="Check job execution status")
        status_parser.add_argument("--days", type=int, default=1, help="Days of history to show")
        status_parser.add_argument("--job", help="Show status for specific job only")
        
        # Run all command
        run_all_parser = subparsers.add_parser("run-all", help="Run all jobs in sequence")
        run_all_parser.add_argument("--stop-on-error", action="store_true", help="Stop if any job fails")
        
        # Test command
        test_parser = subparsers.add_parser("test", help="Test database connectivity")
        
        return parser
    
    async def run_job(self, job_name: str, timeout: int = None, verbose: bool = False) -> bool:
        """Run a specific job"""
        if job_name not in self.available_jobs:
            print(f"Error: Job '{job_name}' not found")
            return False
        
        job_class = self.available_jobs[job_name]
        job = job_class()
        
        # Override timeout if specified
        if timeout:
            job.timeout_minutes = timeout
        
        print(f"Starting job: {job_name}")
        if verbose:
            print(f"Timeout: {job.timeout_minutes} minutes")
        
        start_time = datetime.now()
        
        try:
            success = await job.run()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if success:
                print(f"✓ Job '{job_name}' completed successfully in {duration:.1f}s")
                
                if verbose and hasattr(job, 'get_status_summary'):
                    summary = job.get_status_summary()
                    print(f"Status: {json.dumps(summary, indent=2, default=str)}")
                    
                return True
            else:
                print(f"✗ Job '{job_name}' failed after {duration:.1f}s")
                if job.error_message:
                    print(f"Error: {job.error_message}")
                return False
                
        except Exception as e:
            print(f"✗ Job '{job_name}' crashed: {e}")
            return False
    
    def list_jobs(self):
        """List all available jobs"""
        print("Available jobs:")
        print("-" * 50)
        
        for job_name, job_class in self.available_jobs.items():
            job = job_class()
            print(f"{job_name:20} - {job.__class__.__doc__ or 'No description'}")
            print(f"{'':20}   Timeout: {job.timeout_minutes} minutes")
            print()
    
    async def show_status(self, days: int = 1, specific_job: str = None):
        """Show job execution status"""
        try:
            # Create a temporary job to access the database
            temp_job = BaseJob("status_check", timeout_minutes=5)
            pool = await temp_job.create_db_pool()
            
            query = """
                SELECT 
                    job_name,
                    status,
                    started_at,
                    completed_at,
                    duration_seconds,
                    error_message
                FROM water_infrastructure.job_executions 
                WHERE started_at > NOW() - INTERVAL %s
            """
            
            params = [f"{days} days"]
            
            if specific_job:
                query += " AND job_name = %s"
                params.append(specific_job)
            
            query += " ORDER BY started_at DESC LIMIT 50"
            
            async with pool.acquire() as conn:
                # Convert to asyncpg parameterized query
                asyncpg_query = query.replace('%s', '$1' if len(params) == 1 else '$1' if specific_job else '$1')
                if specific_job:
                    asyncpg_query = query.replace('%s', '$1').replace('%s', '$2')
                
                rows = await conn.fetch(asyncpg_query, *params)
                
                if not rows:
                    print("No job executions found")
                    return
                
                print(f"Job execution status (last {days} days):")
                print("-" * 80)
                print(f"{'Job':<20} {'Status':<10} {'Started':<20} {'Duration':<10} {'Error':<20}")
                print("-" * 80)
                
                for row in rows:
                    duration_str = f"{row['duration_seconds']}s" if row['duration_seconds'] else "N/A"
                    error_str = (row['error_message'][:17] + "...") if row['error_message'] else ""
                    
                    status_symbol = {
                        'success': '✓',
                        'failed': '✗', 
                        'timeout': '⏱',
                        'running': '●'
                    }.get(row['status'], '?')
                    
                    print(f"{row['job_name']:<20} {status_symbol} {row['status']:<8} {row['started_at'].strftime('%Y-%m-%d %H:%M'):<20} {duration_str:<10} {error_str:<20}")
            
            await pool.close()
            
        except Exception as e:
            print(f"Error retrieving status: {e}")
    
    async def run_all_jobs(self, stop_on_error: bool = False) -> bool:
        """Run all jobs in sequence"""
        # Define execution order (dependencies first)
        job_order = ["health_check", "reconciliation", "batch_prediction", "cleanup", "monitor"]
        
        results = {}
        overall_success = True
        
        print("Running all jobs in sequence...")
        print("=" * 50)
        
        for job_name in job_order:
            if job_name in self.available_jobs:
                success = await self.run_job(job_name, verbose=False)
                results[job_name] = success
                
                if not success:
                    overall_success = False
                    if stop_on_error:
                        print(f"Stopping execution due to failure in {job_name}")
                        break
            
            print()  # Add spacing between jobs
        
        # Summary
        print("=" * 50)
        print("Execution Summary:")
        
        for job_name, success in results.items():
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  {job_name:<20} {status}")
        
        success_count = sum(1 for s in results.values() if s)
        print(f"\nOverall: {success_count}/{len(results)} jobs successful")
        
        return overall_success
    
    async def test_connectivity(self):
        """Test database connectivity"""
        try:
            # Use health check job for connectivity test
            health_job = HealthCheckJob()
            pool = await health_job.create_db_pool()
            
            async with pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                
            await pool.close()
            
            print("✓ Database connectivity test passed")
            return True
            
        except Exception as e:
            print(f"✗ Database connectivity test failed: {e}")
            return False


async def main():
    """Main CLI entry point"""
    cli = JobCLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "run":
            success = await cli.run_job(args.job, args.timeout, args.verbose)
            sys.exit(0 if success else 1)
            
        elif args.command == "list":
            cli.list_jobs()
            
        elif args.command == "status":
            await cli.show_status(args.days, args.job)
            
        elif args.command == "run-all":
            success = await cli.run_all_jobs(args.stop_on_error)
            sys.exit(0 if success else 1)
            
        elif args.command == "test":
            success = await cli.test_connectivity()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
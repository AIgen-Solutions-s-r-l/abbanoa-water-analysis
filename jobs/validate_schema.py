#!/usr/bin/env python3
"""
Network Efficiency ETL - Schema and Data Validation

This script validates that the sensor_readings_hourly materialized view 
(node_flow_hourly equivalent) conforms to the expected schema and contains
valid data for network efficiency analysis.

Usage:
    python jobs/validate_schema.py [--verbose] [--fix-issues]
    
Examples:
    python jobs/validate_schema.py --verbose
    python jobs/validate_schema.py --fix-issues
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
import asyncpg
from dataclasses import dataclass
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database.postgres_manager import get_postgres_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    level: ValidationLevel
    message: str
    details: Optional[Dict[str, Any]] = None
    fix_suggestion: Optional[str] = None


class SchemaValidator:
    """Validates schema and data integrity for network efficiency tables."""
    
    def __init__(self, fix_issues: bool = False):
        """
        Initialize schema validator.
        
        Args:
            fix_issues: Whether to attempt to fix issues found during validation
        """
        self.fix_issues = fix_issues
        self.postgres_manager = None
        self.results: List[ValidationResult] = []
        
        # Expected schema for sensor_readings_hourly
        self.expected_schema = {
            'bucket': {'type': 'timestamp with time zone', 'nullable': False},
            'node_id': {'type': 'character varying(50)', 'nullable': False},
            'reading_count': {'type': 'bigint', 'nullable': True},
            'avg_temperature': {'type': 'numeric', 'nullable': True},
            'avg_flow_rate': {'type': 'numeric', 'nullable': True},
            'max_flow_rate': {'type': 'numeric', 'nullable': True},
            'min_flow_rate': {'type': 'numeric', 'nullable': True},
            'stddev_flow_rate': {'type': 'numeric', 'nullable': True},
            'avg_pressure': {'type': 'numeric', 'nullable': True},
            'max_pressure': {'type': 'numeric', 'nullable': True},
            'min_pressure': {'type': 'numeric', 'nullable': True},
            'stddev_pressure': {'type': 'numeric', 'nullable': True},
            'total_volume_m3': {'type': 'numeric', 'nullable': True},
            'avg_quality_score': {'type': 'numeric', 'nullable': True}
        }
        
    async def initialize(self) -> None:
        """Initialize database connections."""
        self.postgres_manager = await get_postgres_manager()
        logger.info("Schema Validator initialized")
        
    async def validate_all(self) -> List[ValidationResult]:
        """
        Run all validation checks.
        
        Returns:
            List of validation results
        """
        logger.info("Starting comprehensive schema and data validation")
        
        # Schema validation
        await self._validate_table_exists()
        await self._validate_schema_structure()
        await self._validate_indexes()
        await self._validate_materialized_view()
        
        # Data validation
        await self._validate_data_integrity()
        await self._validate_data_completeness()
        await self._validate_data_quality()
        await self._validate_performance()
        
        # Network efficiency specific validations
        await self._validate_network_efficiency_metrics()
        await self._validate_time_series_continuity()
        
        # Summary
        self._generate_validation_summary()
        
        return self.results
        
    async def _validate_table_exists(self) -> None:
        """Validate that the sensor_readings_hourly table exists."""
        logger.info("Validating table existence")
        
        async with self.postgres_manager.acquire() as conn:
            # Check if table exists
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'water_infrastructure' 
                    AND table_name = 'sensor_readings_hourly'
                )
            """)
            
            if exists:
                self.results.append(ValidationResult(
                    check_name="table_exists",
                    level=ValidationLevel.INFO,
                    message="Table sensor_readings_hourly exists",
                    details={"table_schema": "water_infrastructure", "table_name": "sensor_readings_hourly"}
                ))
            else:
                self.results.append(ValidationResult(
                    check_name="table_exists",
                    level=ValidationLevel.CRITICAL,
                    message="Table sensor_readings_hourly does not exist",
                    fix_suggestion="Run the database schema initialization script"
                ))
                
    async def _validate_schema_structure(self) -> None:
        """Validate the schema structure matches expectations."""
        logger.info("Validating schema structure")
        
        async with self.postgres_manager.acquire() as conn:
            # Get actual schema
            actual_schema = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'water_infrastructure'
                AND table_name = 'sensor_readings_hourly'
                ORDER BY ordinal_position
            """)
            
            actual_columns = {
                row['column_name']: {
                    'type': row['data_type'],
                    'nullable': row['is_nullable'] == 'YES'
                }
                for row in actual_schema
            }
            
            # Check for missing columns
            for expected_col, expected_props in self.expected_schema.items():
                if expected_col not in actual_columns:
                    self.results.append(ValidationResult(
                        check_name="schema_structure",
                        level=ValidationLevel.ERROR,
                        message=f"Missing column: {expected_col}",
                        details={"expected_column": expected_col, "expected_properties": expected_props}
                    ))
                else:
                    # Check column properties
                    actual_props = actual_columns[expected_col]
                    if actual_props['nullable'] != expected_props['nullable']:
                        self.results.append(ValidationResult(
                            check_name="schema_structure",
                            level=ValidationLevel.WARNING,
                            message=f"Column {expected_col} nullability mismatch",
                            details={
                                "column": expected_col,
                                "expected_nullable": expected_props['nullable'],
                                "actual_nullable": actual_props['nullable']
                            }
                        ))
                        
            # Check for extra columns
            for actual_col in actual_columns:
                if actual_col not in self.expected_schema:
                    self.results.append(ValidationResult(
                        check_name="schema_structure",
                        level=ValidationLevel.INFO,
                        message=f"Extra column found: {actual_col}",
                        details={"extra_column": actual_col}
                    ))
                    
            if len([r for r in self.results if r.check_name == "schema_structure" and r.level == ValidationLevel.ERROR]) == 0:
                self.results.append(ValidationResult(
                    check_name="schema_structure",
                    level=ValidationLevel.INFO,
                    message="Schema structure validation passed",
                    details={"columns_validated": len(self.expected_schema)}
                ))
                
    async def _validate_indexes(self) -> None:
        """Validate that required indexes exist."""
        logger.info("Validating indexes")
        
        async with self.postgres_manager.acquire() as conn:
            # Get indexes
            indexes = await conn.fetch("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'water_infrastructure'
                AND tablename = 'sensor_readings_hourly'
            """)
            
            index_names = [idx['indexname'] for idx in indexes]
            
            # Check for materialized view indexes
            required_indexes = [
                'sensor_readings_hourly_bucket_idx',
                'sensor_readings_hourly_node_id_idx'
            ]
            
            for required_idx in required_indexes:
                if not any(required_idx in idx_name for idx_name in index_names):
                    self.results.append(ValidationResult(
                        check_name="indexes",
                        level=ValidationLevel.WARNING,
                        message=f"Missing or non-standard index: {required_idx}",
                        details={"missing_index": required_idx}
                    ))
                    
            self.results.append(ValidationResult(
                check_name="indexes",
                level=ValidationLevel.INFO,
                message=f"Found {len(indexes)} indexes",
                details={"indexes": index_names}
            ))
            
    async def _validate_materialized_view(self) -> None:
        """Validate materialized view configuration."""
        logger.info("Validating materialized view configuration")
        
        async with self.postgres_manager.acquire() as conn:
            # Check if it's a materialized view
            is_materialized = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_matviews
                    WHERE schemaname = 'water_infrastructure'
                    AND matviewname = 'sensor_readings_hourly'
                )
            """)
            
            if is_materialized:
                self.results.append(ValidationResult(
                    check_name="materialized_view",
                    level=ValidationLevel.INFO,
                    message="Table is properly configured as a materialized view"
                ))
                
                # Check continuous aggregate policy
                try:
                    policy_info = await conn.fetchval("""
                        SELECT application_name 
                        FROM timescaledb_information.jobs 
                        WHERE application_name LIKE '%sensor_readings_hourly%'
                    """)
                    
                    if policy_info:
                        self.results.append(ValidationResult(
                            check_name="materialized_view",
                            level=ValidationLevel.INFO,
                            message="Continuous aggregate policy is active",
                            details={"policy": policy_info}
                        ))
                    else:
                        self.results.append(ValidationResult(
                            check_name="materialized_view",
                            level=ValidationLevel.WARNING,
                            message="No continuous aggregate policy found",
                            fix_suggestion="Add continuous aggregate policy for automatic refresh"
                        ))
                        
                except Exception as e:
                    self.results.append(ValidationResult(
                        check_name="materialized_view",
                        level=ValidationLevel.WARNING,
                        message="Could not check continuous aggregate policy",
                        details={"error": str(e)}
                    ))
                    
            else:
                self.results.append(ValidationResult(
                    check_name="materialized_view",
                    level=ValidationLevel.ERROR,
                    message="Table is not configured as a materialized view",
                    fix_suggestion="Convert to TimescaleDB continuous aggregate"
                ))
                
    async def _validate_data_integrity(self) -> None:
        """Validate data integrity constraints."""
        logger.info("Validating data integrity")
        
        async with self.postgres_manager.acquire() as conn:
            # Check for null values in non-nullable columns
            null_buckets = await conn.fetchval("""
                SELECT COUNT(*) FROM water_infrastructure.sensor_readings_hourly
                WHERE bucket IS NULL
            """)
            
            if null_buckets > 0:
                self.results.append(ValidationResult(
                    check_name="data_integrity",
                    level=ValidationLevel.ERROR,
                    message=f"Found {null_buckets} records with null bucket values",
                    details={"null_buckets": null_buckets}
                ))
                
            # Check for negative values where they shouldn't exist
            negative_values = await conn.fetchval("""
                SELECT COUNT(*) FROM water_infrastructure.sensor_readings_hourly
                WHERE avg_flow_rate < 0 OR max_flow_rate < 0 OR min_flow_rate < 0
                OR avg_pressure < 0 OR max_pressure < 0 OR min_pressure < 0
                OR total_volume_m3 < 0
            """)
            
            if negative_values > 0:
                self.results.append(ValidationResult(
                    check_name="data_integrity",
                    level=ValidationLevel.ERROR,
                    message=f"Found {negative_values} records with negative values",
                    details={"negative_values": negative_values}
                ))
                
            # Check for logical inconsistencies
            inconsistent_values = await conn.fetchval("""
                SELECT COUNT(*) FROM water_infrastructure.sensor_readings_hourly
                WHERE (min_flow_rate > max_flow_rate)
                OR (min_pressure > max_pressure)
                OR (avg_flow_rate > max_flow_rate)
                OR (avg_flow_rate < min_flow_rate)
                OR (avg_pressure > max_pressure)
                OR (avg_pressure < min_pressure)
            """)
            
            if inconsistent_values > 0:
                self.results.append(ValidationResult(
                    check_name="data_integrity",
                    level=ValidationLevel.ERROR,
                    message=f"Found {inconsistent_values} records with logical inconsistencies",
                    details={"inconsistent_values": inconsistent_values}
                ))
                
            if null_buckets == 0 and negative_values == 0 and inconsistent_values == 0:
                self.results.append(ValidationResult(
                    check_name="data_integrity",
                    level=ValidationLevel.INFO,
                    message="Data integrity validation passed"
                ))
                
    async def _validate_data_completeness(self) -> None:
        """Validate data completeness."""
        logger.info("Validating data completeness")
        
        async with self.postgres_manager.acquire() as conn:
            # Check total record count
            total_records = await conn.fetchval("""
                SELECT COUNT(*) FROM water_infrastructure.sensor_readings_hourly
            """)
            
            # Check date range
            date_range = await conn.fetchrow("""
                SELECT MIN(bucket) as min_date, MAX(bucket) as max_date
                FROM water_infrastructure.sensor_readings_hourly
            """)
            
            # Check node coverage
            node_count = await conn.fetchval("""
                SELECT COUNT(DISTINCT node_id) 
                FROM water_infrastructure.sensor_readings_hourly
            """)
            
            # Check recent data availability
            recent_data = await conn.fetchval("""
                SELECT COUNT(*) FROM water_infrastructure.sensor_readings_hourly
                WHERE bucket > NOW() - INTERVAL '24 hours'
            """)
            
            self.results.append(ValidationResult(
                check_name="data_completeness",
                level=ValidationLevel.INFO,
                message=f"Data completeness check",
                details={
                    "total_records": total_records,
                    "date_range": {
                        "min_date": date_range['min_date'].isoformat() if date_range['min_date'] else None,
                        "max_date": date_range['max_date'].isoformat() if date_range['max_date'] else None
                    },
                    "unique_nodes": node_count,
                    "recent_records_24h": recent_data
                }
            ))
            
            if total_records == 0:
                self.results.append(ValidationResult(
                    check_name="data_completeness",
                    level=ValidationLevel.CRITICAL,
                    message="No data found in sensor_readings_hourly table",
                    fix_suggestion="Run the ETL pipeline to populate the table"
                ))
                
            if recent_data == 0:
                self.results.append(ValidationResult(
                    check_name="data_completeness",
                    level=ValidationLevel.WARNING,
                    message="No recent data (last 24 hours) found",
                    fix_suggestion="Check if ETL pipeline is running regularly"
                ))
                
    async def _validate_data_quality(self) -> None:
        """Validate data quality metrics."""
        logger.info("Validating data quality")
        
        async with self.postgres_manager.acquire() as conn:
            # Check quality score distribution
            quality_stats = await conn.fetchrow("""
                SELECT 
                    AVG(avg_quality_score) as avg_quality,
                    MIN(avg_quality_score) as min_quality,
                    MAX(avg_quality_score) as max_quality,
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN avg_quality_score < 0.5 THEN 1 END) as low_quality_records
                FROM water_infrastructure.sensor_readings_hourly
                WHERE avg_quality_score IS NOT NULL
            """)
            
            if quality_stats:
                self.results.append(ValidationResult(
                    check_name="data_quality",
                    level=ValidationLevel.INFO,
                    message="Data quality statistics",
                    details={
                        "avg_quality_score": float(quality_stats['avg_quality']) if quality_stats['avg_quality'] else None,
                        "min_quality_score": float(quality_stats['min_quality']) if quality_stats['min_quality'] else None,
                        "max_quality_score": float(quality_stats['max_quality']) if quality_stats['max_quality'] else None,
                        "total_records": quality_stats['total_records'],
                        "low_quality_records": quality_stats['low_quality_records']
                    }
                ))
                
                if quality_stats['low_quality_records'] > 0:
                    percentage = (quality_stats['low_quality_records'] / quality_stats['total_records']) * 100
                    self.results.append(ValidationResult(
                        check_name="data_quality",
                        level=ValidationLevel.WARNING,
                        message=f"{percentage:.1f}% of records have low quality scores (<0.5)",
                        details={"low_quality_percentage": percentage}
                    ))
                    
    async def _validate_performance(self) -> None:
        """Validate query performance."""
        logger.info("Validating query performance")
        
        async with self.postgres_manager.acquire() as conn:
            # Test query performance
            start_time = datetime.now()
            
            result = await conn.fetchrow("""
                SELECT COUNT(*) as count, AVG(avg_flow_rate) as avg_flow
                FROM water_infrastructure.sensor_readings_hourly
                WHERE bucket > NOW() - INTERVAL '7 days'
            """)
            
            query_time = (datetime.now() - start_time).total_seconds()
            
            self.results.append(ValidationResult(
                check_name="performance",
                level=ValidationLevel.INFO,
                message=f"Query performance test completed in {query_time:.2f}s",
                details={
                    "query_time_seconds": query_time,
                    "records_queried": result['count'],
                    "avg_flow_rate": float(result['avg_flow']) if result['avg_flow'] else None
                }
            ))
            
            if query_time > 5.0:
                self.results.append(ValidationResult(
                    check_name="performance",
                    level=ValidationLevel.WARNING,
                    message="Query performance is slow",
                    details={"query_time_seconds": query_time},
                    fix_suggestion="Consider adding indexes or optimizing the materialized view"
                ))
                
    async def _validate_network_efficiency_metrics(self) -> None:
        """Validate network efficiency specific metrics."""
        logger.info("Validating network efficiency metrics")
        
        async with self.postgres_manager.acquire() as conn:
            # Check for nodes with consistent data
            node_stats = await conn.fetch("""
                SELECT 
                    node_id,
                    COUNT(*) as record_count,
                    AVG(avg_flow_rate) as avg_flow,
                    AVG(avg_pressure) as avg_pressure,
                    MIN(bucket) as first_reading,
                    MAX(bucket) as last_reading
                FROM water_infrastructure.sensor_readings_hourly
                GROUP BY node_id
                ORDER BY record_count DESC
            """)
            
            active_nodes = len([n for n in node_stats if n['record_count'] > 24])  # More than 24 hours of data
            
            self.results.append(ValidationResult(
                check_name="network_efficiency",
                level=ValidationLevel.INFO,
                message=f"Network efficiency metrics validation",
                details={
                    "total_nodes": len(node_stats),
                    "active_nodes": active_nodes,
                    "nodes_with_data": [
                        {
                            "node_id": n['node_id'],
                            "record_count": n['record_count'],
                            "avg_flow": float(n['avg_flow']) if n['avg_flow'] else None,
                            "avg_pressure": float(n['avg_pressure']) if n['avg_pressure'] else None,
                            "data_span_hours": (n['last_reading'] - n['first_reading']).total_seconds() / 3600
                        }
                        for n in node_stats[:10]  # Top 10 nodes
                    ]
                }
            ))
            
            if active_nodes == 0:
                self.results.append(ValidationResult(
                    check_name="network_efficiency",
                    level=ValidationLevel.WARNING,
                    message="No nodes have sufficient data for network efficiency analysis",
                    fix_suggestion="Ensure ETL pipeline is collecting data from sensor nodes"
                ))
                
    async def _validate_time_series_continuity(self) -> None:
        """Validate time series data continuity."""
        logger.info("Validating time series continuity")
        
        async with self.postgres_manager.acquire() as conn:
            # Check for gaps in time series
            gaps = await conn.fetch("""
                WITH hourly_series AS (
                    SELECT 
                        node_id,
                        bucket,
                        LAG(bucket) OVER (PARTITION BY node_id ORDER BY bucket) as prev_bucket
                    FROM water_infrastructure.sensor_readings_hourly
                )
                SELECT 
                    node_id,
                    COUNT(*) as gap_count,
                    AVG(EXTRACT(EPOCH FROM (bucket - prev_bucket))/3600) as avg_gap_hours
                FROM hourly_series
                WHERE prev_bucket IS NOT NULL
                AND bucket - prev_bucket > INTERVAL '2 hours'
                GROUP BY node_id
                ORDER BY gap_count DESC
            """)
            
            if gaps:
                self.results.append(ValidationResult(
                    check_name="time_series_continuity",
                    level=ValidationLevel.WARNING,
                    message=f"Found time series gaps in {len(gaps)} nodes",
                    details={
                        "nodes_with_gaps": len(gaps),
                        "gap_details": [
                            {
                                "node_id": g['node_id'],
                                "gap_count": g['gap_count'],
                                "avg_gap_hours": float(g['avg_gap_hours'])
                            }
                            for g in gaps[:5]  # Top 5 nodes with gaps
                        ]
                    }
                ))
            else:
                self.results.append(ValidationResult(
                    check_name="time_series_continuity",
                    level=ValidationLevel.INFO,
                    message="No significant time series gaps found"
                ))
                
    def _generate_validation_summary(self) -> None:
        """Generate a summary of validation results."""
        logger.info("Generating validation summary")
        
        summary = {
            "total_checks": len(self.results),
            "info": len([r for r in self.results if r.level == ValidationLevel.INFO]),
            "warnings": len([r for r in self.results if r.level == ValidationLevel.WARNING]),
            "errors": len([r for r in self.results if r.level == ValidationLevel.ERROR]),
            "critical": len([r for r in self.results if r.level == ValidationLevel.CRITICAL])
        }
        
        overall_status = "PASSED"
        if summary["critical"] > 0:
            overall_status = "FAILED"
        elif summary["errors"] > 0:
            overall_status = "FAILED"
        elif summary["warnings"] > 0:
            overall_status = "PASSED_WITH_WARNINGS"
            
        self.results.append(ValidationResult(
            check_name="validation_summary",
            level=ValidationLevel.INFO,
            message=f"Validation {overall_status}",
            details=summary
        ))
        
        # Log summary
        logger.info(f"Validation Summary: {summary}")
        logger.info(f"Overall Status: {overall_status}")
        
    def print_results(self, verbose: bool = False) -> None:
        """Print validation results to console."""
        print("\n" + "="*80)
        print("NETWORK EFFICIENCY SCHEMA VALIDATION RESULTS")
        print("="*80)
        
        for result in self.results:
            if result.check_name == "validation_summary":
                continue
                
            icon = {
                ValidationLevel.INFO: "ℹ️",
                ValidationLevel.WARNING: "⚠️",
                ValidationLevel.ERROR: "❌",
                ValidationLevel.CRITICAL: "🔴"
            }[result.level]
            
            print(f"\n{icon} [{result.level.value.upper()}] {result.check_name}")
            print(f"   {result.message}")
            
            if verbose and result.details:
                print(f"   Details: {result.details}")
                
            if result.fix_suggestion:
                print(f"   💡 Fix: {result.fix_suggestion}")
                
        # Print summary
        summary_result = next(r for r in self.results if r.check_name == "validation_summary")
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Status: {summary_result.message}")
        print(f"Total Checks: {summary_result.details['total_checks']}")
        print(f"Info: {summary_result.details['info']}")
        print(f"Warnings: {summary_result.details['warnings']}")
        print(f"Errors: {summary_result.details['errors']}")
        print(f"Critical: {summary_result.details['critical']}")
        print("="*80)


async def main():
    """Main validation execution function."""
    parser = argparse.ArgumentParser(description='Network Efficiency Schema Validation')
    parser.add_argument('--verbose', action='store_true', help='Show detailed validation results')
    parser.add_argument('--fix-issues', action='store_true', help='Attempt to fix issues found')
    
    args = parser.parse_args()
    
    validator = SchemaValidator(fix_issues=args.fix_issues)
    
    try:
        await validator.initialize()
        
        results = await validator.validate_all()
        
        validator.print_results(verbose=args.verbose)
        
        # Exit with error code if critical issues found
        critical_issues = len([r for r in results if r.level == ValidationLevel.CRITICAL])
        error_issues = len([r for r in results if r.level == ValidationLevel.ERROR])
        
        if critical_issues > 0 or error_issues > 0:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 
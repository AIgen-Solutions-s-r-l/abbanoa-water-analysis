#!/usr/bin/env python3
"""
Comprehensive test runner for the water infrastructure API testing suite.

Provides multiple test execution modes for different scenarios:
- Unit tests: Fast, isolated component tests
- Integration tests: API endpoint testing
- Performance tests: Load and stress testing
- E2E tests: Complete workflow testing
- Full suite: All tests with comprehensive reporting

Usage:
    python run_tests.py --mode unit
    python run_tests.py --mode integration
    python run_tests.py --mode performance
    python run_tests.py --mode e2e
    python run_tests.py --mode full
    python run_tests.py --mode smoke
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """Comprehensive test runner for the API testing suite."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.test_dir / "reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)

    def run_unit_tests(self) -> int:
        """Run unit tests for all services."""
        print("🧪 Running Unit Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-m", "unit",
            "--cov=src/api/services",
            "--cov-report=html:htmlcov/unit",
            "--cov-report=term-missing",
            "--junitxml=tests/reports/unit-results.xml",
            "--html=tests/reports/unit-report.html",
            "--self-contained-html",
            "-v"
        ]
        
        return self._execute_command(cmd)

    def run_integration_tests(self) -> int:
        """Run integration tests for API endpoints."""
        print("🔗 Running Integration Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-m", "integration",
            "--junitxml=tests/reports/integration-results.xml",
            "--html=tests/reports/integration-report.html",
            "--self-contained-html",
            "-v"
        ]
        
        return self._execute_command(cmd)

    def run_performance_tests(self) -> int:
        """Run performance and load tests."""
        print("⚡ Running Performance Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/performance/",
            "-m", "performance",
            "--junitxml=tests/reports/performance-results.xml",
            "--html=tests/reports/performance-report.html",
            "--self-contained-html",
            "-v",
            "--tb=short"
        ]
        
        return self._execute_command(cmd)

    def run_e2e_tests(self) -> int:
        """Run end-to-end workflow tests."""
        print("🚀 Running End-to-End Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/e2e/",
            "-m", "e2e",
            "--junitxml=tests/reports/e2e-results.xml",
            "--html=tests/reports/e2e-report.html",
            "--self-contained-html",
            "-v"
        ]
        
        return self._execute_command(cmd)

    def run_smoke_tests(self) -> int:
        """Run quick smoke tests to verify basic functionality."""
        print("💨 Running Smoke Tests...")
        print("=" * 50)
        
        # Define smoke test cases (subset of unit and integration tests)
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/test_consumption_service.py::TestConsumptionService::test_get_consumption_data_success",
            "tests/unit/test_water_quality_service.py::TestWaterQualityService::test_get_quality_readings_success",
            "tests/unit/test_forecasting_service.py::TestForecastingService::test_generate_consumption_forecast_success",
            "tests/unit/test_reports_service.py::TestReportsService::test_generate_consumption_report_success",
            "tests/unit/test_kpis_service.py::TestKPIOrchestrator::test_generate_kpi_dashboard_success",
            "tests/unit/test_filters_service.py::TestAdvancedFilteringService::test_apply_filters_success",
            "--junitxml=tests/reports/smoke-results.xml",
            "--html=tests/reports/smoke-report.html",
            "--self-contained-html",
            "-v"
        ]
        
        return self._execute_command(cmd)

    def run_full_suite(self) -> int:
        """Run complete test suite with comprehensive reporting."""
        print("🎯 Running Full Test Suite...")
        print("=" * 60)
        
        start_time = time.time()
        results = {}
        
        # Run all test types
        print("\n1/4 - Unit Tests")
        results['unit'] = self.run_unit_tests()
        
        print("\n2/4 - Integration Tests")
        results['integration'] = self.run_integration_tests()
        
        print("\n3/4 - Performance Tests")
        results['performance'] = self.run_performance_tests()
        
        print("\n4/4 - End-to-End Tests")
        results['e2e'] = self.run_e2e_tests()
        
        # Generate summary report
        end_time = time.time()
        duration = end_time - start_time
        
        self._generate_summary_report(results, duration)
        
        # Return overall status
        return max(results.values())

    def run_by_service(self, service: str) -> int:
        """Run tests for a specific service."""
        print(f"🔍 Running Tests for {service.title()} Service...")
        print("=" * 50)
        
        valid_services = ["consumption", "quality", "forecasting", "reports", "kpis", "filtering"]
        if service not in valid_services:
            print(f"❌ Invalid service '{service}'. Valid options: {', '.join(valid_services)}")
            return 1
        
        cmd = [
            "python", "-m", "pytest",
            f"tests/",
            "-m", service,
            f"--junitxml=tests/reports/{service}-results.xml",
            f"--html=tests/reports/{service}-report.html",
            "--self-contained-html",
            "-v"
        ]
        
        return self._execute_command(cmd)

    def run_parallel_tests(self) -> int:
        """Run tests in parallel for faster execution."""
        print("⚙️ Running Tests in Parallel...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "tests/integration/",
            "-n", "auto",  # Automatic CPU detection
            "--cov=src",
            "--cov-report=html:htmlcov/parallel",
            "--cov-report=term-missing",
            "--junitxml=tests/reports/parallel-results.xml",
            "--html=tests/reports/parallel-report.html",
            "--self-contained-html",
            "-v"
        ]
        
        return self._execute_command(cmd)

    def run_coverage_report(self) -> int:
        """Generate detailed coverage report."""
        print("📊 Generating Coverage Report...")
        print("=" * 50)
        
        # Run tests with coverage
        cmd_test = [
            "python", "-m", "pytest",
            "tests/unit/",
            "tests/integration/",
            "--cov=src",
            "--cov-report=html:htmlcov/detailed",
            "--cov-report=term-missing",
            "--cov-report=xml:tests/reports/coverage.xml",
            "--cov-fail-under=80",
            "-q"
        ]
        
        result = self._execute_command(cmd_test)
        
        if result == 0:
            print("\n✅ Coverage report generated successfully!")
            print(f"📁 HTML report: {self.project_root}/htmlcov/detailed/index.html")
            print(f"📄 XML report: {self.reports_dir}/coverage.xml")
        
        return result

    def _execute_command(self, cmd: List[str]) -> int:
        """Execute a command and return the exit code."""
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=False)
            return result.returncode
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return 1

    def _generate_summary_report(self, results: Dict[str, int], duration: float) -> None:
        """Generate a summary report of all test results."""
        print("\n" + "=" * 60)
        print("📋 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        total_tests = sum(1 for _ in results.keys())
        passed_tests = sum(1 for result in results.values() if result == 0)
        failed_tests = total_tests - passed_tests
        
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {failed_tests}/{total_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_type, result in results.items():
            status = "✅ PASS" if result == 0 else "❌ FAIL"
            print(f"  {test_type.title()}: {status}")
        
        print(f"\n📁 Reports available in: {self.reports_dir}")
        print(f"📊 Coverage report: {self.project_root}/htmlcov/")
        
        if failed_tests == 0:
            print("\n🎉 All tests passed successfully!")
        else:
            print(f"\n⚠️  {failed_tests} test suite(s) failed. Check reports for details.")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for water infrastructure API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --mode unit           # Run unit tests only
  python run_tests.py --mode integration    # Run integration tests
  python run_tests.py --mode performance    # Run performance tests
  python run_tests.py --mode e2e            # Run end-to-end tests
  python run_tests.py --mode full           # Run complete test suite
  python run_tests.py --mode smoke          # Run smoke tests
  python run_tests.py --service consumption # Run consumption service tests
  python run_tests.py --parallel            # Run tests in parallel
  python run_tests.py --coverage            # Generate coverage report
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--mode",
        choices=["unit", "integration", "performance", "e2e", "full", "smoke"],
        help="Test execution mode"
    )
    group.add_argument(
        "--service",
        choices=["consumption", "quality", "forecasting", "reports", "kpis", "filtering"],
        help="Run tests for specific service"
    )
    group.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    group.add_argument(
        "--coverage",
        action="store_true",
        help="Generate detailed coverage report"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    print("🧪 Water Infrastructure API Test Suite")
    print("=" * 60)
    print(f"Project Root: {runner.project_root}")
    print(f"Test Directory: {runner.test_dir}")
    print(f"Reports Directory: {runner.reports_dir}")
    print("=" * 60)
    
    # Execute based on arguments
    if args.mode:
        if args.mode == "unit":
            exit_code = runner.run_unit_tests()
        elif args.mode == "integration":
            exit_code = runner.run_integration_tests()
        elif args.mode == "performance":
            exit_code = runner.run_performance_tests()
        elif args.mode == "e2e":
            exit_code = runner.run_e2e_tests()
        elif args.mode == "full":
            exit_code = runner.run_full_suite()
        elif args.mode == "smoke":
            exit_code = runner.run_smoke_tests()
    elif args.service:
        exit_code = runner.run_by_service(args.service)
    elif args.parallel:
        exit_code = runner.run_parallel_tests()
    elif args.coverage:
        exit_code = runner.run_coverage_report()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 
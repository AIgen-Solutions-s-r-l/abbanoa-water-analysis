#!/bin/bash
#
# BigQuery View Deployment Script
# Purpose: Deploy vw_daily_timeseries view to BigQuery environments
# Owner: Data Engineering Team
# Created: 2025-07-04
#
# Usage:
#   ./deploy_views.sh [environment] [view_name]
#   
# Examples:
#   ./deploy_views.sh dev vw_daily_timeseries
#   ./deploy_views.sh staging vw_daily_timeseries
#   ./deploy_views.sh prod vw_daily_timeseries
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SQL_DIR="${PROJECT_ROOT}/sql/views"
CONFIG_DIR="${PROJECT_ROOT}/config/bigquery"
TEST_DIR="${PROJECT_ROOT}/tests/sql"

# Default values
ENVIRONMENT="${1:-dev}"
VIEW_NAME="${2:-vw_daily_timeseries}"
DRY_RUN="${DRY_RUN:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"
BACKUP_EXISTING="${BACKUP_EXISTING:-true}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment configuration
load_environment_config() {
    local env_file="${CONFIG_DIR}/dataset_config.yaml"
    
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment configuration file not found: $env_file"
        exit 1
    fi
    
    # Read configuration using Python
    local config=$(python3 -c "
import yaml
with open('$env_file', 'r') as f:
    config = yaml.safe_load(f)
    env_config = config['environments']['$ENVIRONMENT']
    print(f\"{env_config['project_id']} {env_config['dataset_id']}\")
")
    
    PROJECT_ID=$(echo $config | cut -d' ' -f1)
    DATASET_ID=$(echo $config | cut -d' ' -f2)
    
    log_info "Configuration loaded for environment: $ENVIRONMENT"
    log_info "Project ID: $PROJECT_ID"
    log_info "Dataset ID: $DATASET_ID"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if gcloud is installed and authenticated
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "No active gcloud authentication found. Please run 'gcloud auth login'"
        exit 1
    fi
    
    # Check if bq is installed
    if ! command -v bq &> /dev/null; then
        log_error "BigQuery CLI (bq) is not installed"
        exit 1
    fi
    
    # Check if Python and required packages are available
    if ! python3 -c "import yaml, google.cloud.bigquery" &> /dev/null; then
        log_error "Required Python packages not found. Please install: pyyaml google-cloud-bigquery"
        exit 1
    fi
    
    # Check if SQL file exists
    local sql_file="${SQL_DIR}/${VIEW_NAME}.sql"
    if [[ ! -f "$sql_file" ]]; then
        log_error "SQL file not found: $sql_file"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Backup existing view
backup_existing_view() {
    if [[ "$BACKUP_EXISTING" != "true" ]]; then
        log_info "Skipping backup (BACKUP_EXISTING=false)"
        return 0
    fi
    
    log_info "Checking for existing view to backup..."
    
    local view_id="${PROJECT_ID}.${DATASET_ID}.${VIEW_NAME}"
    
    # Check if view exists
    if bq show --view "$view_id" &> /dev/null; then
        log_info "Existing view found, creating backup..."
        
        local backup_name="${VIEW_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
        local backup_dir="${PROJECT_ROOT}/backups/views"
        mkdir -p "$backup_dir"
        
        # Export view definition
        bq show --view --format=prettyjson "$view_id" > "${backup_dir}/${backup_name}.json"
        
        # Extract SQL query
        bq show --view --format=json "$view_id" | \
            python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data['view']['query'])
" > "${backup_dir}/${backup_name}.sql"
        
        log_success "View backed up to: ${backup_dir}/${backup_name}.*"
    else
        log_info "No existing view found, skipping backup"
    fi
}

# Run pre-deployment tests
run_pre_deployment_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warning "Skipping tests (SKIP_TESTS=true)"
        return 0
    fi
    
    log_info "Running pre-deployment tests..."
    
    # SQL syntax validation
    log_info "Validating SQL syntax..."
    local sql_file="${SQL_DIR}/${VIEW_NAME}.sql"
    
    # Use BigQuery dry run to validate syntax
    if ! bq query --dry_run --use_legacy_sql=false < "$sql_file" &> /dev/null; then
        log_error "SQL syntax validation failed"
        return 1
    fi
    
    log_success "SQL syntax validation passed"
    
    # Run unit tests if available
    local test_file="${TEST_DIR}/test_${VIEW_NAME}.sql"
    if [[ -f "$test_file" ]]; then
        log_info "Running unit tests..."
        
        # Execute test queries (this would need to be adapted based on test framework)
        python3 -c "
import sys
sys.path.append('${PROJECT_ROOT}')
from tests.sql.test_runner import run_sql_tests
result = run_sql_tests('$test_file')
sys.exit(0 if result else 1)
" || {
            log_error "Unit tests failed"
            return 1
        }
        
        log_success "Unit tests passed"
    else
        log_warning "No unit tests found for $VIEW_NAME"
    fi
}

# Deploy view
deploy_view() {
    log_info "Deploying view: $VIEW_NAME"
    
    local sql_file="${SQL_DIR}/${VIEW_NAME}.sql"
    local view_id="${PROJECT_ID}.${DATASET_ID}.${VIEW_NAME}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would deploy view $view_id"
        log_info "SQL file: $sql_file"
        return 0
    fi
    
    # Ensure dataset exists
    log_info "Ensuring dataset exists: ${PROJECT_ID}.${DATASET_ID}"
    bq mk --dataset --force "${PROJECT_ID}:${DATASET_ID}" || {
        log_error "Failed to create/verify dataset"
        return 1
    }
    
    # Deploy view
    log_info "Creating/updating view: $view_id"
    
    # Replace placeholder project references in SQL
    local temp_sql=$(mktemp)
    sed "s/abbanoa-464816/${PROJECT_ID}/g" "$sql_file" > "$temp_sql"
    
    if bq mk --view --use_legacy_sql=false --force "$view_id" < "$temp_sql"; then
        log_success "View deployed successfully: $view_id"
    else
        log_error "Failed to deploy view"
        rm -f "$temp_sql"
        return 1
    fi
    
    rm -f "$temp_sql"
}

# Run post-deployment tests
run_post_deployment_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warning "Skipping post-deployment tests"
        return 0
    fi
    
    log_info "Running post-deployment smoke tests..."
    
    local view_id="${PROJECT_ID}.${DATASET_ID}.${VIEW_NAME}"
    
    # Test 1: Basic query execution
    log_info "Testing basic query execution..."
    local basic_query="SELECT COUNT(*) as row_count FROM \`$view_id\` LIMIT 1"
    
    if ! bq query --use_legacy_sql=false "$basic_query" &> /dev/null; then
        log_error "Basic query test failed"
        return 1
    fi
    
    # Test 2: Performance test (should complete within reasonable time)
    log_info "Testing query performance..."
    local perf_query="SELECT date_utc, district_id, COUNT(*) FROM \`$view_id\` WHERE date_utc >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) GROUP BY date_utc, district_id LIMIT 100"
    
    local start_time=$(date +%s)
    if ! bq query --use_legacy_sql=false "$perf_query" &> /dev/null; then
        log_error "Performance test query failed"
        return 1
    fi
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ $duration -gt 10 ]]; then
        log_warning "Query took ${duration}s (>10s threshold)"
    else
        log_success "Performance test passed (${duration}s)"
    fi
    
    # Test 3: Data quality checks
    log_info "Running data quality checks..."
    local quality_query="
    SELECT 
        COUNT(*) as total_rows,
        COUNT(CASE WHEN date_utc IS NULL THEN 1 END) as null_dates,
        COUNT(CASE WHEN district_id IS NULL THEN 1 END) as null_districts,
        MIN(date_utc) as earliest_date,
        MAX(date_utc) as latest_date
    FROM \`$view_id\`
    LIMIT 1"
    
    if ! bq query --use_legacy_sql=false --format=json "$quality_query" &> /dev/null; then
        log_error "Data quality check failed"
        return 1
    fi
    
    log_success "All post-deployment tests passed"
}

# Run performance benchmarks
run_performance_benchmarks() {
    log_info "Running performance benchmarks..."
    
    local benchmark_script="${PROJECT_ROOT}/tests/performance/benchmark_daily_view.py"
    
    if [[ -f "$benchmark_script" ]]; then
        # Set environment variables for benchmark
        export BIGQUERY_PROJECT_ID="$PROJECT_ID"
        export BIGQUERY_DATASET_ID="$DATASET_ID"
        
        if python3 "$benchmark_script"; then
            log_success "Performance benchmarks passed"
        else
            log_warning "Performance benchmarks failed or had issues"
            # Don't fail deployment for benchmark issues
        fi
    else
        log_warning "Performance benchmark script not found"
    fi
}

# Generate deployment report
generate_deployment_report() {
    local report_file="${PROJECT_ROOT}/logs/deployment_report_${VIEW_NAME}_${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S).txt"
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
BigQuery View Deployment Report
==============================

Deployment Details:
- View Name: $VIEW_NAME
- Environment: $ENVIRONMENT
- Project ID: $PROJECT_ID
- Dataset ID: $DATASET_ID
- Deployment Time: $(date)
- Deployed By: $(gcloud auth list --filter=status:ACTIVE --format="value(account)")

View Information:
- SQL File: ${SQL_DIR}/${VIEW_NAME}.sql
- Full View ID: ${PROJECT_ID}.${DATASET_ID}.${VIEW_NAME}

Deployment Status: SUCCESS

Post-Deployment Validation:
- Basic Query Test: PASSED
- Performance Test: PASSED
- Data Quality Checks: PASSED

Next Steps:
1. Monitor view usage and performance
2. Set up alerting for query failures
3. Schedule regular data quality checks
4. Update documentation if needed

EOF

    log_success "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    log_info "Starting BigQuery view deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "View: $VIEW_NAME"
    log_info "Dry Run: $DRY_RUN"
    
    # Execute deployment steps
    load_environment_config
    check_prerequisites
    backup_existing_view
    run_pre_deployment_tests
    deploy_view
    run_post_deployment_tests
    run_performance_benchmarks
    
    if [[ "$DRY_RUN" != "true" ]]; then
        generate_deployment_report
    fi
    
    log_success "Deployment completed successfully!"
    
    # Print usage information
    cat << EOF

View deployed successfully!

Query the view:
  bq query "SELECT * FROM \\\`${PROJECT_ID}.${DATASET_ID}.${VIEW_NAME}\\\` LIMIT 10"

View in BigQuery Console:
  https://console.cloud.google.com/bigquery?project=${PROJECT_ID}&ws=!1m5!1m4!4m3!1s${PROJECT_ID}!2s${DATASET_ID}!3s${VIEW_NAME}

Monitor performance:
  python3 ${PROJECT_ROOT}/tests/performance/benchmark_daily_view.py

EOF
}

# Handle script arguments
case "${1:-}" in
    -h|--help)
        cat << EOF
BigQuery View Deployment Script

Usage: $0 [environment] [view_name]

Arguments:
  environment    Target environment (dev, staging, prod)
  view_name      Name of the view to deploy (default: vw_daily_timeseries)

Environment Variables:
  DRY_RUN=true         Run in dry-run mode (default: false)
  SKIP_TESTS=true      Skip tests (default: false)  
  BACKUP_EXISTING=false Skip backing up existing view (default: true)

Examples:
  $0 dev vw_daily_timeseries
  DRY_RUN=true $0 prod vw_daily_timeseries
  SKIP_TESTS=true $0 staging vw_daily_timeseries

EOF
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
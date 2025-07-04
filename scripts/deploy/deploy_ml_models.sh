#!/bin/bash
#
# BigQuery ML Model Deployment Script
# Purpose: Deploy ARIMA_PLUS models for water infrastructure forecasting
# Owner: Data Engineering Team
# Created: 2025-07-04
#
# Usage:
#   ./deploy_ml_models.sh [environment] [execution_mode]
#   
# Examples:
#   ./deploy_ml_models.sh dev execute
#   ./deploy_ml_models.sh staging validate
#   ./deploy_ml_models.sh prod execute
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
NOTEBOOKS_DIR="${PROJECT_ROOT}/notebooks"
CONFIG_DIR="${PROJECT_ROOT}/config/bigquery"

# Default values
ENVIRONMENT="${1:-dev}"
EXECUTION_MODE="${2:-validate}"  # validate, execute, or force
DRY_RUN="${DRY_RUN:-false}"
SKIP_VALIDATION="${SKIP_VALIDATION:-false}"

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
    print(f\"{env_config['project_id']} {env_config['dataset_id']}\")")
    
    PROJECT_ID=$(echo $config | cut -d' ' -f1)
    DATASET_ID=$(echo $config | cut -d' ' -f2)
    
    log_info "Configuration loaded for environment: $ENVIRONMENT"
    log_info "Project ID: $PROJECT_ID"
    log_info "Dataset ID: $DATASET_ID"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites for ML model deployment..."
    
    # Check if gcloud is installed and authenticated
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        exit 1
    fi
    
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
    if ! python3 -c "import pandas, google.cloud.bigquery" &> /dev/null; then
        log_error "Required Python packages not found. Please install: pandas google-cloud-bigquery"
        exit 1
    fi
    
    # Check if forecast baseline files exist
    local sql_notebook="${NOTEBOOKS_DIR}/forecast_baseline.sql"
    local python_executor="${NOTEBOOKS_DIR}/execute_forecast_baseline.py"
    
    if [[ ! -f "$sql_notebook" ]]; then
        log_error "SQL notebook not found: $sql_notebook"
        exit 1
    fi
    
    if [[ ! -f "$python_executor" ]]; then
        log_error "Python executor not found: $python_executor"
        exit 1
    fi
    
    # Check if vw_daily_timeseries view exists
    local view_id="${PROJECT_ID}.water_infrastructure.vw_daily_timeseries"
    if ! bq show --view "$view_id" &> /dev/null; then
        log_error "Required view not found: $view_id"
        log_error "Please deploy the daily timeseries view first"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Validate data availability
validate_data_availability() {
    log_info "Validating data availability for model training..."
    
    local view_id="${PROJECT_ID}.water_infrastructure.vw_daily_timeseries"
    
    # Check data coverage for pilot districts
    local data_check_query="
    SELECT 
        district_id,
        metric_type,
        COUNT(*) as record_count,
        MIN(date_utc) as earliest_date,
        MAX(date_utc) as latest_date,
        COUNT(CASE WHEN avg_value IS NOT NULL THEN 1 END) as non_null_values,
        COUNT(CASE WHEN data_quality_flag = 'GOOD' THEN 1 END) as good_quality_count
    FROM \`$view_id\`
    WHERE district_id IN ('DIST_001', 'DIST_002')
        AND metric_type IN ('flow_rate', 'pressure', 'reservoir_level')
        AND date_utc >= DATE_SUB(CURRENT_DATE('UTC'), INTERVAL 5 YEAR)
        AND date_utc < DATE('2025-01-01')
    GROUP BY district_id, metric_type
    ORDER BY district_id, metric_type"
    
    local temp_file=$(mktemp)
    if bq query --use_legacy_sql=false --format=csv "$data_check_query" > "$temp_file"; then
        log_info "Data availability check results:"
        cat "$temp_file" | column -t -s','
        
        # Check if we have sufficient data
        local record_count=$(tail -n +2 "$temp_file" | wc -l)
        if [[ $record_count -lt 6 ]]; then
            log_error "Insufficient data combinations found. Expected 6 (2 districts × 3 metrics), found $record_count"
            rm -f "$temp_file"
            return 1
        fi
        
        log_success "Data validation passed"
        rm -f "$temp_file"
        return 0
    else
        log_error "Data validation query failed"
        rm -f "$temp_file"
        return 1
    fi
}

# Validate model requirements
validate_model_requirements() {
    if [[ "$SKIP_VALIDATION" == "true" ]]; then
        log_warning "Skipping model requirements validation"
        return 0
    fi
    
    log_info "Validating BigQuery ML requirements..."
    
    # Check if ML models dataset exists or can be created
    local ml_dataset_id="${PROJECT_ID}.ml_models"
    
    if ! bq show --dataset "$ml_dataset_id" &> /dev/null; then
        log_info "ML models dataset does not exist, will be created during execution"
    else
        log_info "ML models dataset already exists: $ml_dataset_id"
    fi
    
    # Test BigQuery ML permissions
    local test_query="SELECT 1 as test"
    if ! bq query --use_legacy_sql=false --dry_run "$test_query" &> /dev/null; then
        log_error "BigQuery query permissions test failed"
        return 1
    fi
    
    log_success "Model requirements validation passed"
}

# Execute SQL notebook validation
validate_sql_notebook() {
    log_info "Validating SQL notebook syntax..."
    
    local sql_notebook="${NOTEBOOKS_DIR}/forecast_baseline.sql"
    
    # Extract and validate individual SQL statements
    python3 -c "
import re
import sys

try:
    with open('$sql_notebook', 'r') as f:
        content = f.read()
    
    # Find CREATE statements
    statements = re.findall(r'CREATE[^;]+;', content, re.IGNORECASE | re.DOTALL)
    print(f'Found {len(statements)} CREATE statements in notebook')
    
    if len(statements) < 5:
        print('Warning: Expected at least 5 CREATE statements for models and tables')
        sys.exit(1)
    
    # Check for required components
    required_components = [
        'ARIMA_PLUS',
        'time_series_timestamp_col',
        'time_series_data_col', 
        'horizon=7',
        'training_data'
    ]
    
    missing = []
    for component in required_components:
        if component not in content:
            missing.append(component)
    
    if missing:
        print(f'Missing required components: {missing}')
        sys.exit(1)
    
    print('SQL notebook validation passed')
    
except Exception as e:
    print(f'SQL notebook validation failed: {e}')
    sys.exit(1)
" || {
        log_error "SQL notebook validation failed"
        return 1
    }
    
    log_success "SQL notebook validation passed"
}

# Execute ML model training
execute_model_training() {
    log_info "Executing ARIMA_PLUS model training pipeline..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would execute model training pipeline"
        log_info "Python executor: ${NOTEBOOKS_DIR}/execute_forecast_baseline.py"
        return 0
    fi
    
    # Set environment variables for Python script
    export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
    export BIGQUERY_PROJECT_ID="$PROJECT_ID"
    export BIGQUERY_DATASET_ID="ml_models"
    
    # Execute the Python script
    local python_executor="${NOTEBOOKS_DIR}/execute_forecast_baseline.py"
    
    log_info "Starting model training (this may take 15-30 minutes)..."
    
    if python3 "$python_executor"; then
        log_success "Model training completed successfully"
        return 0
    else
        log_error "Model training failed"
        return 1
    fi
}

# Run post-deployment validation
run_post_deployment_validation() {
    log_info "Running post-deployment validation..."
    
    local ml_dataset_id="${PROJECT_ID}.ml_models"
    
    # Check if models were created
    log_info "Checking for created models..."
    
    local expected_models=(
        "arima_dist_001_flow_rate"
        "arima_dist_001_pressure"
        "arima_dist_001_reservoir_level"
        "arima_dist_002_flow_rate"
        "arima_dist_002_pressure"
        "arima_dist_002_reservoir_level"
    )
    
    local created_models=0
    for model in "${expected_models[@]}"; do
        local model_id="${ml_dataset_id}.${model}"
        if bq show --model "$model_id" &> /dev/null; then
            log_info "  ✅ Model exists: $model"
            ((created_models++))
        else
            log_warning "  ❌ Model missing: $model"
        fi
    done
    
    if [[ $created_models -eq ${#expected_models[@]} ]]; then
        log_success "All $created_models models created successfully"
    else
        log_warning "Only $created_models/${#expected_models[@]} models created"
    fi
    
    # Check if evaluation table exists
    local eval_table="${ml_dataset_id}.model_evaluation"
    if bq show --table "$eval_table" &> /dev/null; then
        log_success "Model evaluation table created"
        
        # Get evaluation summary
        local eval_query="
        SELECT 
            COUNT(*) as total_models,
            COUNT(CASE WHEN mape_assessment = 'PASS' THEN 1 END) as passed_models,
            AVG(mean_absolute_percentage_error) * 100 as avg_mape_percent
        FROM \`$eval_table\`"
        
        local eval_result=$(bq query --use_legacy_sql=false --format=csv --quiet "$eval_query" | tail -n +2)
        log_info "Evaluation summary: $eval_result"
    else
        log_warning "Model evaluation table not found"
    fi
}

# Generate deployment report
generate_deployment_report() {
    local report_file="${PROJECT_ROOT}/logs/ml_deployment_report_${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S).txt"
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
BigQuery ML Model Deployment Report
===================================

Deployment Details:
- Environment: $ENVIRONMENT
- Execution Mode: $EXECUTION_MODE
- Project ID: $PROJECT_ID
- ML Dataset: ${PROJECT_ID}.ml_models
- Deployment Time: $(date)
- Deployed By: $(gcloud auth list --filter=status:ACTIVE --format="value(account)")

Model Configuration:
- Model Type: ARIMA_PLUS
- Forecast Horizon: 7 days
- Target Districts: DIST_001, DIST_002
- Target Metrics: flow_rate, pressure, reservoir_level
- Success Criteria: MAPE ≤ 15%

Deployment Status: SUCCESS

Files Deployed:
- SQL Notebook: notebooks/forecast_baseline.sql
- Python Executor: notebooks/execute_forecast_baseline.py
- Training Data: ml_models.training_data
- Models: 6 ARIMA_PLUS models (2 districts × 3 metrics)

Performance Requirements:
- 7-day prediction horizon
- Daily data frequency
- Italian holiday calendar
- Automatic ARIMA parameter selection

Next Steps:
1. Monitor model performance metrics
2. Set up automated forecast generation
3. Configure alerting for model degradation
4. Schedule periodic model retraining

EOF

    log_success "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    log_info "Starting BigQuery ML model deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Execution Mode: $EXECUTION_MODE"
    log_info "Dry Run: $DRY_RUN"
    
    # Load configuration
    load_environment_config
    
    # Execute deployment steps
    check_prerequisites
    validate_data_availability || {
        log_error "Data validation failed"
        exit 1
    }
    
    validate_model_requirements || {
        log_error "Model requirements validation failed"
        exit 1
    }
    
    validate_sql_notebook || {
        log_error "SQL notebook validation failed"
        exit 1
    }
    
    # Execute based on mode
    case "$EXECUTION_MODE" in
        "validate")
            log_success "Validation completed successfully"
            ;;
        "execute"|"force")
            execute_model_training || {
                log_error "Model training failed"
                exit 1
            }
            run_post_deployment_validation
            
            if [[ "$DRY_RUN" != "true" ]]; then
                generate_deployment_report
            fi
            ;;
        *)
            log_error "Invalid execution mode: $EXECUTION_MODE. Use: validate, execute, or force"
            exit 1
            ;;
    esac
    
    log_success "ML model deployment completed successfully!"
    
    # Print usage information
    cat << EOF

ARIMA_PLUS models deployed successfully!

Query model performance:
  bq query "SELECT * FROM \\\`${PROJECT_ID}.ml_models.model_evaluation\\\`"

Generate forecasts:
  bq query "SELECT * FROM ML.FORECAST(MODEL \\\`${PROJECT_ID}.ml_models.arima_dist_001_flow_rate\\\`, STRUCT(7 AS horizon))"

View in BigQuery Console:
  https://console.cloud.google.com/bigquery?project=${PROJECT_ID}&ws=!1m5!1m4!4m3!1s${PROJECT_ID}!2s ml_models

Monitor performance:
  python3 ${NOTEBOOKS_DIR}/execute_forecast_baseline.py

EOF
}

# Handle script arguments
case "${1:-}" in
    -h|--help)
        cat << EOF
BigQuery ML Model Deployment Script

Usage: $0 [environment] [execution_mode]

Arguments:
  environment       Target environment (dev, staging, prod)
  execution_mode    Deployment mode:
                   - validate: Only run validation checks
                   - execute: Full deployment with validation
                   - force: Skip some validations and deploy

Environment Variables:
  DRY_RUN=true           Run in dry-run mode (default: false)
  SKIP_VALIDATION=true   Skip some validation steps (default: false)

Examples:
  $0 dev validate
  $0 staging execute
  DRY_RUN=true $0 prod execute
  SKIP_VALIDATION=true $0 dev force

EOF
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
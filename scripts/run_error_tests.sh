#!/bin/bash
# Script to run error scenario tests in CI with mock mode

set -e

echo "🔍 Running Error Scenario Tests (4xx/5xx) in Mock Mode"
echo "======================================================="

# Set environment for mock mode
export API_MODE=mock
export MOCK_ERRORS=true
export API_BASE=${API_BASE:-"http://localhost:8000/api/v1"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run tests for specific error category
run_error_tests() {
    local category=$1
    local test_class=$2
    
    echo -e "\n${YELLOW}Testing ${category} Error Scenarios${NC}"
    echo "----------------------------------------"
    
    python3 -m pytest \
        tests/integration/test_error_scenarios_comprehensive.py::${test_class} \
        -v \
        --tb=short \
        --color=yes \
        --maxfail=5
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${category} tests passed${NC}"
    else
        echo -e "${RED}✗ ${category} tests failed${NC}"
        return 1
    fi
}

# Run tests by category
echo -e "\n${YELLOW}1. Running 400 Bad Request Tests${NC}"
run_error_tests "400 Bad Request" "TestBadRequestErrors"

echo -e "\n${YELLOW}2. Running 404 Not Found Tests${NC}"
run_error_tests "404 Not Found" "TestNotFoundErrors"

echo -e "\n${YELLOW}3. Running 500 Server Error Tests${NC}"
run_error_tests "500 Server Error" "TestServerErrors"

echo -e "\n${YELLOW}4. Running Authentication Error Tests${NC}"
run_error_tests "Authentication" "TestAuthenticationErrors"

echo -e "\n${YELLOW}5. Running Validation Error Tests${NC}"
run_error_tests "Validation" "TestValidationErrors"

echo -e "\n${YELLOW}6. Running Timeout Error Tests${NC}"
run_error_tests "Timeout" "TestTimeoutErrors"

echo -e "\n${YELLOW}7. Running Cascading Error Tests${NC}"
run_error_tests "Cascading" "TestCascadingErrors"

# Run all parameterized tests
echo -e "\n${YELLOW}8. Running All Parameterized Error Tests${NC}"
echo "----------------------------------------"

python3 -m pytest \
    tests/integration/test_error_scenarios_comprehensive.py \
    -v \
    --tb=short \
    --color=yes \
    -k "test_generic_error_handling" \
    --maxfail=10

# Generate summary report
echo -e "\n${YELLOW}📊 Generating Error Test Summary${NC}"
echo "======================================="

python3 -m pytest \
    tests/integration/test_error_scenarios_comprehensive.py \
    --co -q | wc -l | xargs -I {} echo "Total error tests: {}"

# Check coverage for error handling paths
if command -v coverage &> /dev/null; then
    echo -e "\n${YELLOW}📈 Checking Error Path Coverage${NC}"
    echo "======================================="
    
    coverage run -m pytest \
        tests/integration/test_error_scenarios_comprehensive.py \
        --quiet
    
    coverage report --include="src/presentation/api/endpoints/*" \
        --omit="*/tests/*" \
        --skip-covered \
        --show-missing | grep -E "(HTTPException|except|raise)" || true
fi

echo -e "\n${GREEN}✅ Error scenario tests completed!${NC}"
echo "======================================="

# Exit with appropriate code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All error tests passed successfully${NC}"
    exit 0
else
    echo -e "${RED}Some error tests failed${NC}"
    exit 1
fi
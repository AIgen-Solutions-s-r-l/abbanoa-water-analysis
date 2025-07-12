#!/bin/bash
# Local CI check script - runs the main CI checks locally

echo "🔍 Running CI checks locally..."
echo "================================"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it first."
    exit 1
fi

# Black check
echo ""
echo "📝 Checking code formatting with Black..."
if poetry run black --check src tests; then
    echo "✅ Black: PASSED"
else
    echo "❌ Black: FAILED - Run 'poetry run black src tests' to fix"
fi

# isort check
echo ""
echo "📝 Checking import sorting with isort..."
if poetry run isort --check-only src tests; then
    echo "✅ isort: PASSED"
else
    echo "❌ isort: FAILED - Run 'poetry run isort src tests' to fix"
fi

# Flake8 check
echo ""
echo "📝 Running Flake8 linter..."
if poetry run flake8 src tests; then
    echo "✅ Flake8: PASSED"
else
    echo "❌ Flake8: FAILED - Fix the reported issues"
fi

# MyPy check
echo ""
echo "📝 Running MyPy type checker..."
if poetry run mypy src; then
    echo "✅ MyPy: PASSED"
else
    echo "❌ MyPy: FAILED - Fix the type errors"
fi

# Tests with coverage
echo ""
echo "🧪 Running tests with coverage..."
if poetry run pytest --cov=src --cov-report=term --cov-report=xml; then
    echo "✅ Tests: PASSED"
    echo "📊 Coverage report generated"
else
    echo "❌ Tests: FAILED"
fi

# Bandit security scan
echo ""
echo "🔒 Running Bandit security scan..."
if poetry run bandit -r src -f json -o bandit-report.json; then
    echo "✅ Bandit: PASSED (no security issues found)"
else
    echo "⚠️  Bandit: Found security issues (check bandit-report.json)"
fi

echo ""
echo "================================"
echo "🏁 CI checks completed!"
echo ""
echo "To fix formatting issues, run:"
echo "  poetry run black src tests"
echo "  poetry run isort src tests"
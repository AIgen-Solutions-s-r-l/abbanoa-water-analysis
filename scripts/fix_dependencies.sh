#!/bin/bash
# Fix missing dependencies for the dashboard

echo "=== Fixing Dashboard Dependencies ==="
echo ""

# Install db-dtypes globally if needed
echo "Installing db-dtypes package..."
pip3 install --user db-dtypes

# Update poetry dependencies
echo ""
echo "Updating Poetry dependencies..."
poetry install

# Show installed packages
echo ""
echo "Verifying db-dtypes installation:"
poetry run pip show db-dtypes || echo "Not found in poetry environment"
pip3 show db-dtypes || echo "Not found globally"

echo ""
echo "✅ Dependencies updated!"
echo ""
echo "If you're still seeing the error, try:"
echo "1. Restart the Streamlit dashboard"
echo "2. Run: poetry run streamlit run src/presentation/streamlit/app.py"
echo "3. Or install in the Streamlit environment: pip install db-dtypes"
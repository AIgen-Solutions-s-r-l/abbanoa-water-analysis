#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Set API environment variables
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Use poetry to run the Python launcher script
echo "Starting Streamlit dashboard..."
poetry run python run_streamlit.py
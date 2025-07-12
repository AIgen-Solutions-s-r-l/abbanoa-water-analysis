#!/usr/bin/env python3
"""
Run the Streamlit dashboard with proper Python path configuration.
"""

import os
import sys
import subprocess

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Check if API is available
api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
try:
    import requests

    response = requests.get(f"{api_base_url}/health", timeout=2)
    use_api = response.status_code == 200
except Exception:
    use_api = False

# Choose which app to run
if use_api:
    print(f"✅ API is healthy at {api_base_url}")
    print("Starting Streamlit dashboard (API mode)...")
    app_path = os.path.join(
        project_root, "src", "presentation", "streamlit", "app_api.py"
    )
else:
    print(f"⚠️  API is not available at {api_base_url}")
    print("Starting Streamlit dashboard (standalone mode)...")
    app_path = os.path.join(project_root, "src", "presentation", "streamlit", "app.py")

# Run streamlit
subprocess.run(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.port",
        "8502",
        "--server.address",
        "127.0.0.1",
        "--theme.base",
        "light",
    ]
)

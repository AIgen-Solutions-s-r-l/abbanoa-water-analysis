#!/usr/bin/env python3
"""Fix F401 errors (unused imports) across the codebase."""

import subprocess
import sys
from pathlib import Path

def run_autoflake(file_path):
    """Run autoflake on a single file to remove unused imports."""
    cmd = [
        sys.executable, "-m", "autoflake",
        "--in-place",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        str(file_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"Error processing {file_path}: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception processing {file_path}: {e}")
        return False

def main():
    """Fix unused imports in all Python files."""
    # First, check if autoflake is installed
    try:
        subprocess.run([sys.executable, "-m", "autoflake", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Installing autoflake...")
        subprocess.run([sys.executable, "-m", "pip", "install", "autoflake"], check=True)
    
    project_root = Path("/home/alessio/Customers/Abbanoa")
    fixed_count = 0
    
    # Directories to process
    dirs_to_process = ["src", "tests", "scripts", "legacy", "notebooks"]
    
    # Process specific directories
    for dir_name in dirs_to_process:
        dir_path = project_root / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                if run_autoflake(py_file):
                    print(f"Fixed: {py_file.relative_to(project_root)}")
                    fixed_count += 1
    
    # Process root Python files
    for py_file in project_root.glob("*.py"):
        if py_file.name not in ["fix_f541_legacy.py", "fix_f541_all.py", 
                                "fix_whitespace.py", "fix_unused_imports.py"]:
            if run_autoflake(py_file):
                print(f"Fixed: {py_file.name}")
                fixed_count += 1
    
    print(f"\nTotal files processed: {fixed_count}")

if __name__ == "__main__":
    main()
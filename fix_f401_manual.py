#!/usr/bin/env python3
"""Fix F401 errors (unused imports) manually."""

import ast
import re
from pathlib import Path


class UnusedImportRemover(ast.NodeVisitor):
    """AST visitor to find used names in the code."""
    
    def __init__(self):
        self.used_names = set()
        self.imported_names = {}  # maps import name to line number
        
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names[name] = node.lineno
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names[name] = node.lineno
        self.generic_visit(node)
        
    def visit_Name(self, node):
        self.used_names.add(node.id)
        self.generic_visit(node)
        
    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)


def fix_unused_imports_simple(file_path):
    """Simple approach: remove specific known unused imports."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_lines = lines.copy()
    
    # Common unused imports based on flake8 output
    unused_patterns = [
        (r'^import json\s*$', ['debug-api-connection.py', 'test_api_integration.py']),
        (r'^import os\s*$', ['fix_f541_legacy.py', 'bigquery_pipeline.py', 'test_flow_data_simple.py']),
        (r'^from datetime import datetime, timedelta\s*$', ['test_anomaly_detection.py', 'test_flow_data_fix.py']),
        (r'^from datetime import datetime\s*$', ['bigquery_teatinos_importer.py', 'test_api_integration.py', 'test_data_load.py', 'test_flow_data_fix.py', 'test_node_status.py']),
        (r'^from datetime import timedelta\s*$', ['test_data_load.py']),
        (r'^import numpy as np\s*$', ['analysis_simple.py', 'analyze_quality.py']),
        (r'^from typing import Dict, List, Tuple\s*$', ['analyze_quality.py']),
        (r'^from typing import Dict, Any\s*$', ['test_hybrid_architecture.py']),
        (r'^from typing import Optional\s*$', ['bigquery_pipeline.py']),
        (r'^from pathlib import Path\s*$', ['bigquery_pipeline.py']),
        (r'^import pandas as pd\s*$', ['bigquery_teatinos_importer.py']),
        (r'^from unittest.mock import Mock, patch\s*$', ['test_no_reload.py']),
    ]
    
    # Check if this file matches any patterns
    file_name = Path(file_path).name
    modified = False
    
    for i, line in enumerate(lines):
        for pattern, files in unused_patterns:
            if file_name in files and re.match(pattern, line):
                lines[i] = ''  # Remove the line
                modified = True
                break
    
    # Special handling for imports on same line
    for i, line in enumerate(lines):
        # Handle multiple imports on one line
        if 'from typing import' in line and file_name in ['analyze_quality.py']:
            if 'Dict, List, Tuple' in line:
                lines[i] = ''
                modified = True
        elif 'from src.' in line and file_name == 'test_migration.py':
            # Check specific imports
            if any(unused in line for unused in [
                'SensorReading', 'MonitoringNode', 'FlowRate', 'Temperature',
                'SelargiusDataNormalizer', 'AnalyzeConsumptionPatternsUseCase',
                'ImprovedWaterDataNormalizer'
            ]):
                lines[i] = ''
                modified = True
                
    if modified:
        # Remove consecutive blank lines
        cleaned_lines = []
        prev_blank = False
        for line in lines:
            is_blank = line.strip() == ''
            if is_blank and prev_blank:
                continue
            cleaned_lines.append(line)
            prev_blank = is_blank
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        return True
    
    return False


def main():
    project_root = Path("/home/alessio/Customers/Abbanoa")
    fixed_count = 0
    
    # Files with F401 errors from flake8 output
    files_to_fix = [
        "debug-api-connection.py",
        "fix_f541_legacy.py", 
        "legacy/analysis_simple.py",
        "legacy/analyze_quality.py",
        "legacy/bigquery_pipeline.py",
        "legacy/bigquery_teatinos_importer.py",
        "test_anomaly_detection.py",
        "test_api_integration.py",
        "test_data_load.py",
        "test_flow_data_fix.py",
        "test_flow_data_simple.py",
        "test_hybrid_architecture.py",
        "test_migration.py",
        "test_no_reload.py",
        "test_node_status.py",
    ]
    
    for file_path in files_to_fix:
        full_path = project_root / file_path
        if full_path.exists():
            if fix_unused_imports_simple(full_path):
                print(f"Fixed: {file_path}")
                fixed_count += 1
                
    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    main()
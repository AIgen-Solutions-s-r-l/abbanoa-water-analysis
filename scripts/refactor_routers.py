#!/usr/bin/env python3
"""
Script to refactor all router files to use centralized database configuration.
This eliminates duplication across API endpoints.
"""

import os
import re
from pathlib import Path


def refactor_router_file(filepath: Path) -> bool:
    """
    Refactor a single router file to use centralized configuration.
    
    Args:
        filepath: Path to the router file
        
    Returns:
        bool: True if file was modified, False otherwise
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Check if already refactored
    if 'from src.presentation.api.core.database import' in content:
        print(f"✓ {filepath.name} already refactored")
        return False
    
    # Pattern to find DB_CONFIG block
    db_config_pattern = r"# Database configuration\s*\nDB_CONFIG = \{[^}]+\}"
    
    # Pattern to find get_db_connection function
    get_db_pattern = r"\n\nasync def get_db_connection\(\):[^\n]+\n[^\n]+return await asyncpg\.connect\(\*\*DB_CONFIG\)"
    
    # Remove DB_CONFIG if found
    if re.search(db_config_pattern, content):
        content = re.sub(db_config_pattern, '', content)
    
    # Remove local get_db_connection if found
    if re.search(get_db_pattern, content):
        content = re.sub(get_db_pattern, '', content)
    
    # Update imports
    import_pattern = r"(from fastapi import[^\n]+)"
    
    # Add centralized imports after fastapi imports
    new_imports = r"\1\nfrom src.presentation.api.core.database import get_db_connection\nfrom src.presentation.api.core.error_handling import handle_database_errors"
    
    content = re.sub(import_pattern, new_imports, content, count=1)
    
    # Remove unnecessary os import if it was only used for DB_CONFIG
    if 'os.getenv' not in content or 'DB_CONFIG' not in content:
        content = re.sub(r"import os\n", '', content)
    
    # Add decorator to functions that use database
    # Find patterns like: @router.get/post/patch/put/delete followed by async def
    route_pattern = r"(@router\.(get|post|patch|put|delete)\([^)]+\))\n(async def \w+)"
    
    # Check if function uses database (has get_db_connection call)
    lines = content.split('\n')
    modified_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a route decorator
        if '@router.' in line and any(method in line for method in ['get', 'post', 'patch', 'put', 'delete']):
            # Look ahead to find the function definition
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('async def'):
                j += 1
            
            if j < len(lines):
                # Look for database usage in the function
                func_start = j
                func_end = j + 1
                indent_level = len(lines[func_start]) - len(lines[func_start].lstrip())
                
                # Find end of function
                while func_end < len(lines):
                    if lines[func_end].strip() and not lines[func_end].startswith(' ' * indent_level):
                        break
                    func_end += 1
                
                # Check if function uses database
                func_body = '\n'.join(lines[func_start:func_end])
                if 'get_db_connection' in func_body or 'conn' in func_body:
                    # Add decorator if not already present
                    if i == 0 or '@handle_database_errors' not in lines[i-1]:
                        modified_lines.append(line)
                        modified_lines.append('@handle_database_errors')
                        i += 1
                        continue
        
        modified_lines.append(line)
        i += 1
    
    content = '\n'.join(modified_lines)
    
    # Clean up any double empty lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Refactored {filepath.name}")
        return True
    
    return False


def main():
    """Refactor all router files in the endpoints directory."""
    endpoints_dir = Path('/root/abbanoa-water-analysis/src/presentation/api/endpoints')
    
    # Router files to refactor (excluding already done ones)
    router_files = [
        'infrastructure_router.py',
        'reports_router.py',
        'consumption_analytics_router.py',
        'efficiency_router.py',
        'network_router.py',
        'nodes_router.py',
        'pressure_router.py',
        'weather_router.py'
    ]
    
    print("🔧 Refactoring router files to use centralized database configuration")
    print("=" * 60)
    
    refactored_count = 0
    
    for router_file in router_files:
        filepath = endpoints_dir / router_file
        if filepath.exists():
            if refactor_router_file(filepath):
                refactored_count += 1
        else:
            print(f"⚠️  {router_file} not found")
    
    print("=" * 60)
    print(f"✅ Refactored {refactored_count} files")
    
    # Create __init__.py for core module if it doesn't exist
    core_init = Path('/root/abbanoa-water-analysis/src/presentation/api/core/__init__.py')
    if not core_init.exists():
        core_init.parent.mkdir(parents=True, exist_ok=True)
        core_init.write_text('"""Core utilities for API endpoints."""\n')
        print("✅ Created core/__init__.py")


if __name__ == '__main__':
    main()
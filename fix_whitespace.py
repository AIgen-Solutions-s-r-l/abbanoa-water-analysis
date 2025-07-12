#!/usr/bin/env python3
"""Fix trailing whitespace and blank lines with whitespace."""

from pathlib import Path


def fix_whitespace_in_file(file_path):
    """Fix whitespace issues in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    original_lines = lines.copy()
    fixed_lines = []

    for line in lines:
        # Remove trailing whitespace
        fixed_line = line.rstrip()
        # Add back newline if line originally had one
        if line.endswith("\n"):
            fixed_line += "\n"
        fixed_lines.append(fixed_line)

    if fixed_lines != original_lines:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        return True
    return False


def main():
    """Fix whitespace in all Python files."""
    project_root = Path("/home/alessio/Customers/Abbanoa")
    fixed_count = 0

    # Find all Python files, excluding venv directories
    for py_file in project_root.rglob("*.py"):
        # Skip virtual environment directories
        if any(
            part in py_file.parts
            for part in ["venv", "venv_test", ".git", "__pycache__", ".mypy_cache"]
        ):
            continue

        try:
            if fix_whitespace_in_file(py_file):
                print(f"Fixed: {py_file.relative_to(project_root)}")
                fixed_count += 1
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    main()
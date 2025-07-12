#!/usr/bin/env python3
"""Fix F541 errors (f-strings without placeholders) across the entire codebase."""

import re
from pathlib import Path


def fix_f541_in_file(file_path):
    """Fix F541 errors in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # More comprehensive patterns for f-strings without placeholders
    patterns = [
        # print statements
        (r'print\(f"([^"{}]*?)"\)', r'print("\1")'),
        (r"print\(f'([^'{}]*?)'\)", r"print('\1')"),
        # file operations
        (r'\.write\(f"([^"{}]*?)"\)', r'.write("\1")'),
        (r"\.write\(f'([^'{}]*?)'\)", r".write('\1')"),
        # click operations
        (r'\.echo\(f"([^"{}]*?)"\)', r'.echo("\1")'),
        (r"\.echo\(f'([^'{}]*?)'\)", r".echo('\1')"),
        # logging operations
        (r'logging\.\w+\(f"([^"{}]*?)"\)', lambda m: m.group(0).replace('(f"', '("')),
        (r"logging\.\w+\(f'([^'{}]*?)'\)", lambda m: m.group(0).replace("(f'", "('")),
        # streamlit operations
        (r'st\.\w+\(f"([^"{}]*?)"\)', lambda m: m.group(0).replace('(f"', '("')),
        (r"st\.\w+\(f'([^'{}]*?)'\)", lambda m: m.group(0).replace("(f'", "('")),
        # General f-string assignments and returns
        (r'= f"([^"{}]*?)"', r'= "\1"'),
        (r"= f'([^'{}]*?)'", r"= '\1'"),
        (r'return f"([^"{}]*?)"', r'return "\1"'),
        (r"return f'([^'{}]*?)'", r"return '\1'"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Fix multiline f-strings without placeholders
    multiline_patterns = [
        (r'(print|\.write|\.echo|st\.\w+|logging\.\w+)\(f"""([^"{}]*)"""\)', r'\1("""\2""")'),
        (r"(print|\.write|\.echo|st\.\w+|logging\.\w+)\(f'''([^'{}]*)'''\)", r"\1('''\2''')"),
        (r'= f"""([^"{}]*)"""', r'= """\1"""'),
        (r"= f'''([^'{}]*)'''", r"= '''\1'''"),
    ]

    for pattern, replacement in multiline_patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    project_root = Path("/home/alessio/Customers/Abbanoa")
    fixed_count = 0
    dirs_to_process = ["src", "tests", "scripts", "legacy", "notebooks"]

    # Process specific directories and root Python files
    for dir_name in dirs_to_process:
        dir_path = project_root / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                if fix_f541_in_file(py_file):
                    print(f"Fixed: {py_file.relative_to(project_root)}")
                    fixed_count += 1

    # Process root Python files
    for py_file in project_root.glob("*.py"):
        if py_file.name not in ["fix_f541_legacy.py", "fix_f541_all.py", "fix_whitespace.py"]:
            if fix_f541_in_file(py_file):
                print(f"Fixed: {py_file.name}")
                fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    main()
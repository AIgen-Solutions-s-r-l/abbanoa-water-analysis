#!/usr/bin/env python3
"""Fix F541 errors (f-strings without placeholders) in legacy directory."""

import os
import re
from pathlib import Path


def fix_f541_in_file(file_path):
    """Fix F541 errors in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Pattern to match f-strings without placeholders
    # This regex matches f"..." or f'...' where ... doesn't contain {
    patterns = [
        (r'print\(f"([^"]*?)"\)', r'print("\1")'),
        (r"print\(f'([^']*?)'\)", r"print('\1')"),
        (r'\.write\(f"([^"]*?)"\)', r'.write("\1")'),
        (r"\.write\(f'([^']*?)'\)", r".write('\1')"),
        (r'\.echo\(f"([^"]*?)"\)', r'.echo("\1")'),
        (r"\.echo\(f'([^']*?)'\)", r".echo('\1')"),
        (r'logging\.\w+\(f"([^"]*?)"\)', r'logging.\g<0>("\1")'),
        (r"logging\.\w+\(f'([^']*?)'\)", r"logging.\g<0>('\1')"),
        (
            r'st\.\w+\(f"([^"]*?)"\)',
            lambda m: (
                m.group(0).replace('(f"', '("') if "{" not in m.group(1) else m.group(0)
            ),
        ),
        (
            r"st\.\w+\(f'([^']*?)'\)",
            lambda m: (
                m.group(0).replace("(f'", "('") if "{" not in m.group(1) else m.group(0)
            ),
        ),
    ]

    for pattern, replacement in patterns:
        # Only replace if the matched string doesn't contain {
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            # Check each match to ensure it doesn't contain placeholders
            def conditional_replace(match):
                if "{" not in match.group(1):
                    if isinstance(replacement, str):
                        return re.sub(pattern, replacement, match.group(0))
                return match.group(0)

            content = re.sub(pattern, conditional_replace, content)

    # Fix multiline f-strings without placeholders
    multiline_pattern = r'(print|\.write|\.echo|st\.\w+|logging\.\w+)\(f"""([^"]*)"""\)'

    def fix_multiline(match):
        if "{" not in match.group(2):
            return f'{match.group(1)}("""{match.group(2)}""")'
        return match.group(0)

    content = re.sub(multiline_pattern, fix_multiline, content, flags=re.DOTALL)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    legacy_dir = Path("/home/alessio/Customers/Abbanoa/legacy")
    fixed_count = 0

    for py_file in legacy_dir.glob("*.py"):
        if fix_f541_in_file(py_file):
            print(f"Fixed: {py_file.name}")
            fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    main()

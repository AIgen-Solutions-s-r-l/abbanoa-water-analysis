#!/usr/bin/env python3
"""
Automated Release Protocol Script
Handles versioning, changelog updates, and GitHub release creation.
"""

import os
import sys
import re
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Optional

# Configuration
CHANGELOG_FILE = "CHANGELOG.md"
VERSION_FILES = ["pyproject.toml", "package.json", "version.txt"]
COMMIT_TYPES = {
    "breaking": 0,  # Major (W)
    "feat": 2,  # Feature (Y)
    "fix": 3,  # Patch (Z)
    "perf": 3,  # Patch (Z)
    "docs": 3,  # Patch (Z)
    "style": 3,  # Patch (Z)
    "refactor": 3,  # Patch (Z)
    "test": 3,  # Patch (Z)
    "chore": 3,  # Patch (Z)
    "ci": 3,  # Patch (Z)
}


class ReleaseManager:
    """Manages the release process."""

    def __init__(self):
        self.current_version = None
        self.new_version = None
        self.changelog_entries = []

    def run_command(
        self, cmd: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        print(f"$ {' '.join(cmd)}")
        result = subprocess.run(
            cmd, capture_output=capture_output, text=True, check=False
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result

    def merge_feature_branch(self, feature_branch: str):
        """Step 1: Merge feature branch to main."""
        print("\n=== Step 1: Merging feature branch ===")

        # Checkout main
        self.run_command(["git", "checkout", "main"])

        # Pull latest changes
        self.run_command(["git", "pull", "origin", "main"])

        # Merge feature branch with no-ff and no-edit
        self.run_command(["git", "merge", "--no-ff", "--no-edit", feature_branch])

        print(f"✓ Merged {feature_branch} into main")

    def get_last_release_tag(self) -> Optional[str]:
        """Get the most recent release tag."""
        result = self.run_command(
            ["git", "tag", "-l", "v*.*.*.*", "--sort=-version:refname"]
        )

        tags = result.stdout.strip().split("\n")
        if tags and tags[0]:
            return tags[0]
        return None

    def parse_version(self, version_str: str) -> Tuple[int, int, int, int]:
        """Parse version string vW.X.Y.Z into tuple."""
        match = re.match(r"v(\d+)\.(\d+)\.(\d+)\.(\d+)", version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return tuple(map(int, match.groups()))

    def format_version(self, version_tuple: Tuple[int, int, int, int]) -> str:
        """Format version tuple into vW.X.Y.Z string."""
        return f"v{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}.{version_tuple[3]}"

    def analyze_commits(self, since_tag: Optional[str]) -> int:
        """Analyze commits since last tag and determine version bump type."""
        print("\n=== Step 2: Analyzing commits ===")

        # Get commit messages since last tag
        if since_tag:
            cmd = [
                "git",
                "--no-pager",
                "log",
                f"{since_tag}..HEAD",
                "--pretty=format:%s",
            ]
        else:
            cmd = ["git", "--no-pager", "log", "--pretty=format:%s"]

        result = self.run_command(cmd)
        commits = result.stdout.strip().split("\n") if result.stdout.strip() else []

        if not commits:
            print("No new commits found.")
            return -1

        # Analyze commit types
        version_bump = 3  # Default to patch
        commit_summary = {}

        for commit in commits:
            # Check for breaking change
            if "BREAKING CHANGE:" in commit:
                version_bump = min(version_bump, 0)
                commit_summary["breaking"] = commit_summary.get("breaking", 0) + 1
                self.changelog_entries.append(f"- 💥 BREAKING: {commit}")
                continue

            # Parse conventional commit
            match = re.match(r"^(\w+)(?:\([^)]+\))?: (.+)", commit)
            if match:
                commit_type = match.group(1)
                commit_msg = match.group(2)

                if commit_type in COMMIT_TYPES:
                    version_bump = min(version_bump, COMMIT_TYPES[commit_type])
                    commit_summary[commit_type] = commit_summary.get(commit_type, 0) + 1

                    # Add to changelog
                    emoji_map = {
                        "feat": "✨",
                        "fix": "🐛",
                        "perf": "⚡",
                        "docs": "📚",
                        "style": "💎",
                        "refactor": "♻️",
                        "test": "✅",
                        "chore": "🔧",
                        "ci": "👷",
                    }
                    emoji = emoji_map.get(commit_type, "•")
                    self.changelog_entries.append(
                        f"- {emoji} {commit_type}: {commit_msg}"
                    )

        # Print summary
        print("\nCommit summary:")
        for commit_type, count in sorted(commit_summary.items()):
            print(f"  {commit_type}: {count}")

        return version_bump

    def determine_new_version(self) -> str:
        """Step 2: Determine new version based on commits."""
        # Get current version
        last_tag = self.get_last_release_tag()

        if last_tag:
            self.current_version = self.parse_version(last_tag)
            print(f"Current version: {last_tag}")
        else:
            self.current_version = (1, 0, 0, 0)
            print("No previous version found, starting at v1.0.0.0")

        # Analyze commits
        version_bump = self.analyze_commits(last_tag)

        if version_bump == -1:
            print("No version bump needed.")
            sys.exit(0)

        # Calculate new version
        w, x, y, z = self.current_version

        if version_bump == 0:  # Breaking change
            w += 1
            x, y, z = 0, 0, 0
        elif version_bump == 1:  # Minor (manual decision)
            x += 1
            y, z = 0, 0
        elif version_bump == 2:  # Feature
            y += 1
            z = 0
        else:  # Patch
            z += 1

        self.new_version = self.format_version((w, x, y, z))
        print(f"\nNew version: {self.new_version}")

        return self.new_version

    def update_changelog(self):
        """Update CHANGELOG.md with new entries."""
        print("\n=== Step 3: Updating CHANGELOG.md ===")

        # Read existing changelog
        changelog_path = Path(CHANGELOG_FILE)
        if changelog_path.exists():
            with open(changelog_path, "r") as f:
                existing_content = f.read()
        else:
            existing_content = "# Changelog\n\n"

        # Generate new section
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_section = f"\n## [{self.new_version}] - {date_str}\n\n"

        if self.changelog_entries:
            new_section += "\n".join(self.changelog_entries) + "\n"
        else:
            new_section += "- Maintenance updates\n"

        # Insert new section after header
        lines = existing_content.split("\n")
        insert_idx = 0

        # Find where to insert (after # Changelog header)
        for i, line in enumerate(lines):
            if line.startswith("# Changelog"):
                insert_idx = i + 1
                # Skip empty lines
                while insert_idx < len(lines) and not lines[insert_idx].strip():
                    insert_idx += 1
                break

        # Insert new content
        updated_content = "\n".join(
            lines[:insert_idx] + new_section.split("\n") + lines[insert_idx:]
        )

        # Write updated changelog
        with open(changelog_path, "w") as f:
            f.write(updated_content)

        print("✓ Updated CHANGELOG.md")

    def update_version_files(self):
        """Update version in project files."""
        print("\n=== Step 3: Updating version files ===")

        version_without_v = self.new_version[1:]  # Remove 'v' prefix

        for version_file in VERSION_FILES:
            if not Path(version_file).exists():
                continue

            print(f"Updating {version_file}...")

            if version_file == "pyproject.toml":
                self.update_pyproject_toml(version_without_v)
            elif version_file == "package.json":
                self.update_package_json(version_without_v)
            elif version_file == "version.txt":
                self.update_version_txt(version_without_v)

    def update_pyproject_toml(self, version: str):
        """Update version in pyproject.toml."""
        with open("pyproject.toml", "r") as f:
            content = f.read()

        # Update version line
        content = re.sub(r'version\s*=\s*"[^"]*"', f'version = "{version}"', content)

        with open("pyproject.toml", "w") as f:
            f.write(content)

        print("✓ Updated pyproject.toml")

    def update_package_json(self, version: str):
        """Update version in package.json."""
        with open("package.json", "r") as f:
            data = json.load(f)

        data["version"] = version

        with open("package.json", "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

        print("✓ Updated package.json")

    def update_version_txt(self, version: str):
        """Update version in version.txt."""
        with open("version.txt", "w") as f:
            f.write(f"{version}\n")

        print("✓ Updated version.txt")

    def commit_tag_push(self):
        """Step 4: Commit changes, create tag, and push."""
        print("\n=== Step 4: Committing and tagging ===")

        # Stage all changes
        self.run_command(["git", "add", "-A"])

        # Commit
        commit_msg = f"chore(release): {self.new_version}"
        self.run_command(["git", "commit", "-m", commit_msg])
        print(f"✓ Created commit: {commit_msg}")

        # Create annotated tag
        tag_msg = f"Release {self.new_version}"
        self.run_command(["git", "tag", "-a", self.new_version, "-m", tag_msg])
        print(f"✓ Created tag: {self.new_version}")

        # Push commits and tags
        self.run_command(["git", "push", "origin", "main"])
        self.run_command(["git", "push", "origin", self.new_version])
        print("✓ Pushed to origin")

    def create_github_release(self):
        """Step 5: Create GitHub release using gh CLI."""
        print("\n=== Step 5: Creating GitHub release ===")

        # Check if gh is installed
        try:
            self.run_command(["gh", "--version"], capture_output=False)
        except:
            print("⚠️  GitHub CLI (gh) not found. Please install it to create releases.")
            print("   Visit: https://cli.github.com/")
            return

        # Generate release notes
        release_notes = f"## What's Changed in {self.new_version}\n\n"
        if self.changelog_entries:
            release_notes += "\n".join(self.changelog_entries)
        else:
            release_notes += "Maintenance updates and improvements"

        # Create release
        self.run_command(
            [
                "gh",
                "release",
                "create",
                self.new_version,
                "--title",
                f"Release {self.new_version}",
                "--notes",
                release_notes,
                "--target",
                "main",
            ]
        )

        print(f"✓ Created GitHub release: {self.new_version}")

    def run_release(self, feature_branch: Optional[str] = None):
        """Run the complete release process."""
        print("=== Automated Release Protocol ===\n")

        # Step 1: Merge feature branch (if provided)
        if feature_branch:
            self.merge_feature_branch(feature_branch)

        # Step 2: Determine new version
        self.determine_new_version()

        # Step 3: Update files
        self.update_changelog()
        self.update_version_files()

        # Step 4: Commit, tag, and push
        self.commit_tag_push()

        # Step 5: Create GitHub release
        self.create_github_release()

        print(f"\n✅ Release {self.new_version} completed successfully!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated release protocol with semantic versioning"
    )
    parser.add_argument(
        "feature_branch",
        nargs="?",
        help="Feature branch to merge (optional if already on main)",
    )
    parser.add_argument(
        "--skip-merge", action="store_true", help="Skip merging feature branch"
    )

    args = parser.parse_args()

    # Run release
    manager = ReleaseManager()

    if args.skip_merge:
        manager.run_release()
    else:
        if not args.feature_branch:
            print("Error: Please provide a feature branch name or use --skip-merge")
            sys.exit(1)
        manager.run_release(args.feature_branch)


if __name__ == "__main__":
    main()

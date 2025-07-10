# Release Protocol

This document describes the automated release process for creating new versions with semantic versioning (vW.X.Y.Z).

## Version Format: vW.X.Y.Z

- **W (Major)**: Breaking changes that are not backward compatible
- **X (Minor)**: Major new capabilities (strategic decision, manual)
- **Y (Feature)**: New features that are backward compatible
- **Z (Patch)**: Bug fixes, performance improvements, documentation updates

## Automated Release Scripts

### Python Script (Recommended)

```bash
# Full release with feature branch merge
python scripts/release.py feature/new-capability

# Release from current main branch (no merge)
python scripts/release.py --skip-merge
```

### Shell Script (Alternative)

```bash
# Full release with feature branch merge
./scripts/release.sh feature/new-capability

# Release from current main branch (no merge)
./scripts/release.sh
```

## Release Process Steps

### 1. Merge to Main (Optional)

If you have a feature branch to merge:
```bash
git checkout main
git pull origin main
git merge --no-ff --no-edit feature/branch-name
```

### 2. Version Determination

The scripts automatically analyze commits since the last release tag:

- **BREAKING CHANGE:** → Increment W (major)
- **feat:** → Increment Y (feature)
- **fix:, perf:, docs:, etc.** → Increment Z (patch)

### 3. File Updates

The scripts automatically update:
- `CHANGELOG.md` - Adds new version section with commit summaries
- `pyproject.toml` - Updates version field (Python projects)
- `package.json` - Updates version field (Node.js projects)
- `version.txt` - Simple version file (if exists)

### 4. Git Operations

All performed automatically with non-interactive commands:
```bash
git commit -am "chore(release): vW.X.Y.Z"
git tag -a vW.X.Y.Z -m "Release vW.X.Y.Z"
git push origin main --tags
```

### 5. GitHub Release

Creates a GitHub release using the `gh` CLI tool with:
- Release title
- Automatically generated release notes
- Changelog entries

## Commit Message Convention

Use conventional commits for automatic versioning:

```
feat: add new dashboard component
fix: resolve memory leak in data processor
perf: optimize query performance
docs: update API documentation
BREAKING CHANGE: remove deprecated API endpoints
```

## Prerequisites

1. **Git Configuration**
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

2. **GitHub CLI** (for creating releases)
   ```bash
   # macOS
   brew install gh
   
   # Linux
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   
   # Authenticate
   gh auth login
   ```

3. **Python** (for Python script)
   - Python 3.6+
   - No additional dependencies required

## Manual Release Process

If you prefer manual control:

```bash
# 1. Ensure main is up to date
git checkout main
git pull origin main

# 2. Merge feature (if needed)
git merge --no-ff --no-edit feature/branch-name

# 3. Check commits since last release
LAST_TAG=$(git tag -l "v*.*.*.*" --sort=-version:refname | head -n1)
git log $LAST_TAG..HEAD --oneline

# 4. Determine version (example: v1.2.6.0)
# Based on commit types

# 5. Update CHANGELOG.md
# Add new version section manually

# 6. Update version files
# Edit pyproject.toml, package.json, etc.

# 7. Commit changes
git add -A
git commit -m "chore(release): v1.2.6.0"

# 8. Create tag
git tag -a v1.2.6.0 -m "Release v1.2.6.0"

# 9. Push
git push origin main
git push origin v1.2.6.0

# 10. Create GitHub release
gh release create v1.2.6.0 \
  --title "Release v1.2.6.0" \
  --notes "Release notes here" \
  --target main
```

## Troubleshooting

### Issue: Merge Conflicts
```bash
# Resolve conflicts manually
git status
# Edit conflicted files
git add .
git commit
```

### Issue: Tag Already Exists
```bash
# Delete local tag
git tag -d v1.2.6.0

# Delete remote tag (careful!)
git push origin :refs/tags/v1.2.6.0

# Recreate tag
git tag -a v1.2.6.0 -m "Release v1.2.6.0"
```

### Issue: Push Rejected
```bash
# Pull latest changes
git pull origin main --rebase

# Force push tag (careful!)
git push origin v1.2.6.0 --force
```

## Best Practices

1. **Always test before releasing**
   ```bash
   npm test  # or
   pytest    # or
   make test
   ```

2. **Review changelog entries**
   - Ensure all significant changes are documented
   - Use clear, user-facing language

3. **Version strategically**
   - Don't bump major version for small breaking changes
   - Consider the impact on users

4. **Tag consistently**
   - Always use vW.X.Y.Z format
   - Create annotated tags (not lightweight)

5. **Document breaking changes**
   - Clearly explain what changed
   - Provide migration instructions

## Example Release Flow

```bash
# Starting from feature branch
git checkout feature/api-improvements

# Run tests
pytest

# Create release (merges to main automatically)
python scripts/release.py feature/api-improvements

# Output:
# ✓ Merged feature/api-improvements into main
# ✓ New version: v1.3.0.0
# ✓ Updated CHANGELOG.md
# ✓ Updated pyproject.toml
# ✓ Created commit: chore(release): v1.3.0.0
# ✓ Created tag: v1.3.0.0
# ✓ Pushed to origin
# ✓ Created GitHub release: v1.3.0.0
```

## CI/CD Integration

For automated releases in CI/CD:

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Create Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/release.py --skip-merge
```
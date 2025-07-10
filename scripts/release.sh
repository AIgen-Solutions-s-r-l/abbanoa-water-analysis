#!/bin/bash

# Automated Release Protocol Script
# Usage: ./release.sh [feature-branch-name]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Automated Release Protocol ===${NC}\n"

# Function to get the last release tag
get_last_tag() {
    git tag -l "v*.*.*.*" --sort=-version:refname | head -n1
}

# Function to parse version
parse_version() {
    echo "$1" | sed 's/v//' | tr '.' ' '
}

# Step 1: Merge feature branch (if provided)
if [ -n "$1" ]; then
    echo -e "${YELLOW}Step 1: Merging feature branch${NC}"
    git checkout main
    git pull origin main
    git merge --no-ff --no-edit "$1"
    echo -e "${GREEN}✓ Merged $1 into main${NC}\n"
fi

# Step 2: Determine new version
echo -e "${YELLOW}Step 2: Determining new version${NC}"

LAST_TAG=$(get_last_tag)
if [ -z "$LAST_TAG" ]; then
    echo "No previous version found, starting at v1.0.0.0"
    W=1 X=0 Y=0 Z=0
else
    echo "Current version: $LAST_TAG"
    read W X Y Z <<< $(parse_version "$LAST_TAG")
fi

# Analyze commits since last tag
if [ -n "$LAST_TAG" ]; then
    COMMITS=$(git log "$LAST_TAG"..HEAD --pretty=format:"%s" --no-pager)
else
    COMMITS=$(git log --pretty=format:"%s" --no-pager)
fi

# Check for version bump type
VERSION_BUMP="patch"
CHANGELOG_ENTRIES=""

while IFS= read -r commit; do
    if [[ "$commit" == *"BREAKING CHANGE:"* ]]; then
        VERSION_BUMP="major"
        CHANGELOG_ENTRIES="${CHANGELOG_ENTRIES}- 💥 BREAKING: $commit\n"
    elif [[ "$commit" == feat:* ]] || [[ "$commit" == feat\(*\):* ]]; then
        if [ "$VERSION_BUMP" != "major" ]; then
            VERSION_BUMP="feature"
        fi
        CHANGELOG_ENTRIES="${CHANGELOG_ENTRIES}- ✨ $commit\n"
    elif [[ "$commit" == fix:* ]] || [[ "$commit" == fix\(*\):* ]]; then
        CHANGELOG_ENTRIES="${CHANGELOG_ENTRIES}- 🐛 $commit\n"
    elif [[ "$commit" == perf:* ]] || [[ "$commit" == perf\(*\):* ]]; then
        CHANGELOG_ENTRIES="${CHANGELOG_ENTRIES}- ⚡ $commit\n"
    elif [[ "$commit" == docs:* ]] || [[ "$commit" == docs\(*\):* ]]; then
        CHANGELOG_ENTRIES="${CHANGELOG_ENTRIES}- 📚 $commit\n"
    fi
done <<< "$COMMITS"

# Calculate new version
case "$VERSION_BUMP" in
    "major")
        W=$((W + 1))
        X=0 Y=0 Z=0
        ;;
    "feature")
        Y=$((Y + 1))
        Z=0
        ;;
    *)
        Z=$((Z + 1))
        ;;
esac

NEW_VERSION="v$W.$X.$Y.$Z"
echo -e "New version: ${GREEN}$NEW_VERSION${NC}\n"

# Step 3: Update CHANGELOG.md
echo -e "${YELLOW}Step 3: Updating CHANGELOG.md${NC}"

DATE=$(date +%Y-%m-%d)
NEW_SECTION="## [$NEW_VERSION] - $DATE\n\n${CHANGELOG_ENTRIES}"

if [ -f CHANGELOG.md ]; then
    # Create temp file with new content
    echo -e "$NEW_SECTION" > changelog_new.tmp
    
    # Skip the header and insert new content
    awk 'NR==1 {print; print ""} NR==2 {system("cat changelog_new.tmp"); print ""} NR>1' CHANGELOG.md > changelog_updated.tmp
    
    mv changelog_updated.tmp CHANGELOG.md
    rm changelog_new.tmp
else
    echo -e "# Changelog\n\n$NEW_SECTION" > CHANGELOG.md
fi

echo -e "${GREEN}✓ Updated CHANGELOG.md${NC}"

# Step 3: Update version files
echo -e "${YELLOW}Step 3: Updating version files${NC}"

VERSION_NO_V="${NEW_VERSION:1}"  # Remove 'v' prefix

# Update pyproject.toml if exists
if [ -f pyproject.toml ]; then
    sed -i.bak "s/version = \"[^\"]*\"/version = \"$VERSION_NO_V\"/" pyproject.toml && rm pyproject.toml.bak
    echo -e "${GREEN}✓ Updated pyproject.toml${NC}"
fi

# Update package.json if exists
if [ -f package.json ]; then
    # Use a more robust JSON update
    if command -v jq &> /dev/null; then
        jq ".version = \"$VERSION_NO_V\"" package.json > package.json.tmp && mv package.json.tmp package.json
    else
        sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION_NO_V\"/" package.json && rm package.json.bak
    fi
    echo -e "${GREEN}✓ Updated package.json${NC}"
fi

# Update version.txt if exists
if [ -f version.txt ]; then
    echo "$VERSION_NO_V" > version.txt
    echo -e "${GREEN}✓ Updated version.txt${NC}"
fi

# Step 4: Commit, tag, and push
echo -e "\n${YELLOW}Step 4: Committing and tagging${NC}"

git add -A
git commit -m "chore(release): $NEW_VERSION"
echo -e "${GREEN}✓ Created commit${NC}"

git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"
echo -e "${GREEN}✓ Created tag: $NEW_VERSION${NC}"

git push origin main
git push origin "$NEW_VERSION"
echo -e "${GREEN}✓ Pushed to origin${NC}"

# Step 5: Create GitHub release
echo -e "\n${YELLOW}Step 5: Creating GitHub release${NC}"

if command -v gh &> /dev/null; then
    RELEASE_NOTES="## What's Changed in $NEW_VERSION

$CHANGELOG_ENTRIES"
    
    gh release create "$NEW_VERSION" \
        --title "Release $NEW_VERSION" \
        --notes "$RELEASE_NOTES" \
        --target main
    
    echo -e "${GREEN}✓ Created GitHub release${NC}"
else
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) not found. Please install it to create releases.${NC}"
    echo "   Visit: https://cli.github.com/"
fi

echo -e "\n${GREEN}✅ Release $NEW_VERSION completed successfully!${NC}"
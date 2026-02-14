#!/bin/bash
# Reset script for qutebrowser task: Changelog upgrades filtering

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="${1:-$SCRIPT_DIR/../../qutebrowser}"

cd "$REPO_DIR"

BASE_COMMIT="5ee28105ad972dd635fcdc0ea56e5f82de478fb1"
SOLUTION_COMMIT="f631cd4422744160d9dcf7a0455da532ce973315"

git reset --hard "$BASE_COMMIT"
git clean -fd

git checkout "$SOLUTION_COMMIT" -- \
    tests/unit/config/test_configfiles.py

cat > TASK.md << 'EOF'
# SWE-bench Task: Changelog Display Filtering

## Problem Statement

The application is currently configured to display the changelog after any upgrade, including patch and minor updates. This behavior lacks flexibility and does not allow users to control when the changelog should be shown.

There is no distinction between major, minor, or patch upgrades, so even trivial updates trigger a changelog prompt. Users are repeatedly shown changelogs that may not contain relevant information, leading to unnecessary interruptions.

## Expected behavior

The changelog should appear only after meaningful upgrades (e.g., minor or major releases), and users should be able to configure this behavior using a setting.

## Actual behavior

The changelog appears after all upgrades, including patch-level updates, with no configuration available to limit or disable this behavior.

## Test Files

These tests must pass:
- tests/unit/config/test_configfiles.py

## Run Tests

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen pytest tests/unit/config/test_configfiles.py -v
```
EOF

echo "Task setup complete. See TASK.md"

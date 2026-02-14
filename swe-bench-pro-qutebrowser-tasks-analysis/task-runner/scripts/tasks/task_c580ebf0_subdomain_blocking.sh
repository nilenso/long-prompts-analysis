#!/bin/bash
# Reset script for qutebrowser task: Host blocking subdomains

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="${1:-$SCRIPT_DIR/../../qutebrowser}"

cd "$REPO_DIR"

BASE_COMMIT="0b8cc812fd0b73e296a3f93db02ce5d0b35714fc"
SOLUTION_COMMIT="c580ebf0801e5a3ecabc54f327498bb753c6d5f2"

git reset --hard "$BASE_COMMIT"
git clean -fd

git checkout "$SOLUTION_COMMIT" -- \
    tests/unit/components/test_hostblock.py \
    tests/unit/config/test_configutils.py \
    tests/unit/utils/test_urlutils.py

cat > TASK.md << 'EOF'
# SWE-bench Task: Host Blocking Subdomains

## Problem Statement

Host blocking does not apply to subdomains when only the parent domain is listed.

In the hosts-based blocking method, requests are only blocked if the exact request hostname matches an entry in either the dynamically loaded blocked hosts set or the config-defined blocked hosts. As a result, adding example.com to the blocklist does not block sub.example.com, a.b.example.com, etc.

## Current behavior

With content.blocking.enabled turned on, and example.com present in the blocklist:
- https://example.com is blocked.
- https://sub.example.com and deeper subdomains are NOT blocked.

## Expected behavior

- If a parent domain is blocked, all of its subdomains should also be blocked unless explicitly whitelisted.
- Blocking example.com should block example.com, sub.example.com, and a.b.example.com.
- Whitelist rules should take precedence: if a request URL is whitelisted, it must not be blocked.

## Test Files

These tests must pass:
- tests/unit/components/test_hostblock.py
- tests/unit/config/test_configutils.py
- tests/unit/utils/test_urlutils.py

## Run Tests

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen pytest tests/unit/components/test_hostblock.py tests/unit/utils/test_urlutils.py tests/unit/config/test_configutils.py -v
```
EOF

echo "Task setup complete. See TASK.md"

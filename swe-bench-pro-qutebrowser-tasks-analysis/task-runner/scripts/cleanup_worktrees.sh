#!/bin/bash
# Cleanup all worktrees
# Usage: ./cleanup_worktrees.sh [--force]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKTREES_DIR="$PROJECT_DIR/worktrees"
QUTEBROWSER_DIR="$PROJECT_DIR/qutebrowser"
FORCE="${1:-}"

if [[ ! -d "$WORKTREES_DIR" ]]; then
    echo "No worktrees directory found"
    exit 0
fi

echo "Current worktrees:"
git -C "$QUTEBROWSER_DIR" worktree list
echo ""

if [[ "$FORCE" != "--force" ]]; then
    read -p "Remove all worktrees in $WORKTREES_DIR? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 0
    fi
fi

echo "Removing worktrees..."

# Remove each worktree properly through git
for worktree in "$WORKTREES_DIR"/*/; do
    if [[ -d "$worktree" ]]; then
        echo "Removing: $worktree"
        git -C "$QUTEBROWSER_DIR" worktree remove "$worktree" --force 2>/dev/null || rm -rf "$worktree"
    fi
done

# Prune any stale worktree references
git -C "$QUTEBROWSER_DIR" worktree prune

# Remove command files
rm -f "$WORKTREES_DIR"/run_commands_*.txt

echo ""
echo "Cleanup complete"
echo ""
echo "Remaining worktrees:"
git -C "$QUTEBROWSER_DIR" worktree list

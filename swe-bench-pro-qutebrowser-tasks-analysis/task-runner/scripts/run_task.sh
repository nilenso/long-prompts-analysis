#!/bin/bash
# Run a single task with a single agent in its own worktree
# Usage: ./run_task.sh <task_script> <agent>
#
# Example:
#   ./run_task.sh scripts/tasks/task_c580ebf0_subdomain_blocking.sh opus-claude

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TASK_SCRIPT="${1:-}"
AGENT="${2:-opus-claude}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RANDOM_ID=$(head -c 4 /dev/urandom | xxd -p)

if [[ -z "$TASK_SCRIPT" ]] || [[ -z "$AGENT" ]]; then
    echo "Usage: $0 <task_script> <agent>"
    exit 1
fi

# Resolve task script path
if [[ -f "$PROJECT_DIR/$TASK_SCRIPT" ]]; then
    TASK_SCRIPT="$PROJECT_DIR/$TASK_SCRIPT"
elif [[ ! -f "$TASK_SCRIPT" ]]; then
    echo "Error: Task script not found: $TASK_SCRIPT"
    exit 1
fi

# Parse task script name: task_bf045f7e_search_flags.sh -> id=bf045f7e, name=search-flags
TASK_BASENAME=$(basename "$TASK_SCRIPT" .sh | sed 's/^task_//')
TASK_ID=$(echo "$TASK_BASENAME" | cut -d'_' -f1)
TASK_NAME=$(echo "$TASK_BASENAME" | cut -d'_' -f2- | tr '_' '-')
AGENT_UNDERSCORE=$(echo "$AGENT" | tr '-' '_')
WORKTREES_DIR="$PROJECT_DIR/worktrees"
QUTEBROWSER_DIR="$PROJECT_DIR/qutebrowser"

mkdir -p "$WORKTREES_DIR"

WORKTREE_PATH="$WORKTREES_DIR/${TASK_NAME}_${AGENT}_${TIMESTAMP}_${RANDOM_ID}"
TITLE="${TASK_NAME}_${AGENT}_${TIMESTAMP}_${RANDOM_ID}"

echo "Task: $TASK_NAME"
echo "Agent: $AGENT"
echo "Worktree: $WORKTREE_PATH"
echo "Title: $TITLE"
echo ""

# Create worktree
git -C "$QUTEBROWSER_DIR" worktree add "$WORKTREE_PATH" --detach HEAD 2>/dev/null || {
    git -C "$QUTEBROWSER_DIR" worktree remove "$WORKTREE_PATH" --force 2>/dev/null || true
    git -C "$QUTEBROWSER_DIR" worktree add "$WORKTREE_PATH" --detach HEAD
}

# Reset to task state
bash "$TASK_SCRIPT" "$WORKTREE_PATH" > /dev/null

# Symlink venv
if [[ -d "$QUTEBROWSER_DIR/.venv" ]] && [[ ! -e "$WORKTREE_PATH/.venv" ]]; then
    ln -sf "$QUTEBROWSER_DIR/.venv" "$WORKTREE_PATH/.venv"
fi

# Copy opencode.json and prompt files
if [[ -f "$PROJECT_DIR/opencode.json" ]]; then
    mkdir -p "$WORKTREE_PATH/.opencode-prompts"
    sed 's|{file:prompts/|{file:.opencode-prompts/|g' \
        "$PROJECT_DIR/opencode.json" > "$WORKTREE_PATH/opencode.json"
    for prompt_file in "$PROJECT_DIR/prompts/"*.txt; do
        if [[ -f "$prompt_file" ]]; then
            cp "$prompt_file" "$WORKTREE_PATH/.opencode-prompts/"
        fi
    done
fi

# Export directory
EXPORTS_DIR="$PROJECT_DIR/exports/latest-run"
mkdir -p "$EXPORTS_DIR"

# Run opencode
cd "$WORKTREE_PATH"
OPENCODE_CONFIG_CONTENT='{"permission":{"external_directory":"allow"}}' opencode --agent "$AGENT" run --title "$TITLE" \
    "Read TASK.md for the task description. Fix the code to make all the tests pass. The test files and run command are in TASK.md."

# Export session
echo ""
echo "Exporting session: $TITLE"
SESSION_ID=$(opencode session list --format json | jq -r --arg title "$TITLE" '.[] | select(.title == $title) | .id')
if [[ -z "$SESSION_ID" ]]; then
    echo "Error: Could not find session with title: $TITLE"
    exit 1
fi
EXPORT_FILE="$EXPORTS_DIR/${TASK_NAME}_${AGENT_UNDERSCORE}_${TASK_ID}.json"
opencode export "$SESSION_ID" > "$EXPORT_FILE"
echo "Exported to: $EXPORT_FILE"

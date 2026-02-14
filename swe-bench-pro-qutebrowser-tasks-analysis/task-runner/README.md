# SWE-bench Pro Task Runner

Run 10 qutebrowser SWE-bench Pro tasks across 6 different agent configurations using [opencode](https://opencode.ai).

## Prerequisites

- **opencode** CLI installed (`npm i -g @anthropic/opencode` or equivalent)
- **git** (for worktree management)
- **Python 3.10+** with a virtualenv
- **jq** (for session export)
- API keys set for Anthropic (`ANTHROPIC_API_KEY`) and/or OpenAI (`OPENAI_API_KEY`)

## Setup

```bash
# 1. Clone qutebrowser as a submodule (or place it at ./qutebrowser)
git submodule add https://github.com/qutebrowser/qutebrowser.git qutebrowser
cd qutebrowser && git checkout main && cd ..

# 2. Create a Python virtualenv inside qutebrowser (shared across worktrees)
cd qutebrowser
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[testing]'
cd ..

# 3. Install node dependency (for opencode codex integration)
npm install
```

## How it works

1. Each **task script** (`scripts/tasks/task_*.sh`) resets the qutebrowser repo to a specific base commit, then cherry-picks failing test files from the solution commit. This creates a state where tests fail and the agent must write the fix.

2. `scripts/run_task.sh` creates an isolated **git worktree** for each run, symlinks the shared virtualenv, copies the opencode config + system prompt files, then invokes `opencode` with the chosen agent. After the agent finishes, the session is exported to JSON.

3. The **Makefile** orchestrates everything, allowing single runs, per-task parallel runs, or full 60-run matrix (10 tasks x 6 agents).

## Available agents

| Agent        | Model              | System prompt     |
|--------------|--------------------|-------------------|
| opus-codex   | Claude Opus 4.5    | Codex CLI prompt  |
| opus-claude  | Claude Opus 4.5    | Claude Code prompt|
| gpt-codex    | GPT 5.2            | Codex CLI prompt  |
| gpt-claude   | GPT 5.2            | Claude Code prompt|
| opus-empty   | Claude Opus 4.5    | (none)            |
| gpt-empty    | GPT 5.2            | (none)            |

## Available tasks

| Key             | Description                              |
|-----------------|------------------------------------------|
| subdomain       | Host blocking subdomains                 |
| qt_warning      | Qt warning filtering                     |
| changelog       | Changelog upgrade filtering              |
| parse_duration  | Duration parsing validation              |
| later_units     | Add units to :later command              |
| coord_parsing   | Coordinate string parsing                |
| process_cleanup | Process data cleanup                     |
| close_matches   | Close matches for invalid commands       |
| search_flags    | Search direction flags fix               |
| untrusted_args  | Untrusted CLI arguments handling         |

## Usage

```bash
# Run a single task with a single agent
make run TASK=subdomain AGENT=opus-claude

# Run all 6 agents on one task (parallel)
make run-all-agents TASK=parse_duration

# Run all 10 tasks x 6 agents (60 parallel runs)
make run-all

# List tasks and agents
make list-tasks
make list-agents

# Show worktree status
make status

# Clean up all worktrees
make cleanup
```

## File structure

```
task-runner/
  Makefile                  # Orchestrator
  opencode.json             # Agent definitions (models + system prompts)
  package.json              # Node dependency (@openai/codex)
  .gitmodules               # qutebrowser submodule reference
  prompts/
    anthropic-claude-code_na_2025-11-01.txt   # Claude Code system prompt
    openai-codex-cli_na_2025-09-24.txt        # Codex CLI system prompt
  scripts/
    run_task.sh              # Creates worktree, runs agent, exports session
    cleanup_worktrees.sh     # Removes all worktrees
    tasks/
      task_70248f25_later_units.sh
      task_85b867fe_coord_parsing.sh
      task_8f46ba3f_untrusted_args.sh
      task_96b99780_parse_duration.sh
      task_a84ecfb8_close_matches.sh
      task_bf045f7e_search_flags.sh
      task_c09e1439_process_cleanup.sh
      task_c580ebf0_subdomain_blocking.sh
      task_f631cd44_changelog.sh
      task_f91ace96_qt_warning.sh
```

## Output

Session exports are saved to `exports/latest-run/` as JSON files, named like `<task>_<agent>_<task-id>.json`.

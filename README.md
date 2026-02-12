# Long Prompts Analysis

Data, scripts, and analysis artefacts behind our investigation into the system prompts of terminal-based AI coding agents.

## Repository Index

### `data/`

- **`terminal-cli-coding-agents-system-prompts.csv`** / **`.md`** — Comparison table of system prompts across 12 coding agents (Claude Code, Codex, Gemini CLI, Cursor, Kiro, Kimi, Amp, Aider, OpenHands, Qwen Code, Goose, Copilot). Columns cover line counts, tool definitions, security posture, git guidance, autonomy, and more.
- **`prompts/`** — Raw system prompt files, named `{agent}_{version}_{date}.{ext}`. Includes prompts from leaked-prompt repos and official open-source projects.
  - **`filtered/`** — Cleaned/filtered versions of select prompts used for head-to-head comparisons.
  - **`annotated/`** — Prompts annotated for "weight-fighting" signals (nagging, repetition, prohibitions, emphatic language, etc.) in JSON, Markdown, and plain text formats. Also contains thematic analyses of forceful language patterns.
  - **`paragraphs/`** — Prompts split into numbered paragraph JSON, an intermediate format used as input for annotation.
  - **`viewer.html`** — Interactive HTML viewer for browsing annotated prompts.
- **`transcripts/`** — Exported transcripts of Claude Code solving SWE-Bench tasks under different system prompts (Claude prompt vs Codex prompt).

### `codex-and-claude-system-prompts/`

Tracks how the Claude Code and OpenAI Codex CLI system prompts evolved over time, release by release.

- **`data/claude-code/`** / **`data/codex/`** — Prompt snapshots at every version (`prompts-{version}.txt`).
- **`data/claude-code-model-releases-filtered/`** / **`data/codex-cli-model-releases-filtered/`** — Curated prompt snapshots keyed to major model releases, with human-readable filenames describing what changed.
- **`cc-prompts-tokens.csv`** — Token counts per Claude Code prompt version.
- **`model-releases.csv`** — Timeline of Anthropic and OpenAI model releases.
- **`events/`** — Markdown descriptions of significant model release events with `events.json` index.
- **`generate_release_changes.py`** — Script that diffs prompts across model release boundaries and produces `release-changes.json`.
- **`prompt-evolution-combined.html`** / **`index.html`** — Interactive visualisations of prompt size and content over time.

### `context-viewer-exports/`

JSON exports from the [Context Viewer](https://context.nilenso.com) tool, used for token-level analysis of prompt structure.

- **`system-prompts-session-export.json`** / **`system-prompts-simpler.json`** — Annotated session exports with semantic labels (identity, environment, tools, workflow, etc.) for 6 major agent prompts.
- **`claude-prompt-evolution-export*.json`** / **`codex-prompt-evolution-export*.json`** — Prompt evolution data formatted for the Context Viewer.
- **`swapping-prompts-swe-tasks.json`** — SWE-Bench task runs with different system prompts, including token distributions per phase.
- **`system-prompt-component-colors.json`** / **`system-prompt-component-distribution.json`** — Component taxonomy and token distribution data used for waffle chart visualisations.
- **`context-viewer-analysis.md`** — Annotated export showing per-component token breakdowns for each agent's prompt.

### `swe-bench-pro-qutebrowser-tasks-analysis/`

Analysis of how different system prompts affect agent behaviour on SWE-Bench Pro tasks (qutebrowser subset).

- **`opencode-exports/`** — Raw JSON transcripts from [OpenCode](https://github.com/nicepkg/opencode) runs: 10 tasks x 5 agent configurations (opus/gpt models x empty/codex/claude prompts).
- **`swe-tasks-summary.csv`** — Summary table of all runs (tokens, messages, tool calls, patches, test runs).
- **`swe-tasks-avg.json`** — Averaged metrics per agent configuration.
- **`workflow-patterns-across-agents.md`** — High-level analysis of how prompts shape workflow: opening moves, phase distribution, iteration patterns, verification styles.
- **`gpt-claude-vs-gpt-codex-workflows.md`** / **`opus-claude-vs-opus-codex-workflows.md`** — Head-to-head workflow comparisons holding the model constant while swapping prompts.
- **`swe-tasks-viz.html`** / **`swe-tasks-waffle-avg.html`** — Interactive HTML visualisations.
- **`comparison.jpg`** — Visual comparison of agent workflows.

### `scripts/`

- **`annotate_weight_fighting.py`** — Annotates prompt files for weight-fighting signals (reminders, repetition, prohibitions, emphatic language, threats/pleading, over-constraining).
- **`generate_html_view.py`** — Generates the interactive HTML viewer for annotated prompts.
- **`generate_waffle_avg.py`** — Generates waffle chart HTML showing average token distribution per agent across SWE-Bench tasks.
- **`parse_swe_tasks_csv.py`** — Parses SWE-Bench task JSON into a CSV summary (time, tokens per agent per task).
- **`split_paragraphs.py`** — Splits prompt files into numbered paragraph JSON for annotation input.

### `docs/`

- **`methodology.md`** — How the system prompts were collected: source repos, search strategy, filtering, and metadata extraction.
- **`structure.txt`** — Taxonomy of system prompt components (identity, personality, environment, code_style, search, workflow, project_context, tools) and their sub-categories.
- **`long-prompts.md`** — Extended notes.

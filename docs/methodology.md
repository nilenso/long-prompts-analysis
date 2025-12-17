# Methodology: Collecting Terminal-Based AI Coding Agent System Prompts

## Overview

This document describes the approach used to collect system prompts for terminal-based agentic coding CLI tools from both leaked prompt repositories and official open source projects.

## Data Collection Process

### 1. Source Repository Cloning

Cloned 8 repositories known to contain leaked AI system prompts:
- `system-prompts-and-models-of-ai-tools` (x1xhlol)
- `system_prompts_leaks` (asgeirtj)
- `leaked-system-prompts` (jujumilk3)
- `awesome-ai-system-prompts` (dontriskit)
- `CL4R1T4S` (elder-plinius)
- `cursor-system-prompts` (labac-dev)
- `ai-system-prompt` (thekishandev)
- `L1B3RT4S` (elder-plinius)

### 2. Target Tool Identification

Defined the scope to 12 terminal-based coding CLI tools:
- Anthropic Claude Code
- OpenAI Codex
- Google Gemini CLI
- GitHub Copilot CLI
- Cursor CLI
- Amazon Kiro CLI
- Moonshot Kimi CLI
- Sourcegraph Amp
- Aider
- OpenHands CLI
- Alibaba Qwen Code
- Block Goose

### 3. Search Strategy

**Keyword-based searching** using `grep` with regex patterns:
- Tool-specific patterns: `claude.?code`, `codex`, `gemini.?cli`, `copilot.?cli`, `cursor.?agent`, `kiro`, `kimi.?cli`, `ampcode`, `aider`, `openhands`, `qwen.?code`, `goose`
- Generic patterns: `system.?prompt`, `SYSTEM_PROMPT`

**Directory exploration** to understand repository structures and locate prompt files in expected locations (e.g., `/prompts/`, `/agents/`, tool-specific folders).

### 4. Official Repository Cloning

For open source tools, cloned official repositories with `--depth 1`:
- `github.com/Aider-AI/aider`
- `github.com/All-Hands-AI/OpenHands`
- `github.com/block/goose`
- `github.com/google-gemini/gemini-cli`
- `github.com/MoonshotAI/kimi-cli`
- `github.com/QwenLM/qwen-code`

### 5. File Reading and Cataloging

Read identified prompt files to:
- Extract version numbers (from filenames, file content, or metadata)
- Determine dates (from filenames, content, or inferred from commit context)
- Verify content is actually a system prompt for the target CLI tool

### 6. Data Compilation

Compiled findings into a structured markdown table with:
- Agent/App name
- Version (if available)
- Date (if available)
- Relative file path to source

## Key Findings

- **11 of 12 tools** had system prompts available
- **GitHub Copilot CLI** was the only tool without a dedicated CLI prompt (only Chat prompts found)
- **6 tools** have official open source repositories with current prompts
- Multiple versions/dates available for Claude Code, Codex, Gemini CLI, and Cursor

## Data Validity and Authenticity

### Sources of Uncertainty

1. **Leaked prompts are unverified**: Cannot confirm these match actual production prompts
2. **Dates are often inferred**: From filenames or file metadata, not official release dates
3. **Version numbers are inconsistent**: Some extracted from content, others from filenames, many unavailable
4. **Prompts may be outdated**: Leaked prompts represent snapshots in time; tools update frequently

### Higher Confidence Data

- **Official open source repos**: Aider, OpenHands, Goose, Gemini CLI, Kimi CLI, Qwen Code — these are authoritative
- **Prompts with version numbers**: e.g., Claude Code 0.2.9 includes version in the file

### Lower Confidence Data

- **Prompts from L1B3RT4S**: Repository focuses on jailbreaks; some content may be manipulated
- **Undated/unversioned prompts**: Cannot verify recency or authenticity
- **CL4R1T4S prompts**: Appear to be community-contributed without verification

### Recommendations for Use

1. **Prefer official sources** when available
2. **Cross-reference** leaked prompts with multiple repositories when possible
3. **Treat dates as approximate** unless from official sources
4. **Verify critical details** against current tool behavior before relying on leaked prompts
5. **Note that prompts evolve** — information here represents historical snapshots

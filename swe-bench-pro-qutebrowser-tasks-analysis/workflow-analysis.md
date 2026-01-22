# Analysis: Workflow Differences by Model + System Prompt

## Summary Table Context

| Combination | Characteristics |
|-------------|-----------------|
| **gpt-claude** | GPT model with Claude Code system prompt |
| **gpt-codex** | GPT model with Codex system prompt |
| **opus-claude** | Opus model with Claude Code system prompt |
| **opus-codex** | Opus model with Codex system prompt |

## Metrics Summary

| Model \ Task | subdomain_blocking | qt_warning | changelog |
|--------------|-------------------|------------|-----------|
| **gpt-claude** | 5498 tokens, 93 msgs, 8m0s | 2518 tokens, 70 msgs, 8m0s | 3939 tokens, 70 msgs, 6m5s |
| **gpt-codex** | 1386 tokens, 52 msgs, 5m53s | 1856 tokens, 22 msgs, 1m53s | 2671 tokens, 44 msgs, 3m59s |
| **opus-claude** | 2027 tokens, 62 msgs, 7m34s | 2273 tokens, 36 msgs, 2m38s | 2616 tokens, 42 msgs, 5m12s |
| **opus-codex** | 1349 tokens, 70 msgs, 7m4s | 1084 tokens, 50 msgs, 3m4s | 1261 tokens, 48 msgs, 5m46s |

---

## Key Workflow Differences

### 1. Task Planning & Organization

| Approach | Used By | Example |
|----------|---------|---------|
| Uses `todowrite` tool for task tracking | Claude prompts (gpt-claude, opus-claude) | Creates explicit TODO lists with status tracking |
| No formal task tracking | Codex prompts (gpt-codex, opus-codex) | Proceeds directly to action without creating task lists |

**Observation**: The Claude system prompt encourages structured task management with `todowrite`, adding ~57-114 tokens of overhead but providing visible progress tracking.

---

### 2. Initial Understanding Phase

**Claude Prompt Approach** (more verbose):
```
1. Read TASK.md
2. Read test file
3. Search for function definition (grep)
4. If not found, search broader (grep)
5. Locate module file (glob)
6. Read implementation file
7. Create TODO list
8. Document expected behavior in markdown table
```

**Codex Prompt Approach** (more direct):
```
1. Read TASK.md
2. Run tests immediately to see failures
3. Search for implementation
4. Read relevant file
5. Begin fixing
```

**Token Impact**: Claude prompt workflows use ~200-400 more tokens on analysis before taking action.

---

### 3. Problem-Solving Style

| Style | Claude Prompt | Codex Prompt |
|-------|---------------|--------------|
| **Diagnostic depth** | Deep - documents expected behavior in tables, creates comprehensive docstrings | Shallow - understands requirements but documents less |
| **Explanatory text** | High verbosity with reasoning | Minimal intermediate text |
| **Edit style** | Longer edit blocks with full documentation | Shorter edits focused on implementation |

**Example**: For `parse_duration`, Claude prompts include a 437-token markdown table documenting all test cases before writing code. Codex prompts jump to implementation after ~100 tokens of analysis.

---

### 4. Environment Troubleshooting

All combinations encountered the same environment issue (shared venv pointing to wrong worktree), but handled it differently:

| Combination | Troubleshooting Depth |
|-------------|----------------------|
| **opus-claude** | Most thorough: 30+ bash commands investigating sys.path, editable installs, symlinks |
| **gpt-claude** | Similar thoroughness, but slightly fewer commands |
| **gpt-codex** | Moderate: investigates paths, tries workarounds, but less systematic |
| **opus-codex** | Most efficient: checks path, identifies issue quickly, fewer redundant checks |

---

### 5. Message & Token Efficiency

From the summary table:

| Task | Most Efficient | Least Efficient | Difference |
|------|----------------|-----------------|------------|
| `subdomain_blocking` | opus-codex (1,349 tokens, 70 msgs) | gpt-claude (5,498 tokens, 93 msgs) | 4x token diff |
| `qt_warning` | opus-codex (1,084 tokens, 50 msgs) | gpt-claude (2,518 tokens, 70 msgs) | 2.3x token diff |
| `changelog` | opus-codex (1,261 tokens, 48 msgs) | gpt-claude (3,939 tokens, 70 msgs) | 3.1x token diff |

---

### 6. Tool Selection Patterns

**Claude prompts tend to**:
- Use `todowrite` for progress tracking
- Produce more verbose `TEXT` blocks explaining reasoning
- Create detailed tables/documentation before editing

**Codex prompts tend to**:
- Use `apply_patch` tool (multi-file patches in single call)
- More direct tool calls with less explanatory text
- Labels like `[project_context]`, `[search]` in tool annotations

---

### 7. Code Generation Quality

Both prompt types produce functionally equivalent code. However:

| Aspect | Claude Prompts | Codex Prompts |
|--------|----------------|---------------|
| Docstrings | Comprehensive (80-150 words) | Adequate (30-60 words) |
| Comments | More inline comments | Fewer comments |
| Code structure | Similar quality | Similar quality |

---

## Key Insights

1. **Codex prompt is 2-4x more token-efficient** across all tasks due to:
   - No task tracking overhead
   - Less explanatory text
   - More direct problem-solving

2. **Claude prompt is more "observable"** - creates better audit trails with:
   - TODO lists
   - Behavior documentation
   - Explicit reasoning

3. **Model choice (GPT vs Opus) has smaller impact** than prompt choice:
   - Opus tends slightly faster in time
   - Token usage similar within same prompt type

4. **Environment issues dominate runtime** - all combinations spent significant time on Python path/venv issues rather than actual coding.

---

## Recommendations

- **For cost optimization**: Use Codex-style prompts (2-4x fewer tokens)
- **For auditability/debugging**: Use Claude-style prompts (better documentation trail)
- **For speed**: Model choice matters less than prompt efficiency
- **For complex multi-step tasks**: Claude-style may catch more edge cases due to upfront analysis

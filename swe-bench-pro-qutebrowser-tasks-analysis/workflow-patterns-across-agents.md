# Workflow Patterns Across Agents

## The Setup

- **10 tasks** x **5 agent configs** = 50 runs
- Agents: `opus_empty`, `opus_codex`, `opus_claude`, `gpt_codex`, `gpt_claude`
- 7 GPT runs failed immediately (empty/1-step), leaving 43 meaningful runs

## Pattern 1: Opening Moves Reveal the Prompt

| Agent | Typical First 3 Phases | Character |
|-------|----------------------|-----------|
| **opus_empty** | Understand → Explore → Plan | Read-first, methodical |
| **opus_codex** | Understand → Explore → Search | Read-first, dive into code |
| **opus_claude** | Understand → Plan → Explore | Plan-first, then explore |
| **gpt_codex** | Explore/Verify → Understand → Implement | Action-first, read later |
| **gpt_claude** | Plan → Understand → Verify | Plan immediately, test early |

The **codex prompt** encourages jumping into code and testing early. The **claude prompt** encourages planning first. The **empty prompt** produces the most textbook workflow.

## Pattern 2: Phase Distribution (% of steps)

| Phase | opus_empty | opus_codex | opus_claude | gpt_codex | gpt_claude |
|-------|-----------|-----------|------------|----------|-----------|
| **understand** | ~12% | ~12% | ~12% | ~5% | ~6% |
| **explore** | ~20% | ~25% | ~22% | ~25% | ~34% |
| **analyze** | ~20% | ~20% | ~23% | ~15% | ~15% |
| **plan** | ~10% | ~5% | ~8% | ~2% | ~8% |
| **implement** | ~18% | ~18% | ~18% | ~23% | ~18% |
| **verify** | ~15% | ~15% | ~12% | ~22% | ~14% |

Key takeaways:
- **Opus** agents spend 2x more time in `understand` — they read requirements and tests thoroughly before acting
- **gpt_codex** has the highest `implement` + `verify` share (~45%) — it's the most "code-and-test" oriented
- **gpt_claude** spends the most time in `explore` (34%) — it gets lost browsing the codebase

## Pattern 3: Iteration Styles

This is the most striking difference.

### Opus agents: "Think, then do"

```
Understand → Explore → [Plan] → Implement → Verify → Complete
            (occasional backtrack)
```

- Relatively clean phase progression
- 0 verify→implement backtracks (never goes back to fix after testing!)
- ~9-11 backtracks per run on average

### GPT+Codex: "Brute force loop"

```
Explore → Implement → Verify → Implement → Verify → Implement → Verify...
```

- 25 verify→implement transitions across all runs — classic "code, test, fix, test, fix" loop
- On `coord-parsing`: **67 phases, 30 backtracks, 173 steps** — a marathon of trial and error
- Highest implement percentage of any agent

### GPT+Claude: "Plan then wander"

```
Plan → Understand → Verify(!) → [long exploration] → Implement → Verify → Explore...
```

- Starts with planning and premature verification (testing before implementing)
- Marks tasks "complete" early, then continues working — 2 of 6 runs start with `complete.update-tasks` within the first 4 steps
- Heaviest exploration phase, suggesting it gets disoriented

## Pattern 4: Task Complexity Amplifies Differences

For the **simplest task** (untrusted-args), all Opus agents look nearly identical:

| Agent | Phases | Steps | Backtracks |
|-------|--------|-------|------------|
| opus_empty | 8 | 21 | 2 |
| opus_codex | 8 | 20 | 2 |
| opus_claude | 9 | 32 | 3 |

For a **hard task** (process-cleanup), they diverge dramatically:

| Agent | Phases | Steps | Backtracks |
|-------|--------|-------|------------|
| opus_empty | 64 | 170 | 29 |
| opus_codex | 39 | 81 | 17 |
| opus_claude | 63 | 148 | 28 |
| gpt_codex | 1 (failed) | — | — |
| gpt_claude | 1 (failed) | — | — |

On hard tasks, both GPT agents fail outright while Opus agents at least attempt them (though with significant struggle).

## Pattern 5: Per-Task Side-by-Side

**untrusted-args** — the cleanest comparison:

| Phase | opus_empty | opus_codex | opus_claude |
|-------|-----------|-----------|------------|
| 1 | Understand(5) | Understand(5) | Understand(5) |
| 2 | Explore(4) | Explore(5) | Explore(5) |
| 3 | Plan(2) | Plan(1) | Plan(2) |
| 4 | Explore(1) | Explore(2) | **Implement(3)** |
| 5 | Implement(2) | Plan(1) | **Plan(2)** |
| 6 | Verify(3) | Implement(2) | **Implement(6)** |
| 7 | Complete(3) | Verify(3) | **Plan(2)** |
| 8 | Implement(1) | Complete(1) | Verify(4) |
| 9 | — | — | Complete(3) |

The claude prompt interleaves plan→implement→plan→implement (iterative refinement), while codex and empty go straight through.

## Summary

| Dimension | Codex Prompt | Claude Prompt | Empty Prompt |
|-----------|-------------|---------------|-------------|
| **Strategy** | Code-first, test-verify loop | Plan-first, iterative refinement | Read-understand-plan-do |
| **Planning** | Minimal (~2-5%) | Heavy (~8-10%) | Moderate (~10%) |
| **Error recovery** | Brute force (retry) | Re-plan then retry | Re-explore then retry |
| **On GPT** | Long implement→verify spirals | Wandering exploration | N/A |
| **On Opus** | Lean and direct | Methodical but verbose | Textbook pipeline |
| **Failure mode** | Infinite loops on hard tasks | Gets lost exploring | Over-plans, sometimes stalls |

The system prompt doesn't just change surface behavior — it shapes the fundamental problem-solving strategy. The same model with a codex prompt becomes a "brute force coder" while with a claude prompt it becomes an "architect who iterates."

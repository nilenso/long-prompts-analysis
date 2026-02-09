# Opus + Codex Prompt vs Opus + Claude Prompt

Same model (Opus), different system prompts, across 10 SWE-bench tasks.

## At a Glance

| Metric | opus_codex | opus_claude |
|--------|-----------|------------|
| Total steps (all tasks) | 695 | 720 |
| Step wins | 5/10 | 5/10 |
| Phase wins | 4/10 | 6/10 |
| Backtrack wins | 6/10 | 4/10 |
| Total backtracks | 97 | 103 |
| todowrite calls | 8 | 35 |
| Total plan steps | 40 | 55 |
| Total explore steps | 199 | 189 |
| Total verify steps | 126 | 102 |
| Implements before first verify | 5/10 tasks | 7/10 tasks |

The two agents are remarkably evenly matched on raw output — nearly identical total steps (695 vs 720), with each winning 5 of 10 tasks on step count. The differences are in *how* they work, not how much.

## Planning: Architect vs Improviser

The most visible difference is planning overhead.

**opus_claude** uses `todowrite` 4.4x more (35 calls vs 8). It front-loads planning — 42 of its 55 plan steps are "early" (before any implementation begins). The claude prompt produces an agent that wants to lay out a roadmap before writing code.

**opus_codex** plans minimally and late. When it does plan, it's often mid-implementation — updating a checklist as it goes rather than building one upfront. It prefers to let the code speak.

### Example: untrusted-args

```
opus_codex:  Understand(5) → Explore(5) → Plan(1) → Explore(2) → Plan(1) → Implement(2) → Verify(3) → Complete(1)
opus_claude: Understand(5) → Explore(5) → Plan(2) → Implement(3) → Plan(2) → Implement(6) → Plan(2) → Verify(4) → Complete(3)
```

opus_codex plans once and moves on. opus_claude interleaves plan→implement→plan→implement — three separate planning phases wrapping two implementation bursts. It's iterative refinement: plan a piece, build it, re-plan, build more.

## Exploration: grep vs Read

Both agents explore roughly the same amount (199 vs 189 steps), but their exploration style differs.

**opus_codex** uses `grep` nearly 2x more (19 vs 11 calls). It searches for patterns across the codebase — casting a wide net to find relevant code by keyword.

**opus_claude** favours reading files directly and searching by file name. It navigates the codebase more structurally, following the directory tree rather than searching contents.

This maps to the prompt personalities: the codex prompt encourages pattern-matching and code search, while the claude prompt encourages understanding structure.

## Verification: Test More vs Code More

**opus_codex** runs 24% more verification steps (126 vs 102). It tests earlier and more often — a tighter feedback loop between code and tests.

**opus_claude** implements before verifying in 7/10 tasks (vs 5/10 for codex). It's more confident about its code being correct before running tests. When it does verify, it tends to do so in fewer, larger batches.

### Verification as terminal phase

Both agents end with verification as their final phase in 8/10 tasks — they both know to "leave the tests green." The remaining 2/10 are tasks where the agent ran out of turns or stalled.

## Backtracking: Who Stays on Track

opus_codex backtracks less overall (97 vs 103) and wins on backtracking in 6/10 tasks. Its leaner planning means fewer phase transitions, which means fewer opportunities to regress.

opus_claude's interleaved plan-implement cycles create structural backtracking — going from implement back to plan is technically a backward phase transition, even though it's intentional.

## Per-Task Comparison

### Simple tasks (untrusted-args, close-matches)

Both agents are efficient and similar. The codex variant is slightly leaner:

| Task | opus_codex steps | opus_claude steps | Winner |
|------|-----------------|------------------|--------|
| untrusted-args | 20 | 32 | codex |
| close-matches | 64 | 51 | claude |

### Medium tasks (subdomain-blocking, changelog, parse-duration)

| Task | opus_codex steps | opus_claude steps | Winner |
|------|-----------------|------------------|--------|
| subdomain-blocking | 63 | 78 | codex |
| changelog | 44 | 68 | codex |
| parse-duration | 47 | 67 | codex |

opus_codex is consistently leaner on medium-complexity tasks. Its minimal-planning, grep-heavy approach pays off when the problem is tractable without elaborate strategy.

### Hard tasks (process-cleanup, qt-warning, coord-parsing)

| Task | opus_codex steps | opus_claude steps | Winner |
|------|-----------------|------------------|--------|
| process-cleanup | 81 | 148 | codex |
| qt-warning | 143 | 98 | claude |
| coord-parsing | 77 | 34 | claude |

Here the results diverge. opus_claude's upfront planning pays off on some hard tasks (qt-warning, coord-parsing) where understanding the problem structure matters. But on process-cleanup, its planning becomes over-planning — 63 phase transitions vs codex's 39.

### Ambiguous tasks (later-units, search-flags)

| Task | opus_codex steps | opus_claude steps | Winner |
|------|-----------------|------------------|--------|
| later-units | 84 | 76 | claude |
| search-flags | 72 | 68 | claude |

Slight edge to claude on tasks that benefit from more methodical exploration.

## First Divergence Point

The two agents always share the opening — `Understand` first, followed by either `Explore` or `Plan`. They diverge on average at phase index ~2, meaning after just 2 collapsed phases, they're already on different paths.

The divergence is typically:
- **opus_codex** goes into deeper exploration (grep, search)
- **opus_claude** goes into planning (todowrite)

## Summary

| Dimension | opus_codex | opus_claude |
|-----------|-----------|------------|
| **Personality** | Pragmatic coder | Methodical architect |
| **Planning** | Minimal, late, adaptive | Heavy, early, structured |
| **Exploration** | grep-first (search by pattern) | Read-first (navigate by structure) |
| **Verification** | Early and frequent | Late but confident |
| **Backtracking** | Less (stays on track) | More (intentional iteration) |
| **Best on** | Medium tasks, clear problems | Hard tasks needing structural understanding |
| **Worst on** | Tasks needing upfront strategy | Tasks where planning becomes over-planning |
| **In a sentence** | "Find the code, fix it, test it" | "Understand the problem, plan the fix, iterate" |

The codex prompt produces a leaner, faster agent that excels when the path forward is discoverable through code search. The claude prompt produces a more deliberate agent that excels when the problem requires understanding structure before acting. Neither dominates — they split wins 5/5 on step count across the 10 tasks.

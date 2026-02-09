# GPT + Codex Prompt vs GPT + Claude Prompt

Same model (GPT), different system prompts, across 10 SWE-bench tasks.

## At a Glance

| Metric | gpt_codex | gpt_claude |
|--------|-----------|------------|
| Tasks completed (non-trivial) | 7/10 | 6/10 |
| Shared failures | 3 (close-matches, process-cleanup, untrusted-args) |
| Total steps (succeeded runs) | 631 | 806 |
| Avg steps per succeeded task | 90.1 | 134.3 |
| Step wins (both-succeeded tasks) | 5/6 | 1/6 |
| Total phases (succeeded runs) | 256 | 243 |
| Total backtracks (succeeded runs) | 210 | 201 |
| implement->verify transitions | 55 | 29 |
| verify->implement transitions | 25 | 9 |
| Total implement<->verify loops | 80 | 38 |
| todowrite calls | 15 | 62 |
| Total plan steps | 10 | 42 |
| Total explore steps | 216 (34.2%) | 367 (45.5%) |
| Total verify steps | 127 | 98 |
| Total implement steps | 146 | 116 |
| Verify before first implement | 5/7 tasks | 6/6 tasks |

The GPT model under both prompts is far less reliable than the Opus runs (3 shared failures out of 10 tasks, plus additional partial failures). When it does work, the codex prompt produces a significantly leaner agent -- 76.3 average steps vs 134.3 on the 6 tasks where both succeeded. The codex variant wins on step count in 5 of those 6.

## Reliability: High Failure Rate

Both GPT agents share a distinctive failure mode: reading the requirements, then producing empty or trivially short output. Three tasks failed identically for both prompts:

| Task | gpt_codex | gpt_claude |
|------|-----------|------------|
| close-matches | FAILED (1 step) | FAILED (1 step) |
| process-cleanup | FAILED (1 step) | FAILED (1 step) |
| untrusted-args | FAILED (1 step) | FAILED (1 step) |
| coord-parsing | 173 steps | FAILED (1 step) |

All four failures manifest identically: a single `understand.read-requirements` step, then nothing. This is a model-level failure -- the GPT model reads the issue and then produces no tool calls. The prompt choice makes no difference in these cases.

The codex prompt edges ahead on reliability: 7/10 completed vs 6/10 for claude. The one task where only codex succeeded (coord-parsing) was a 173-step marathon with heavy implement->verify cycling.

Two additional codex runs are questionable completions:
- **subdomain-blocking** (24 steps): never reached implementation, ended in `analyze.check-environment`. Technically ran but accomplished nothing.
- **changelog** (116 steps): implemented code but ended on `analyze.run-tests-diagnostic` without ever reaching `complete`.

If we count "actually completed the task" (reached `complete` or ended with a meaningful terminal state), the effective scores are closer to 5/10 for codex and 6/10 for claude.

## Opening Moves: Both Start with Plan, Then Diverge

Both agents open identically: `understand` -> `plan`. But what comes next reveals the prompt personality.

**gpt_codex** opens `understand(1) -> plan(1) -> ...` with a single plan step, then immediately branches into exploration or verification:

```
codex changelog:       understand(1) -> plan(1) -> understand(4) -> plan(1) -> verify(1) -> ...
codex qt-warning:      understand(1) -> plan(1) -> explore(2) -> understand(2) -> verify(1) -> ...
codex search-flags:    understand(1) -> plan(1) -> explore(1) -> analyze(1) -> explore(1) -> ...
codex parse-duration:  understand(1) -> plan(1) -> understand(2) -> explore(22) -> implement(2) -> ...
```

The codex agent plans once (1 todowrite call), then dives into the codebase. It often runs verification or analysis early -- 5/7 successful tasks have `verify` before the first `implement`.

**gpt_claude** opens `understand(1) -> plan(2) -> ...` with a doubled plan step (two consecutive todowrite calls), then loops back to understand:

```
claude changelog:      understand(1) -> plan(2) -> understand(2) -> plan(2) -> verify(2) -> ...
claude qt-warning:     understand(1) -> plan(2) -> understand(2) -> plan(2) -> verify(2) -> ...
claude search-flags:   understand(1) -> plan(2) -> understand(2) -> plan(2) -> verify(2) -> ...
claude parse-duration: understand(1) -> plan(2) -> understand(2) -> complete(2) -> verify(2) -> ...
```

Every successful gpt_claude run follows the same pattern: `understand -> plan(2) -> understand(2) -> ...`. The claude prompt makes GPT plan twice upfront, re-read requirements, then plan again. Five of six runs then immediately call `verify` or `complete` before any exploration -- a distinctive "check the test suite first" pattern.

## The Early-Complete Anomaly

The gpt_claude agent has a striking quirk: it calls `complete.update-tasks` extremely early, long before the task is actually done.

| Task | First `complete` at step | Total steps | Implement starts at |
|------|--------------------------|-------------|---------------------|
| subdomain-blocking | 6/83 (7%) | 83 | step 58 |
| parse-duration | 6/168 (4%) | 168 | step 13 |
| later-units | 8/170 (5%) | 170 | step 21 |
| search-flags | 10/122 (8%) | 122 | step 51 |
| qt-warning | 20/154 (13%) | 154 | step 33 |
| changelog | 107/109 (98%) | 109 | step 74 |

In 5/6 tasks, gpt_claude calls `complete` within the first 13% of the run -- before any implementation has started. This is the claude system prompt's todowrite mechanism being misused: the GPT model interprets the initial plan-and-task-list creation as "task management" and marks tasks complete prematurely. Only changelog calls `complete` at the appropriate time (step 107 of 109).

gpt_codex never exhibits this pattern. Its `complete` calls only appear at the true end of the workflow.

## Iteration Patterns: Codex Loops, Claude Wanders

**gpt_codex** is a tight implement->verify loop machine. Across all succeeded tasks:

- 55 implement->verify transitions (avg 7.9/task)
- 25 verify->implement transitions (avg 3.6/task)
- 80 total implement<->verify cycles

The codex agent writes a patch, tests it, adjusts, tests again. This is most extreme on coord-parsing (its solo success): 17 implement->verify transitions and 12 verify->implement transitions in a single 173-step run.

**gpt_claude** iterates far less between implement and verify:

- 29 implement->verify transitions (avg 4.8/task)
- 9 verify->implement transitions (avg 1.5/task)
- 38 total implement<->verify cycles

Half the codex rate. Instead of tight loops, gpt_claude interposes exploration between implementation attempts:

```
parse-duration gpt_claude: ... implement(2) -> verify(2) -> explore(2) -> implement(4) -> verify(2) -> explore(12) -> implement(4) -> explore(2) -> ...
```

Where codex would go implement->verify->implement->verify, claude goes implement->verify->explore->implement->verify->explore. The exploration breaks interrupt the feedback loop.

### Per-task implement<->verify cycles (both-succeeded tasks)

| Task | codex impl->verify | codex verify->impl | claude impl->verify | claude verify->impl |
|------|--------------------|--------------------|---------------------|---------------------|
| changelog | 6 | 0 | 2 | 0 |
| later-units | 10 | 5 | 3 | 0 |
| parse-duration | 10 | 3 | 18 | 9 |
| qt-warning | 7 | 5 | 3 | 0 |
| search-flags | 2 | 0 | 3 | 0 |
| subdomain-blocking | 0 | 0 | 0 | 0 |
| **Total** | **35** | **13** | **29** | **9** |

parse-duration is the one task where gpt_claude out-loops codex (18 vs 10 impl->verify transitions). On every other task, codex loops more tightly.

## Planning and Todowrite Usage

gpt_claude uses todowrite 4.1x more than gpt_codex (62 calls vs 15).

| Agent | Total plan steps | todowrite calls | Avg todowrite/task |
|-------|------------------|-----------------|--------------------|
| gpt_codex | 10 | 15 | 2.1 |
| gpt_claude | 42 | 62 | 10.3 |

Every gpt_codex run uses exactly 2 todowrite calls except search-flags (3). The pattern is: one todowrite at the start to create the plan, one at the end to mark complete. The codex prompt makes GPT use planning as bookkeeping, not strategy.

gpt_claude uses 7-11 todowrite calls per task, spread throughout the run. Planning is interleaved with implementation -- the claude prompt makes GPT update its task list as it discovers new information.

## Exploration Depth: Claude Explores Far More

gpt_claude spends 45.5% of its steps exploring, vs 34.2% for gpt_codex.

| Task | codex explore | claude explore |
|------|---------------|----------------|
| changelog | 47/116 (40.5%) | 49/109 (45.0%) |
| later-units | 38/114 (33.3%) | 74/170 (43.5%) |
| parse-duration | 43/105 (41.0%) | 54/168 (32.1%) |
| qt-warning | 21/67 (31.3%) | 70/154 (45.5%) |
| search-flags | 5/32 (15.6%) | 73/122 (59.8%) |
| subdomain-blocking | 12/24 (50.0%) | 47/83 (56.6%) |

The gap is most extreme on search-flags: gpt_claude spends 59.8% of its 122 steps exploring (73 explore steps), while gpt_codex uses only 5 explore steps in a 32-step run. gpt_codex found what it needed quickly and moved to implementation; gpt_claude kept reading and searching.

gpt_claude also uses `delegate-exploration` (11 total calls vs 2 for codex) -- a pattern where the agent dispatches subtasks to explore the codebase. This is the claude prompt's multi-agent exploration style leaking through.

## Analysis Phase: Claude Gets Stuck Diagnosing

gpt_claude spends significantly more time in the `analyze` phase (126 steps vs 88 for codex). This includes `check-environment` and `run-tests-diagnostic` calls.

The worst case is qt-warning, where gpt_claude burns 37 analyze steps (24% of the run) investigating the test environment, compared to 4 for codex. The claude prompt appears to make GPT more cautious about environment issues, leading to analysis paralysis.

## The Doubling Pattern

Both GPT agents show a distinctive step-doubling pattern not seen in Opus runs: consecutive identical steps (e.g., `explore.search-files -> explore.search-files`).

- gpt_codex: 303/631 steps are duplicates (48.0%)
- gpt_claude: 461/806 steps are duplicates (57.2%)

This means roughly half of all GPT tool calls are immediate repeats. The GPT model tends to issue the same tool call twice in succession -- reading the same file twice, running the same search twice. After deduplication, the effective step counts drop to 328 (codex) and 345 (claude), making the two agents much closer in actual distinct work performed.

## Per-Task Side-by-Side (Both Succeeded)

### search-flags (codex: 32 steps, claude: 122 steps)

The starkest efficiency gap. codex: understand, plan, do some quick exploration and environment checking, implement, verify, done. claude: the same task takes 122 steps with 73 explore steps, 4 plan/todowrite phases, and a premature `complete` call at step 10.

```
gpt_codex:  understand(1) -> plan(1) -> explore(1) -> analyze(1) -> explore(1) -> analyze(1) -> understand(2) -> plan(1) -> verify(3) -> analyze(3) -> verify(1) -> analyze(1) -> explore(2) -> understand(1) -> explore(1) -> implement(4) -> verify(1) -> analyze(1) -> implement(2) -> verify(2) -> complete(1)
gpt_claude: understand(1) -> plan(2) -> understand(2) -> plan(2) -> verify(2) -> complete(2) -> explore(12) -> analyze(2) -> ... [30 phases total]
```

### qt-warning (codex: 67 steps, claude: 154 steps)

codex spends 21 steps exploring, then enters a tight 7-cycle implement->verify loop. claude spends 70 steps exploring and 37 analyzing the environment before managing 3 implementation phases.

```
gpt_codex:  ... explore(6) -> implement(2) -> verify(2) -> explore(8) -> implement(2) -> verify(2) -> ... [tight loops]
gpt_claude: ... explore(12) -> implement(4) -> explore(2) -> implement(2) -> plan(2) -> analyze(2) -> explore(2) -> verify(2) -> explore(14) -> analyze(14) -> ... [wandering]
```

### parse-duration (codex: 105 steps, claude: 168 steps)

The one task where gpt_claude's implement<->verify loop count actually exceeds codex's (27 vs 13 transitions). claude spent 168 steps but did iterate more aggressively on patches -- 18 implement->verify transitions. However, it also spent 16 explore steps between iterations that codex skipped.

### later-units (codex: 114 steps, claude: 170 steps)

Both runs are long. codex enters 10 implement->verify cycles and grinds through. claude tries 3 implement->verify cycles, then falls into a long exploration tail -- the final 60+ steps are almost entirely explore/analyze with 12 keyword searches in a row at the end.

### changelog (codex: 116 steps, claude: 109 steps)

The only task where claude wins on step count. codex never reached `complete` (ended on `analyze`), suggesting it ran out of turns. claude completed properly in 109 steps. This is the one case where claude's more methodical approach paid off -- codex's exploration-heavy opening (30 consecutive explore steps) burned too many turns.

### subdomain-blocking (codex: 24 steps, claude: 83 steps)

codex never implemented anything -- 24 steps of exploring and analyzing, ending on `analyze.check-environment`. claude took 83 steps but successfully reached implementation (8 implement steps) and `complete`. Neither run is efficient, but claude at least finished.

## Summary

| Dimension | gpt_codex | gpt_claude |
|-----------|-----------|------------|
| **Personality** | Brute-force looper | Wandering explorer |
| **Reliability** | 7/10 ran, ~5 actually completed | 6/10 ran, 6 completed |
| **Planning** | Minimal (2 todowrite calls/task) | Heavy (10.3 todowrite calls/task) |
| **Opening move** | plan(1), then explore or verify | plan(2), re-understand, then verify or complete |
| **Iteration style** | Tight implement<->verify loops (80 total) | Loose loops with exploration between (38 total) |
| **Exploration** | 34.2% of steps | 45.5% of steps |
| **Verification** | Early and frequent (127 steps) | Early but less frequent (98 steps) |
| **Step efficiency** | 76.3 avg steps (both-succeeded) | 134.3 avg steps (both-succeeded) |
| **Step wins** | 5/6 tasks | 1/6 tasks |
| **Quirks** | Never reaches complete on 2 tasks | Premature complete calls in 5/6 tasks |
| **Best on** | Tasks solvable by iteration (search-flags, qt-warning) | Tasks where exploration depth matters (changelog) |
| **In a sentence** | "Try a fix, test it, try again" | "Read everything, plan extensively, fix eventually" |

The codex prompt produces a leaner, loop-heavy GPT agent that wins on raw efficiency in 5/6 head-to-head comparisons. But it sometimes fails to properly terminate (2 runs end without `complete`). The claude prompt produces a more thorough but dramatically slower agent that spends nearly half its steps exploring. Its distinctive pathology is premature `complete` calls -- the GPT model misinterprets the claude prompt's todowrite mechanism as a signal to mark tasks done before they're started.

Neither prompt overcomes GPT's fundamental reliability problem: 3/10 tasks fail identically regardless of prompt, producing a single step then stopping. The prompt matters for *how* the agent works, but not *whether* it works.

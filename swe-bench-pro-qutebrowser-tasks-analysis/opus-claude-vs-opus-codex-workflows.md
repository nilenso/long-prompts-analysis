# Workflow Comparison: opus-claude vs opus-codex

Both agents use the same underlying model (Claude Opus) but with different system prompts — one from Claude Code ("claude") and one from Codex ("codex"). All 10 tasks have real transcripts for both agents.

## Overview Stats

| Task | Agent | Tokens | Msgs | Tool Calls | Edits | Test Runs |
|------|-------|--------|------|------------|-------|-----------|
| untrusted-args | opus-claude | 9,027 | 26 | 12 | 3 | 1 |
| | opus-codex | 8,329 | 16 | 7 | 1 | 1 |
| subdomain-blocking | opus-claude | 48,099 | 56 | 31 | 4 | 3 |
| | opus-codex | 47,680 | 40 | 23 | 5 | 4 |
| search-flags | opus-claude | 35,391 | 52 | 25 | 1 | 7 |
| | opus-codex | 44,383 | 50 | 25 | 4 | 6 |
| qt-warning | opus-claude | 39,057 | 72 | 38 | 1 | 8 |
| | opus-codex | 57,065 | 100 | 51 | 5 | 17 |
| process-cleanup | opus-claude | 45,565 | 106 | 52 | 8 | 10 |
| | opus-codex | 30,756 | 58 | 28 | 7 | 6 |
| parse-duration | opus-claude | 36,635 | 52 | 25 | 1 | 9 |
| | opus-codex | 40,880 | 34 | 17 | 2 | 8 |
| later-units | opus-claude | 42,629 | 57 | 28 | 2 | 13 |
| | opus-codex | 53,325 | 60 | 30 | 2 | 11 |
| coord-parsing | opus-claude | 40,514 | 24 | 11 | 2 | 2 |
| | opus-codex | 61,310 | 56 | 28 | 3 | 5 |
| close-matches | opus-claude | 28,245 | 36 | 22 | 7 | 1 |
| | opus-codex | 30,828 | 42 | 24 | 4 | 5 |
| changelog | opus-claude | 59,165 | 50 | 24 | 4 | 8 |
| | opus-codex | 48,791 | 30 | 15 | 4 | 5 |
| **TOTAL** | **opus-claude** | **384,327** | **531** | **268** | **33** | **62** |
| | **opus-codex** | **423,347** | **486** | **248** | **37** | **68** |

Note: Neither agent used `apply_patch` — both used the `edit` tool exclusively (Claude Code's native editing tool). This is a key difference from the gpt-based agents, which used `apply_patch` (the Codex-style tool).

---

## Task-by-Task Workflow Comparison

### 1. untrusted-args

**opus-claude** reads TASK.md, reads the test file, reads the source file, sets up a TODO, then makes 3 targeted edits to `qutebrowser.py` (add the flag, implement `_validate_untrusted_args`, wire it into `main()`). Updates TODOs between edits. Runs tests once — all pass. 12 steps total.

**opus-codex** follows an almost identical sequence: reads TASK.md, test, source. But instead of 3 separate edits, it greps for `untrusted-args` first, then makes a **single edit** containing the full implementation. Runs tests once — all pass. 7 steps total.

**Key difference:** Nearly identical workflows. Codex was slightly more concise — one edit vs three — but both agents understood the task fully before editing and got it right on the first try. The simplest task, and both handled it cleanly.

---

### 2. subdomain-blocking

**opus-claude** reads TASK.md, sets a TODO, reads all 3 test files upfront, runs tests (hits conftest import issue), probes the environment, re-runs tests, then reads the key source files (`hostblock.py`, `urlutils.py`, `configutils.py`). Greps for `widened_hostnames`, reasons about where to add it. Makes 4 edits: 2 to `urlutils.py` (add function), 2 to `hostblock.py` (add import + modify `_is_blocked`). Tests pass on the first post-edit run.

**opus-codex** reads TASK.md, reads all 3 test files, then locates the source files with globs before reading them. Runs tests, hits the same import issue, re-runs. Greps for `widened_hostnames`, reads `configutils.py` to understand the existing `_widened_hostnames`. Makes 5 edits: adds function to `urlutils.py`, adds a local `_widened_hostnames` helper to `hostblock.py`, modifies `_is_blocked`. Runs tests twice to confirm. Also adds a back-compat re-read of `urlutils.py` between edits.

**Key difference:** Very similar approaches. Both read all test files before touching code, both traced the `widened_hostnames` function through the codebase. Codex made one more edit because it added a local helper function to `hostblock.py` in addition to the `urlutils` function. Both were methodical.

---

### 3. search-flags

**opus-claude** reads TASK.md, sets a TODO, reads the test file, greps for `_FindFlags` (doesn't exist), finds `webenginetab.py`, reads it. Sets another TODO, makes a **single edit** adding the full `_FindFlags` dataclass. Runs tests — passes. Then spends steps 21-39 (nearly half the session) investigating a **pre-existing unrelated failure** (`test_greasemonkey_undefined_world`): runs multiple `git diff`/`git log` commands to verify it was already failing, re-runs tests in different configurations. Finally confirms the pre-existing failure and reports success.

**opus-codex** follows a similar read-understand-edit pattern: reads TASK.md, test file, greps for search flags, finds `webenginetab.py`. But instead of one big edit, makes **4 separate edits**: adds the dataclass, updates `WebEngineSearch._flags`, updates `_find`, updates `prev_result`/`next_result`. Then also spends significant time investigating the same pre-existing greasemonkey test failure with git commands, re-running tests to confirm.

**Key difference:** Both spent roughly half their effort investigating a pre-existing test failure that wasn't their problem. opus-claude made one surgical edit; opus-codex made four incremental edits. Both used git to verify the failure predated their changes — a thoroughness pattern unique to Opus (the gpt agents never checked git history).

---

### 4. qt-warning

**opus-claude** reads TASK.md, sets TODOs, reads both test files, finds and reads both source files (`qtlog.py`, `log.py`). Runs the tests — most pass. Then enters a **confusion spiral** (steps 14-43): the `hide_qt_warning` function exists in `log.py` but tests import from `qtlog`, and somehow the tests pass anyway. Spends ~15 steps trying to understand *why* tests pass when the function doesn't exist where it's imported from — running probes, checking conftest fixtures, reading fixtures.py. Eventually gives up investigating and just adds the function to `qtlog.py` with a single edit. Then struggles with venv/path issues for several test runs before getting green.

**opus-codex** reads TASK.md, reads both test and source files. Also hits the same confusion — `qtlog.hide_qt_warning` doesn't exist but tests pass. Spends ~20 steps investigating: probes, reads conftest, reads fixtures, tries pytest with `-s` flag (which finally reveals the actual failure). Then makes **5 edits**: adds functions to `qtlog.py`, removes them from `log.py`, updates `qtnetworkdownloads.py` to import from the new location. Hits path issues, clears pycache, eventually gets tests passing. Then spends 10+ steps verifying the pre-existing `test_init_from_config_console` failure with git.

**Key difference:** Both agents got genuinely confused by the same issue (tests passing when they shouldn't have) and spent significant effort investigating. opus-codex went further in the refactoring — actually *moving* the functions from `log.py` to `qtlog.py` and updating downstream imports — while opus-claude just *added* them to `qtlog.py` without removing them from `log.py`. Codex's approach was more thorough but cost substantially more tokens (57K vs 39K) and test runs (17 vs 8).

---

### 5. process-cleanup

**opus-claude** reads TASK.md, sets TODOs, runs tests immediately. Reads `guiprocess.py` and the test file. Then enters a careful **analysis phase** (steps 13-25): 5 consecutive THINK steps reasoning through each failing test case, understanding what `_cleanup_timer`, `_on_cleanup_timeout`, and the process cleanup lifecycle should do. Makes 8 edits incrementally — each one addressing a specific aspect (type annotation, timer init, timer start, cleanup handler). Hits a subtle issue where the installed package differs from the local file; fixes with `pip install -e .`. Then discovers a completion model issue and edits `miscmodels.py` and `pytest.ini`. Tests pass after 10 runs.

**opus-codex** reads TASK.md, runs tests, reads the test file and source. Also reads `test_models.py` and `miscmodels.py` to understand the completion side. Then reads `pytest.ini` to understand the Qt warning config. Makes 7 edits: similar to claude but in a more consolidated sequence, then fixes `miscmodels.py` and `pytest.ini`. Tests pass after 6 runs.

**Key difference:** opus-claude's distinctive feature here was the extended multi-step reasoning phase — 5 THINK blocks in a row, working through each test case mentally before writing code. This "think before you act" approach led to more targeted edits but also more of them (8 vs 7). Codex was leaner but equally thorough in reading comprehension files upfront. Claude's pip-install-editable debugging detour added several steps.

---

### 6. parse-duration

**opus-claude** reads TASK.md, reads the test file, greps for `parse_duration` (doesn't exist), reads `utils.py`. Then hits **test-running difficulties** (steps 10-17): 4 consecutive test run attempts with different path configurations, a pip install to fix the worktree. Uses probes to verify the function works. Eventually makes a **single edit** to `utils.py` — one shot, comprehensive implementation. Gets tests passing.

**opus-codex** reads TASK.md, reads the test file, globs broadly, reads `utils.py`. Makes a **single edit** for the implementation. Then struggles with test running: `pkg_resources` deprecation treated as error. Reads `pytest.ini`, edits it to add a warning ignore. Tests pass.

**Key difference:** Remarkably similar. Both read the tests carefully, wrote the full implementation in a single edit, then fought with test infrastructure. opus-claude spent more time on path/venv issues; opus-codex identified the `pytest.ini` filter warning problem faster. The implementations were both first-try successes.

---

### 7. later-units

**opus-claude** reads TASK.md, reads the test file, finds and reads `utils.py`. Makes a single edit. Then spends steps 7-37 fighting test infrastructure: import path issues, `pkg_resources` deprecation warnings, conftest interference from other worktrees. Reads `conftest.py`, `setup.cfg`, `pytest.ini`. Edits `pytest.ini` to add warning ignore. Then runs tests in various scopes (parse_duration tests, invalid duration tests, hypothesis tests) until all pass. 13 test runs total.

**opus-codex** follows the same read-edit pattern. Makes a single edit. Then also fights test infrastructure: probes the function manually (works), but pytest fails. Discovers the `.venv` is a symlink to a shared venv with qutebrowser installed from a *different* worktree. Fixes with `pip install -e .`. Also edits `pytest.ini` for the warning. 11 test runs.

**Key difference:** Both wrote the implementation in one shot and then spent the majority of their session fighting the test environment. opus-codex found a deeper root cause (the venv symlink pointing to the wrong worktree) while opus-claude worked around it with path manipulation. Both ended up editing `pytest.ini`. The codex session was more token-expensive (53K vs 43K) due to the pip investigation.

---

### 8. coord-parsing

**opus-claude** reads TASK.md, sets a TODO, reads the test file, reads `utils.py`. Reasons about the implementation, makes 2 edits (add import, add function). Runs tests twice — passes. Reads the test file one more time to verify. Done in **11 steps** — the shortest session in the entire dataset.

**opus-codex** reads TASK.md, reads the test file, and also reads `misc.feature` (a BDD feature file referenced in the task). Reads `utils.py`, runs tests, probes the function. Makes 3 edits. Then goes significantly beyond the task scope: greps for `click_element`, reads `misccommands.py` and `browsertab.py`, searches for position filtering patterns, and **edits `misccommands.py`** to add position-based filtering to the `click_element` command. Runs tests twice more. 28 steps.

**Key difference:** The starkest divergence in the dataset. opus-claude did exactly what the tests required — nothing more. opus-codex read the BDD feature file, noticed that `click_element` would benefit from position support, and proactively extended the implementation. This is the only case where one agent did significantly *more* feature work than the other. Claude was minimal (11 steps, 40K tokens); Codex was expansive (28 steps, 61K tokens).

---

### 9. close-matches

**opus-claude** reads TASK.md, reads all 3 test files, reads both source files (`cmdexc.py`, `parser.py`). Reasons about the implementation, sets TODOs. Makes **7 edits** across the two files in a carefully sequenced order: adds `difflib` import, adds `for_cmd` classmethod, adds `EmptyCommandError`, updates `NoSuchCommandError`, then modifies the parser's error handling. Runs tests once — passes (with one pre-existing Qt warning failure). Re-reads both files to verify.

**opus-codex** follows the same read-all-first pattern. Sets TODOs. Makes **4 edits** — more consolidated than Claude's 7. But then spends steps 20-34 investigating the pre-existing Qt warning failure: tries different pytest options (`-p no:qt`), runs `git diff`/`git stash` to test without changes, runs the test in isolation. Eventually confirms it's pre-existing.

**Key difference:** opus-claude made more granular edits (7 vs 4) but accepted the pre-existing failure quickly. opus-codex made fewer edits but spent considerably more effort verifying the pre-existing failure — 5 test runs and 3 git commands. Claude was confident it wasn't their problem; Codex wanted proof.

---

### 10. changelog

**opus-claude** reads TASK.md, reads the test file, finds and reads `configfiles.py`. Runs tests (path issues), fixes with explicit path. Reasons about the implementation across several THINK steps. Makes 4 edits to `configfiles.py`: adds `VersionChange` enum, adds `_determine_version_change` method, updates `StateConfig.__init__`. Then spends steps 29-39 investigating the pre-existing Qt OpenGL test failure: runs multiple test configurations, checks git history. 8 test runs.

**opus-codex** follows the same read-understand-implement pattern. Makes 4 edits to `configfiles.py`. Then runs tests — passes except the same pre-existing failure. Runs a couple more targeted test commands to confirm. Shorter verification phase. 5 test runs.

**Key difference:** Very similar implementations. Both made 4 edits to the same file. The main difference is in the post-implementation phase: opus-claude spent more time verifying the pre-existing failure and ran more tests (8 vs 5). Codex was quicker to accept the pre-existing failure and wrap up.

---

## Summary: Workflow Pattern Differences

| Dimension | opus-claude | opus-codex |
|-----------|-------------|------------|
| **Opening sequence** | `read(TASK.md) → TODO → read(tests) → read(source)` | `read(TASK.md) → THINK → read(tests) → read(source)` |
| **Progress tracking** | Uses `todowrite` consistently (35 total, avg 3.5/task) | Uses `todowrite` sparingly (8 total, only on 3 tasks) |
| **Reasoning style** | Extended THINK chains before editing (e.g., 5 consecutive THINKs in process-cleanup) | Shorter THINK steps, more interspersed with actions |
| **Edit granularity** | More granular: many small, targeted edits (avg 3.3/task) | Slightly more consolidated edits (avg 3.7/task) but with less back-and-forth |
| **Pre-existing failure handling** | Investigates briefly, usually accepts quickly | Investigates thoroughly — uses git history, re-runs without changes, tries isolation |
| **Scope discipline** | Stays tightly within the test requirements | Occasionally expands scope (coord-parsing: added `click_element` position support) |
| **Test run count** | 62 total (avg 6.2/task) | 68 total (avg 6.8/task) |
| **Token efficiency** | 384K total — **10% more efficient** | 423K total |
| **Environmental debugging** | Moderate: some probing, pip installs | Similar: probing, pip installs, but more git verification |

### The fundamental contrast with the gpt agents

Unlike the gpt-claude vs gpt-codex comparison (where the two agents had dramatically different workflows), **opus-claude and opus-codex follow remarkably similar workflows**. Both:

1. **Read comprehensively before editing** — always reading TASK.md, test files, and source files before making changes
2. **Use the `edit` tool exclusively** (never `apply_patch`) — the underlying Opus model's preference overrides both system prompts
3. **Get implementations right in few edits** — typically 1-4 edits per task, with most time spent on test infrastructure
4. **Struggle with the same environmental issues** — venv paths, `pkg_resources` warnings, Qt OpenGL contexts, worktree cross-contamination

The differences are marginal and stylistic:
- **Claude prompt** drives more `todowrite` usage and slightly more upfront reasoning
- **Codex prompt** drives slightly more post-hoc verification (git checks, extra test runs)
- **Claude prompt** keeps scope tighter; **Codex prompt** occasionally encourages going beyond requirements

**The model dominates the prompt.** When Opus is the underlying model, both system prompts produce similar read-reason-edit-test workflows. The system prompt differences that caused dramatic divergence with GPT (broad exploration vs focused patching, investigative vs mechanical) are largely dampened by Opus's consistent problem-solving approach.

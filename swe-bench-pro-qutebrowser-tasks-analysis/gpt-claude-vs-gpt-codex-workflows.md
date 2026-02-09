# Workflow Comparison: gpt-claude vs gpt-codex

## Overview Stats

| Task | Agent | Tokens | Msgs | Tool Calls | Patches | Test Runs |
|------|-------|--------|------|------------|---------|-----------|
| subdomain-blocking | gpt-claude | 63,332 | 83 | 41 | 4 | 3 |
| | gpt-codex | 17,248 | 18 | 10 | 0 | 3 |
| search-flags | gpt-claude | 84,487 | 122 | 60 | 5 | 7 |
| | gpt-codex | 29,010 | 28 | 14 | 3 | 5 |
| qt-warning | gpt-claude | 57,006 | 152 | 76 | 8 | 10 |
| | gpt-codex | 31,062 | 60 | 32 | 7 | 11 |
| parse-duration | gpt-claude | 84,428 | 168 | 83 | 24 | 22 |
| | gpt-codex | 54,535 | 102 | 52 | 13 | 11 |
| later-units | gpt-claude | 91,403 | 166 | 84 | 10 | 7 |
| | gpt-codex | 75,191 | 109 | 57 | 19 | 13 |
| changelog | gpt-claude | 65,445 | 109 | 54 | 7 | 7 |
| | gpt-codex | 44,907 | 104 | 56 | 6 | 8 |

---

## Task-by-Task Workflow Comparison

### 1. subdomain-blocking

**gpt-claude** follows a structured ritual: `TODO → read(TASK.md) → TODO → TEST-RUN`. After the first test run fails, it enters a long environment-probing phase — checking imports, inspecting `__init__.py`, probing `qutebrowser.qt.machinery`, globbing for Qt wrappers, spawning **two subagents** to find the Qt wrapper generator. This entire detour (steps 5-18) is unrelated to the actual host-blocking task. Only at step 24 does it finally read `hostblock.py`. It then reads surrounding files (`configutils.py`, `urlutils.py`), greps for related functions, and applies 4 patches — needing multiple re-reads of `urlutils.py` between patches to fix its own edits.

**gpt-codex** announces a plan in text, spawns a subagent, then re-reads TASK.md itself and runs tests. After seeing results, it immediately greps for the two critical function names (`widened_hostnames`, `_is_blocked`), reads `hostblock.py`, and discovers the fix is **already in place**. Zero patches. Done in 13 steps.

**Key difference:** Claude got lost in an environmental rabbit hole (Qt wrappers) before even looking at the relevant code. Codex went straight to the domain-relevant code.

---

### 2. search-flags

**gpt-claude** does its `TODO → read → TODO → TEST-RUN` ritual, then immediately detours into a **`pkg_resources` rabbit hole** (steps 6-11: four greps for `pkg_resources`, a glob of all `.py` files). It probes Python paths and imports (steps 12-16). Only at step 18 does it spawn a subagent to locate the actual find-flag code. After reading the key files and applying 2 patches (steps 26-27), tests pass for unit tests — but then it **expands scope into end-to-end tests** (steps 29-49): reading `search.feature`, BDD test files, spawning another subagent, investigating webserver fixtures, patching `webserver_sub.py` for cheroot compatibility. Steps 50-60 are more greps that appear to be post-hoc verification.

**gpt-codex** announces its plan, finds TASK.md, reads it, runs the test command (tries 3 times to get the venv/path right), then reads the two key files (`webenginetab.py`, `test_webenginetab.py`). Applies 3 patches to `webenginetab.py` with test runs between each. Done in 17 steps.

**Key difference:** Claude expanded scope far beyond the failing tests (into end-to-end tests, webserver infrastructure). Codex stayed within the boundary of the test file named in TASK.md.

---

### 3. qt-warning

**gpt-claude** does `TODO → read → TODO → TEST-RUN`, struggles to get tests running (4 test attempts, steps 4-9), then reads the relevant source files and applies its first patches at steps 17-20. After a test run fails, it enters a **massive environment-probing spiral** (steps 25-48): grepping for OpenGL/Qt constants, reading `qtargs.py`, probing Qt runtime behaviour with 7 sequential `python -c` experiments, reading `earlyinit.py`, `webenginewidgets.py`, `machinery.py`, `webenginecore.py`. It applies more patches (steps 49-50, 58-59, 73), interleaved with more probing (steps 61-71: another 7 `python -c` experiments). The middle section (steps 25-72) is almost entirely environmental investigation.

**gpt-codex** announces plan, reads TASK.md, runs tests (3 attempts for venv), then goes straight to the test files to understand expectations. Reads `test_qtlog.py` and `test_log.py` first, then the source files `qtlog.py` and `log.py`. From step 15 onward, it enters a tight **patch→test→patch→test** loop on `qtlog.py` and `log.py`. 7 patches, 11 test runs, minimal exploration. No environment probing at all.

**Key difference:** Claude spent ~50 steps probing OpenGL/Qt internals trying to understand *why* warnings occurred. Codex ignored the environment entirely and focused on making the test assertions pass through code changes. Claude's approach was investigative; Codex's was mechanical.

---

### 4. parse-duration

**gpt-claude** does its ritual, runs tests, reads `utils.py`, and patches immediately at step 7 — unusually fast. But the patch doesn't work, and what follows is the longest patch-test spiral in the dataset: steps 7-82 contain **24 patches and 22 test runs**. In between, it investigates `guiprocess.py`, `version.py`, `message.py`, creates a `pkg_resources.py` shim and `sitecustomize.py`. The middle section has many tangential reads (OpenGL, QtWebEngine, GUIProcess) mixed into what should be a string-parsing task. Steps 40-67 are a brutal `PATCH(utils.py) → TEST-RUN` cycle — patching the same file 12+ times in sequence.

**gpt-codex** reads TASK.md, then does an extensive **pre-read phase**: 8 steps of grep/read to understand the codebase before the first patch at step 14. After the first test failure, it reads more context (`machinery.py`, `qt.py`, `conftest.py`, `usertypes.py`), then enters its own patch-test loop — but with a crucial difference: it reads back the file (`read(utils.py)`) between patches more frequently, and uses `grep` to check for related functions before patching. It also creates `sitecustomize.py`, `usercustomize.py`, and modifies `pytest.ini`. 13 patches, 11 test runs.

**Key difference:** Both struggled, but Claude patched before understanding (patch at step 7, only 5 steps after reading the source), leading to 24 iterations. Codex invested in understanding first (8 search steps before first patch), leading to roughly half the iterations.

---

### 5. later-units

**gpt-claude** does `TODO → read → subagent → TODO → TEST-RUN`, reads the 3 key files (`utils.py`, `test_utils.py`, `utilcmds.py`), patches quickly (steps 11-12). After the test fails, it enters the deepest environmental investigation in the entire dataset: steps 14-76 are dominated by **18 `python -c` probes** (testing PyQt5/OpenGL/QtWebEngine behaviour), 18 greps, and reads of `version.py`, `backendproblem.py`, `earlyinit.py`, `stylesheet.py`, `qtutils.py`, `fixtures.py`. It patches `version.py` at step 74 to try to suppress a Qt warning. The actual task (duration parsing + `:later` command) was patched by step 12 — everything after was fighting the test environment.

**gpt-codex** reads TASK.md, does 6 targeted greps (for `later`, `duration`, `parse_duration`), reads tests and source, then patches at step 9. After the first test failure, it enters a patch-test loop — but the loop is split between two concerns: patches to `utils.py` (the actual feature) and patches to `conftest.py`/`pytest.ini` (test environment). Steps 13-58 have 19 patches total: ~8 on `utils.py` and ~11 on `conftest.py`/`pytest.ini`. It never probes Qt/OpenGL at all — it fixes the environment through config changes rather than investigation.

**Key difference:** Claude investigated the environment extensively (18 python probes, 18 greps into Qt internals) but only made 10 patches. Codex never investigated the environment — it just patched config files directly until tests passed (19 patches). Claude tried to *understand* the problem; Codex tried to *make it go away*.

---

### 6. changelog

**gpt-claude** does `TODO → read → TODO → TEST-RUN → TODO`, then enters a long **codebase comprehension phase** (steps 6-37): reads `machinery.py`, globs for directory structures, probes imports, reads `conftest.py`, `qt.py`, `usertypes.py`, `configfiles.py`, `test_configfiles.py`, `configdata.yml`, `utils.py`, `log.py`, `app.py`, `configdata.py`. Greps for `changelog`, `VersionChange`, `changelog_after_upgrade`. This is 32 steps of reading/searching before the first patch at step 38. Then it patches 4 files at once (`configfiles.py`, `configdata.yml`, `app.py`) and iterates to green.

**gpt-codex** announces its plan, spawns a subagent, reads TASK.md, runs the test — and immediately hits a **`machinery.py` import error** it can't resolve. Steps 6-30 are a confused loop: 6 greps for "already imported", 7 globs for `machinery.py` (in different path patterns), listing directories, probing worktrees, checking imports. It creates a `__init__.py` shim and `sitecustomize.py` to work around the import. Only at step 48 does it finally read the actual task-relevant file (`configfiles.py`). Applies 2 patches to the real code, but by its own admission, it "hit two separate issues" and spent most of its time on environmental setup.

**Key difference:** Claude's extensive reading phase was actually productive — it read all the relevant files before patching. Codex got stuck in an environmental loop (machinery.py imports) that consumed most of its budget, leaving it under-prepared for the actual code changes.

---

## Summary: Workflow Pattern Differences

| Dimension | gpt-claude | gpt-codex |
|-----------|-----------|-----------|
| **Opening ritual** | Always `TODO → read(TASK.md) → TODO → TEST-RUN` | Text announcement ("I'll read TASK.md, then...") → `read(TASK.md) → TEST-RUN` |
| **Progress tracking** | `todowrite` used 5x per task as checkpoints | Never uses `todowrite`; progress is implicit |
| **Exploration style** | Broad, deep: reads many tangential files, spawns subagents for discovery, heavy grep usage | Narrow, targeted: reads only files directly referenced by tests, minimal subagent use |
| **Environment handling** | Investigates root causes with `python -c` probes (avg ~8 per task); tries to *understand* Qt/OpenGL issues | Ignores root causes; patches config files (`pytest.ini`, `conftest.py`, `sitecustomize.py`) to *suppress* issues |
| **Patch timing** | Sometimes patches early then iterates heavily (parse-duration: 24 patches); other times reads extensively first (changelog: 32 steps before first patch) | Reads enough to form a hypothesis, patches, tests — more consistent rhythm |
| **Scope creep** | Frequently expands beyond the test scope (end-to-end tests in search-flags, Qt internals in later-units) | Stays within the test scope defined in TASK.md |
| **Failure response** | Reads more files, greps more patterns, probes the runtime — investigative | Patches again with a tweak, re-runs tests — mechanical |
| **Token efficiency** | ~446K total across 6 tasks | ~298K total across 6 tasks (1.5x more efficient) |

The fundamental difference: **gpt-claude tries to understand the full system before and during patching** (broad reads, greps, subagents, runtime probes), while **gpt-codex treats it as a patch-test convergence problem** (read the minimum, patch, test, adjust, repeat). Claude's approach produces deeper understanding but at much higher cost — and that understanding often goes into tangential areas (Qt wrappers, OpenGL contexts) that don't help solve the actual task.

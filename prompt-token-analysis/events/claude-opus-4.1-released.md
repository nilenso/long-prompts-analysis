---
layout: null
---
# Claude Opus 4.1 Released

**Model release date:** 2025-08-05
**Prompt versions:** 1.0.60 (2025-07-24) to 1.0.73 (2025-08-11)
**Token change:** 12,893 to 13,066 (+173 tokens)

## Summary

The Claude Code prompt grew by 173 tokens around the Opus 4.1 launch. The main additions were **background execution support** for Bash (new `run_in_background` parameter, a new `BashOutput` tool for monitoring output, and a new `KillBash` tool for terminating background shells). The `NotebookRead` tool was removed and its functionality was folded into the existing `Read` tool. Several minor cleanups were also made: the conciseness mandate ("answer with fewer than 4 lines") was dropped, the custom slash command routing through Task agent was removed, and the `${PRODUCT_NAME}` template variable was replaced with the literal "Claude Code". The `priority` field was removed from the TodoWrite tool schema. A new `statusline-setup` agent type was added.

## Changes

### Added: Background Bash execution

New `run_in_background` parameter on the Bash tool, plus two new tools:

```diff
+  - You can use the `run_in_background` parameter to run the command in the background, which allows you
+    to continue working while the command runs. You can monitor the output using the Bash tool as it
+    becomes available. Never use `run_in_background` to run 'sleep' as it will return immediately. You do
+    not need to use '&' at the end of the command when using this parameter.
```

New `BashOutput` tool:

```diff
+## BashOutput
+
+- Retrieves output from a running or completed background bash shell
+- Takes a shell_id parameter identifying the shell
+- Always returns only new output since the last check
+- Returns stdout and stderr output along with shell status
+- Supports optional regex filtering to show only lines matching a pattern
+- Use this tool when you need to monitor or check the output of a long-running shell
```

New `KillBash` tool:

```diff
+## KillBash
+
+- Kills a running background bash shell by its ID
+- Takes a shell_id parameter identifying the shell to kill
+- Returns a success or failure status
+- Use this tool when you need to terminate a long-running shell
```

### Removed: NotebookRead tool

The standalone NotebookRead tool was removed. Its functionality was absorbed into the Read tool:

```diff
-## NotebookRead
-
-Reads a Jupyter notebook (.ipynb file) and returns all of the cells with their outputs. Jupyter notebooks
-are interactive documents that combine code, text, and visualizations, commonly used for data analysis and
-scientific computing. The notebook_path parameter must be an absolute path, not a relative path.
```

Read tool updated to handle notebooks directly:

```diff
-- For Jupyter notebooks (.ipynb files), use the NotebookRead instead
++ This tool can read Jupyter notebooks (.ipynb files) and returns all cells with their outputs, combining
+  code, text, and visualizations.
```

### Removed: Conciseness mandate and slash command routing

The hard 4-line answer limit was dropped:

```diff
-You MUST answer concisely with fewer than 4 lines of text (not including tool use or code generation),
- unless user asks for detail.
```

Slash command routing through Task agent removed:

```diff
-- A custom slash command is a prompt that starts with / to run an expanded prompt saved as a Markdown file,
-  like /compact. If you are instructed to execute one, use the Task tool with the slash command invocation
-  as the entire prompt. Slash commands can take arguments; defer to user instructions.
```

Task agent also updated:

```diff
-When to use the Agent tool:
-- When you are instructed to execute custom slash commands. Use the Agent tool with the slash command
-  invocation as the entire prompt.
+
```

### Added: statusline-setup agent

```diff
+ - statusline-setup: Use this agent to configure the user's Claude Code status line setting.
+   (Tools: Read, Edit)
```

### Changed: TodoWrite schema simplified

The `priority` field was removed:

```diff
-          "priority": {
-            "type": "string",
-            "enum": [
-              "high",
-              "medium",
-              "low"
-            ]
-          },
```

### Minor cleanups

Template variable replaced with literal:

```diff
-- If you _still_ need to run `grep`, STOP. ALWAYS USE ripgrep at `rg` first, which all ${PRODUCT_NAME}
-  users have pre-installed.
++ If you _still_ need to run `grep`, STOP. ALWAYS USE ripgrep at `rg` first, which all Claude Code
+  users have pre-installed.
```

Example wording tightened:

```diff
-assistant: [use the ls tool to list the files in the current directory, then read docs/commands...]
+assistant: [runs ls to list the files in the current directory, then read docs/commands...]
```

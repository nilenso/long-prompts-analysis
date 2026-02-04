# Claude Haiku 4.5 Released

**Model release date:** 2025-10-15
**Prompt versions:** 2.0.14 (2025-10-10) to 2.0.22 (2025-10-17)
**Token change:** 12,273 to 12,956 (+683 tokens)

## Summary

The Claude Code prompt grew by 683 tokens around the Haiku 4.5 launch. The two significant additions were the new **Skill tool** (a system for executing specialized skills within conversations, ~43 lines of tool definition) and the new **Explore agent type** (a fast codebase exploration agent with thoroughness levels). The ExitPlanMode tool got improved documentation around handling ambiguity in plans. No sections were removed.

## Changes

### Added: Skill tool

A new tool for executing specialized skills within conversations:

```diff
+## Skill
+
+Execute a skill within the main conversation
+
+<skills_instructions>
+When users ask you to perform tasks, check if any of the available skills below can help complete the
+ task more effectively. Skills provide specialized capabilities and domain knowledge.
+
+How to use skills:
+- Invoke skills using this tool with the skill name only (no arguments)
+- When you invoke a skill, you will see <command-message>The "{name}" skill is loading</command-message>
+- The skill's prompt will expand and provide detailed instructions on how to complete the task
+- Examples:
+  - `command: "pdf"` - invoke the pdf skill
+  - `command: "xlsx"` - invoke the xlsx skill
+  - `command: "ms-office-suite:pdf"` - invoke using fully qualified name
+
+Important:
+- Only use skills listed in <available_skills> below
+- Do not invoke a skill that is already running
+- Do not use this tool for built-in CLI commands (like /help, /clear, etc.)
+</skills_instructions>
```

### Added: Explore agent type

A new specialized agent for fast codebase exploration:

```diff
+- Explore: Fast agent specialized for exploring codebases. Use this when you need to quickly find files
+  by patterns (eg. "src/components/**/*.tsx"), search code for keywords (eg. "API endpoints"), or answer
+  questions about the codebase (eg. "how do API endpoints work?"). When calling this agent, specify the
+  desired thoroughness level: "quick" for basic searches, "medium" for moderate exploration, or "very
+  thorough" for comprehensive analysis across multiple locations and naming conventions.
+  (Tools: Glob, Grep, Read, Bash)
```

### Added: Tool usage directive for Explore agent

A new critical directive was added to the tool usage policy to route codebase exploration through the Explore agent:

```diff
+- VERY IMPORTANT: When exploring the codebase to gather context or to answer a question that is not a
+  needle query for a specific file/class/function, it is CRITICAL that you use the Task tool with
+  subagent_type=Explore instead of running search commands directly.
+<example>
+user: Where are errors from the client handled?
+assistant: [Uses the Task tool with subagent_type=Explore to find the files that handle client errors
+ instead of using Glob or Grep directly]
+</example>
+<example>
+user: What is the codebase structure?
+assistant: [Uses the Task tool with subagent_type=Explore]
+</example>
```

### Changed: ExitPlanMode improved ambiguity handling

The ExitPlanMode tool documentation was expanded with a new section on handling ambiguity:

```diff
-Eg.
+#### Handling Ambiguity in Plans
+Before using this tool, ensure your plan is clear and unambiguous. If there are multiple valid
+ approaches or unclear requirements:
+1. Use the AskUserQuestion tool to clarify with the user
+2. Ask about specific implementation choices (e.g., architectural patterns, which library to use)
+3. Clarify any assumptions that could affect the implementation
+4. Only proceed with ExitPlanMode after resolving ambiguities
+
+
+#### Examples
+
 1. Initial task: "Search for and understand the implementation of vim mode in the codebase" -
    Do not use the exit plan mode tool because you are not planning the implementation steps of a task.
 2. Initial task: "Help me implement yank mode for vim" - Use the exit plan mode tool after you have
    finished planning the implementation steps of the task.
+3. Initial task: "Add a new feature to handle user authentication" - If unsure about auth method
+   (OAuth, JWT, etc.), use AskUserQuestion first, then use exit plan mode tool after clarifying
+   the approach.
```

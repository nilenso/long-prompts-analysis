# Terminal-Based Agentic Coding CLI Tools - System Prompts Collection

This document catalogs system prompts from various terminal-based agentic coding CLI tools gathered from leaked prompts repositories and official open source repositories.

## Metadata Field Definitions

| Field           | Description                                               |
|-----------------|-----------------------------------------------------------|
| **Model**       | Specific model(s) mentioned in the prompt                 |
| **Lines**       | Line count (via wc -l)                                    |
| **Tools**       | Whether formal tool definitions with schemas are included |
| **Examples**    | Whether worked examples are provided                      |
| **Security**    | Explicit security guidelines present                      |
| **Planning**    | Todo/plan management features                             |
| **Git**         | Version control guidance                                  |
| **Sandbox**     | Sandbox/permission handling                               |
| **Tone**        | Communication guidelines                                  |
| **Sub-agents**  | Can delegate to specialized agents                        |
| **Instr Files** | Recognizes AGENTS.md or similar project files             |
| **Autonomy**    | How autonomous vs interactive                             |

## Summary Table

| Agent/App                         | Version | Date       | Source Path                                                                          | Model                 | Lines | Tools                      | Examples               | Security                 | Planning                 | Git                     | Sandbox                  | Tone                      | Sub-agents              | Instr Files            | Autonomy               |
|-----------------------------------|---------|------------|--------------------------------------------------------------------------------------|-----------------------|-------|----------------------------|------------------------|--------------------------|--------------------------|-------------------------|--------------------------|---------------------------|-------------------------|------------------------|------------------------|
| Anthropic Claude Code             | 0.2.9   | 2025-05-24 | system_prompts_leaks/Anthropic/claude-code.md                                        | Sonnet (implied)      | 666   | JSON Schema, 12+ tools     | task execution flows   | OWASP top 10, secrets    | TodoWrite with status    | commit/PR workflows     | permission modes         | concise, no emojis        | Task tool delegation    | -                      | complete tasks fully   |
| Anthropic Claude Code             | -       | 2025-11-01 | system_prompts_leaks/Anthropic/claude-code-2025-11-1.md                              | Haiku 4.5, Sonnet 4.5 | 138   | JSON Schema, 15+ tools     | multiple task examples | security testing rules   | TodoWrite with status    | detailed commit/PR      | multiple sandbox modes   | professional, direct      | Explore, Plan agents    | -                      | complete tasks fully   |
| Anthropic Claude Code             | -       | 2024-03-04 | CL4R1T4S/ANTHROPIC/Claude_Code_03-04-24.md                                           | -                     | 50    | tool names only            | -                      | basic rules section      | -                        | -                       | -                        | brief guidelines          | -                       | -                      | moderate interaction   |
| Anthropic Claude Code (Tools)     | -       | -          | system_prompts_leaks/Anthropic/calude_code_cli_tools.md                              | Sonnet 4.5            | 1396  | extensive JSON schemas     | detailed tool examples | OWASP, secrets handling  | TodoWrite tool           | commit message format   | approval modes           | GitHub markdown           | subagent_type parameter | -                      | complete tasks fully   |
| Anthropic Claude Code (Tools JS)  | -       | -          | awesome-ai-system-prompts/Claude-Code/                                               | -                     | 12    | JS tool definitions        | -                      | -                        | -                        | -                       | -                        | -                         | -                       | -                      | -                      |
| OpenAI Codex CLI                  | -       | 2025-09-24 | system_prompts_leaks/OpenAI/codex-cli.md                                             | ChatGPT               | 419   | shell, plan, view_image    | preamble, plan quality | sandbox, approval flows  | update_plan with steps   | git log/blame guidance  | read-only to full-access | concise, direct, friendly | -                       | AGENTS.md spec         | configurable via modes |
| OpenAI Codex                      | -       | -          | CL4R1T4S/OPENAI/Codex.md                                                             | ChatGPT               | 90    | container namespace        | -                      | -                        | -                        | basic commit rules      | container-based          | -                         | -                       | AGENTS.md spec         | moderate interaction   |
| OpenAI Codex                      | -       | 2025-09-15 | CL4R1T4S/OPENAI/Codex_Sep-15-2025.md                                                 | ChatGPT               | 183   | container + browser        | final answer format    | -                        | -                        | PR guidelines           | container-based          | code style guidelines     | -                       | AGENTS.md spec         | moderate interaction   |
| Google Gemini CLI                 | -       | 2025-06-26 | leaked-system-prompts/google-gemini-cli_20250626.md                                  | Gemini                | 207   | tool name references       | workflow examples      | explain critical cmds    | TodoWrite tool           | git workflow section    | sandbox detection        | minimal output, no chat   | -                       | -                      | complete tasks fully   |
| Google Gemini CLI                 | -       | -          | system_prompts_leaks/Google/Gemini-cli system prompt.md                              | Gemini                | 175   | tool name references       | workflow examples      | security first           | TodoWrite tool           | git workflow section    | sandbox awareness        | concise CLI tone          | -                       | -                      | complete tasks fully   |
| Google Gemini CLI (Official)      | latest  | current    | gemini-cli/packages/core/src/core/prompts.ts                                         | Gemini                | 453   | ToolNames variables        | extensive workflows    | explain critical cmds    | TodoWrite tool           | detailed git section    | macOS Seatbelt detection | concise, no chitchat      | Task delegation         | -                      | complete tasks fully   |
| GitHub Copilot Chat               | -       | 2024-09-30 | leaked-system-prompts/github-copilot-chat_20240930.md                                | -                     | 102   | -                          | -                      | -                        | -                        | -                       | -                        | -                         | -                       | -                      | -                      |
| GitHub Copilot Chat               | -       | 2023-05-13 | leaked-system-prompts/github-copilot-chat_20230513.md                                | -                     | 49    | -                          | -                      | -                        | -                        | -                       | -                        | -                         | -                       | -                      | -                      |
| Cursor Agent CLI                  | -       | 2025-08-07 | system-prompts-and-models-of-ai-tools/Cursor Prompts/Agent CLI Prompt 2025-08-07.txt | GPT-5                 | 206   | JSON Schema tools          | tool call examples     | trust boundary rules     | -                        | -                       | -                        | markdown, status updates  | -                       | -                      | complete tasks fully   |
| Cursor Agent                      | 2.0     | -          | system-prompts-and-models-of-ai-tools/Cursor Prompts/Agent Prompt 2.0.txt            | GPT-4.1               | 772   | extensive JSON schemas     | code change examples   | trust boundary rules     | -                        | -                       | -                        | communication guidelines  | -                       | -                      | proactive tool use     |
| Cursor Agent                      | -       | 2025-09-03 | system-prompts-and-models-of-ai-tools/Cursor Prompts/Agent Prompt 2025-09-03.txt     | -                     | 229   | JSON Schema tools          | tool examples          | security guidelines      | -                        | -                       | -                        | status updates            | -                       | -                      | complete tasks fully   |
| Cursor Agent                      | 1.0     | -          | system-prompts-and-models-of-ai-tools/Cursor Prompts/Agent Prompt v1.0.txt           | -                     | 83    | JSON Schema tools          | basic examples         | security guidelines      | -                        | -                       | -                        | concise output            | -                       | -                      | complete tasks fully   |
| Cursor Agent                      | 1.2     | -          | system-prompts-and-models-of-ai-tools/Cursor Prompts/Agent Prompt v1.2.txt           | -                     | 568   | JSON Schema tools          | tool examples          | security guidelines      | -                        | -                       | -                        | concise output            | -                       | -                      | complete tasks fully   |
| Cursor Agent (Tools)              | 1.0     | -          | system-prompts-and-models-of-ai-tools/Cursor Prompts/Agent Tools v1.0.json           | -                     | 326   | JSON tool definitions      | -                      | -                        | -                        | -                       | -                        | -                         | -                       | -                      | -                      |
| Cursor Agent                      | -       | -          | awesome-ai-system-prompts/Cursor/Agent.md                                            | -                     | 567   | tool definitions           | -                      | -                        | -                        | -                       | -                        | -                         | -                       | -                      | -                      |
| Cursor                            | 2.0     | -          | CL4R1T4S/CURSOR/Cursor_2.0_Sys_Prompt.txt                                            | -                     | 432   | JSON Schema tools          | code examples          | security guidelines      | -                        | -                       | -                        | status updates            | -                       | -                      | complete tasks fully   |
| Cursor                            | -       | -          | CL4R1T4S/CURSOR/Cursor_Prompt.md                                                     | -                     | 54    | JSON Schema tools          | basic examples         | security guidelines      | -                        | -                       | -                        | concise output            | -                       | -                      | complete tasks fully   |
| Cursor (Claude 3.7 Sonnet)        | -       | -          | cursor-system-prompts/Claude_3.7_Sonnet.txt                                          | Claude 3.7 Sonnet     | 107   | JSON Schema tools          | tool examples          | security guidelines      | -                        | -                       | -                        | status updates            | -                       | -                      | complete tasks fully   |
| Amazon Kiro (Spec Mode)           | -       | -          | system-prompts-and-models-of-ai-tools/Kiro/Spec_Prompt.txt                           | -                     | 514   | tool definitions           | spec writing examples  | -                        | structured spec workflow | -                       | -                        | specification focus       | -                       | -                      | spec-focused workflow  |
| Amazon Kiro (Vibe Mode)           | -       | -          | system-prompts-and-models-of-ai-tools/Kiro/Vibe_Prompt.txt                           | -                     | 195   | tool definitions           | coding examples        | -                        | -                        | -                       | -                        | autonomous coding         | -                       | -                      | autonomous "vibe" mode |
| Amazon Kiro (Mode Classifier)     | -       | -          | system-prompts-and-models-of-ai-tools/Kiro/Mode_Clasifier_Prompt.txt                 | -                     | 63    | -                          | -                      | -                        | -                        | -                       | -                        | -                         | -                       | -                      | classifier only        |
| Moonshot Kimi CLI (Official)      | latest  | current    | kimi-cli/src/kimi_cli/agents/default/system.md                                       | -                     | 72    | tool name references       | workflow examples      | security guidelines      | planning features        | git guidance            | sandbox aware            | concise CLI style         | -                       | -                      | complete tasks fully   |
| Moonshot Kimi                     | -       | 2025-07-11 | CL4R1T4S/MOONSHOT/Kimi_2_July-11-2025.txt                                            | -                     | 22    | tool references            | workflow examples      | security guidelines      | planning features        | git guidance            | sandbox aware            | concise style             | -                       | -                      | complete tasks fully   |
| Sourcegraph Amp (Claude 4 Sonnet) | -       | -          | system-prompts-and-models-of-ai-tools/Amp/claude-4-sonnet.yaml                       | Claude 4 Sonnet       | 2174  | extensive YAML definitions | detailed examples      | comprehensive rules      | task planning            | git workflows           | permission handling      | detailed guidelines       | -                       | -                      | complete tasks fully   |
| Sourcegraph Amp (GPT-5)           | -       | -          | system-prompts-and-models-of-ai-tools/Amp/gpt-5.yaml                                 | GPT-5                 | 1999  | extensive YAML definitions | detailed examples      | comprehensive rules      | task planning            | git workflows           | permission handling      | detailed guidelines       | -                       | -                      | complete tasks fully   |
| Aider (Official)                  | latest  | current    | aider/aider/coders/base_prompts.py                                                   | Model-agnostic        | 60    | -                          | -                      | -                        | -                        | commit message gen      | -                        | lazy/overeager modifiers  | -                       | -                      | moderate, user-driven  |
| Aider (Official)                  | latest  | current    | aider/aider/prompts.py                                                               | Model-agnostic        | 61    | -                          | -                      | -                        | -                        | conventional commits    | -                        | -                         | -                       | -                      | moderate, user-driven  |
| OpenHands (Official)              | latest  | current    | OpenHands/openhands/agenthub/codeact_agent/prompts/system_prompt.j2                  | Model-agnostic        | 113   | Jinja2 injected            | -                      | security risk assessment | -                        | version control section | -                        | efficiency focus          | -                       | -                      | complete tasks fully   |
| OpenHands Interactive (Official)  | latest  | current    | OpenHands/openhands/agenthub/codeact_agent/prompts/system_prompt_interactive.j2      | Model-agnostic        | 14    | Jinja2 injected            | -                      | security risk assessment | -                        | Co-authored-by format   | -                        | minimal changes           | -                       | -                      | complete tasks fully   |
| Alibaba Qwen Code (Official)      | latest  | current    | qwen-code/packages/core/src/core/prompts.ts                                          | Qwen-coder, Qwen-vl   | 855   | ToolNames references       | model-specific formats | explain critical cmds    | TodoWrite tool           | detailed git section    | macOS Seatbelt, generic  | concise, no chitchat      | Task delegation         | -                      | complete tasks fully   |
| Block Goose (Official)            | latest  | current    | goose/crates/goose/src/prompts/desktop_prompt.md                                     | Model-agnostic        | 13    | -                          | -                      | -                        | -                        | -                       | -                        | markdown support          | subagents_enabled flag  | GOOSE_HINTS, AGENTS_MD | configurable Auto/Chat |
| Block Goose (Official)            | latest  | current    | goose/crates/goose/src/agents/prompt_manager.rs                                      | Model-agnostic        | 400   | extension system           | -                      | -                        | -                        | -                       | -                        | -                         | subagents_enabled flag  | hint file loading      | configurable GooseMode |

---

## Special Features & Notes

| Agent/App             | Special Features                                                                                      |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| OpenAI Codex CLI      | "Oververbosity" (1-10 scale), "Juice" parameter, channels (analysis/commentary/final), AGENTS.md spec |
| OpenAI Codex (Sep-15) | Browser automation (Playwright), screenshot instructions, "Juice: 240"                                |
| Google Gemini CLI     | Dynamic sandbox detection (macOS Seatbelt), compression prompt for history, plan mode                 |
| Cursor Agent 2.0      | Parallel tool calls emphasis, codebase search optimization, proactive tool use                        |
| Amazon Kiro           | Spec vs Vibe mode separation, specification-driven development                                        |
| Alibaba Qwen Code     | Model-specific tool call formats, compression prompt, plan mode, memory tool                          |
| Block Goose           | Extension-based architecture, dynamic prompt building, hint file loading (GOOSE_HINTS, AGENTS_MD)     |
| Aider                 | Modular prompt system, lazy_prompt/overeager_prompt modifiers, repo map handling                      |
| OpenHands             | Jinja2 templating, structured XML sections, troubleshooting workflow                                  |
| Sourcegraph Amp       | YAML-based configuration, very detailed tool descriptions (~2000+ lines)                              |

---

## Comparative Analysis

### Common Patterns Across All CLI Agents

1. **Tool Definitions**: All mature agents include formal tool schemas (JSON Schema or equivalent)
2. **Git Integration**: Most include git commit/PR workflow guidance
3. **Tone Guidelines**: Emphasis on conciseness appropriate for CLI environments
4. **Security Awareness**: Most include some form of security rules
5. **Autonomy**: Modern agents emphasize completing tasks fully without stopping

### Evolution Patterns Observed

| Feature           | Early (2024)  | Mid (2025)     | Late (2025)                   |
|-------------------|---------------|----------------|-------------------------------|
| Tool Schemas      | Minimal       | Comprehensive  | Extensive with examples       |
| Task Planning     | Absent        | Basic todo     | Full planning with status     |
| Sub-agents        | Absent        | Absent         | Common (Claude, Gemini, Qwen) |
| Sandbox Modes     | Basic         | Multiple modes | Granular permissions          |
| Instruction Files | Absent        | AGENTS.md      | AGENTS.md + custom hints      |
| Examples          | Minimal       | Present        | Extensive with quality tiers  |

### Prompt Length Analysis

Prompt length varies dramatically based on **architectural choices**, not just temporal evolution:

| Category | Lines | Examples |
|----------|-------|----------|
| **Base prompts only** | 13-138 | Goose desktop (13), Kimi leaked (22), Claude Code 2024-03 (50), OpenHands interactive (14) |
| **With tool references** | 175-453 | Gemini CLI leaked (175-207), Codex Sep-15 (183), Gemini CLI official (453) |
| **With embedded tool schemas** | 568-2174 | Cursor 1.2 (568), Claude Code v0.2.9 (666), Cursor 2.0 (772), Qwen Code (855), Claude Code Tools (1396), Amp GPT-5 (1999), Amp Claude 4 (2174) |

**Key findings:**
- **Shortest prompts** are from modular systems where tools are injected separately (OpenHands Jinja2: 14 lines, Goose extensions: 13 lines)
- **Longest prompts** embed complete JSON Schema tool definitions inline (Amp: ~2000 lines)
- **Official open-source tools** tend toward shorter, modular prompts (Aider: 60, Kimi: 72, OpenHands: 113)
- **Leaked "complete" prompts** include everything bundled together (Claude Code Tools: 1396, Amp: 2000+)
- **Date is not the primary factor** — Claude Code Nov 2025 (138 lines) is shorter than Claude Code May 2025 (666 lines) because they capture different components

### Model-Specific Observations

| Vendor      | Model Mentioned            | Notable Features                           |
|-------------|----------------------------|--------------------------------------------|
| Anthropic   | Haiku 4.5, Sonnet 4.5      | Sub-agent delegation, TodoWrite            |
| OpenAI      | ChatGPT, GPT-4.1, GPT-5    | AGENTS.md spec, Juice/Oververbosity params |
| Google      | Gemini                     | Sandbox detection, plan mode               |
| Alibaba     | Qwen-coder, Qwen-vl        | Model-specific tool call formats           |
| Cursor      | GPT-4.1, GPT-5, Claude 3.7 | Parallel tool calls emphasis               |
| Sourcegraph | Claude 4 Sonnet, GPT-5     | YAML config, extensive tooling             |

### Unique Features by Tool

| Tool       | Unique Feature                         |
|------------|----------------------------------------|
| Codex      | "Juice" and "Oververbosity" parameters |
| Gemini CLI | Dynamic sandbox detection              |
| Kiro       | Spec vs Vibe mode separation           |
| Qwen Code  | Model-specific prompt formatting       |
| Goose      | Extension-based architecture           |
| Aider      | Lazy/overeager prompt modifiers        |
| OpenHands  | Jinja2 templating system               |

---

## Notes

### GitHub Copilot CLI
- No dedicated CLI-specific system prompt was found in the leaked repositories
- The available prompts are for GitHub Copilot Chat (IDE integration), not a standalone CLI tool
- GitHub Copilot CLI (`gh copilot`) may use different prompts that haven't been leaked

### Official Open Source Tools
The following tools have their system prompts available in their official open source repositories:
- **Aider**: https://github.com/Aider-AI/aider
- **OpenHands**: https://github.com/All-Hands-AI/OpenHands
- **Block Goose**: https://github.com/block/goose
- **Gemini CLI**: https://github.com/google-gemini/gemini-cli
- **Kimi CLI**: https://github.com/MoonshotAI/kimi-cli
- **Qwen Code**: https://github.com/QwenLM/qwen-code

### Source Repositories
Leaked prompts were gathered from:
- `system_prompts_leaks` - https://github.com/asgeirtj/system_prompts_leaks
- `leaked-system-prompts` - https://github.com/jujumilk3/leaked-system-prompts
- `CL4R1T4S` - https://github.com/elder-plinius/CL4R1T4S
- `system-prompts-and-models-of-ai-tools` - https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools
- `awesome-ai-system-prompts` - https://github.com/dontriskit/awesome-ai-system-prompts
- `cursor-system-prompts` - https://github.com/labac-dev/cursor-system-prompts
- `ai-system-prompt` - https://github.com/thekishandev/ai-system-prompt
- `L1B3RT4S` - https://github.com/elder-plinius/L1B3RT4S

## Coverage Summary

| Tool                  | Found   | Source Type              |
|-----------------------|---------|--------------------------|
| Anthropic Claude Code | Yes     | Leaked                   |
| OpenAI Codex          | Yes     | Leaked                   |
| Google Gemini CLI     | Yes     | Both (Leaked + Official) |
| GitHub Copilot CLI    | Partial | Only Chat prompts found  |
| Cursor CLI            | Yes     | Leaked                   |
| Amazon Kiro CLI       | Yes     | Leaked                   |
| Moonshot Kimi CLI     | Yes     | Both (Leaked + Official) |
| Sourcegraph Amp       | Yes     | Leaked                   |
| Aider                 | Yes     | Official                 |
| OpenHands CLI         | Yes     | Official                 |
| Alibaba Qwen Code     | Yes     | Official                 |
| Block Goose           | Yes     | Official                 |

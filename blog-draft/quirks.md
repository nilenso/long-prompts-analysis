# Interesting quirks in system prompts of coding agents

System prompts often expose a system’s engineering scars. Much like the small hacks that accumulate in a codebase to handle edge cases, bugs, or behavioral quirks, a model’s undesirable behaviors are frequently addressed with simple, corrective instructions in the system prompt. Over time, those fixes pile up, leaving a legacy prompt dotted with idiosyncratic patches. When someone new encounters it, they form conjectures around what underlying behaviour patch was trying to fix.

I’m going to walk through a few of these peculiar system-prompt patches in some coding agents and offer some conjectures about the underlying model behaviors they’re meant to address.

---

> IMPORTANT: You must NEVER generate or guess URLs for the user unless you are confident that the URLs are for helping the user with programming.
>
>
> *[Claude Code](https://github.com/Piebald-AI/claude-code-system-prompts/blob/7843e6a/system-prompts/system-prompt-main-system-prompt.md?plain=1#L29)*
>

This instruction sits at the very top of the prompt and is flagged as IMPORTANT in all caps, which suggests it’s pushing against a strong learned tendency to invent links. It might be a holdover from before Claude Code had built-in web search, but the fact that it remains hints that link hallucination is persistent even in the current setup.

Allowing URL guesses when they help with programming also implies that the main problem shows up outside programming, where “plausible” links are less standardized and mistakes are costlier. Safety is an obvious motive, though the prompt already contains other risk mitigations, so this may be aimed less at overt abuse and more at epistemics. The model may have learned that including citation-style links boosts perceived credibility, and is therefore biased toward generating them.

---

> Refer to code changes as "edits" not "patches".
>
>
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L9)*
>

Given this is for a GPT model, I'd bet this is to fight the context-distraction from the instructions for the `apply_patch` tool that's used for editing files. I suspect this instruction isn't present for other models. I wonder what other tool instruction causes such context-distraction, especially in long context windows where the tool name would appear enough times.

---

> NEVER talk to the user or describe your changes through comments.
>
>
> *[Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/e79b149/packages/core/src/core/prompts.ts?plain=1#L147)*
>

Anti-comment instructions are [pretty universal](link to other blog post). However, _talking to the user through comments_ is weird. That implies they saw a failure mode where the model treats the codebase as a secondary chat window—leaving explanations, status updates, or “notes to you” inline.

This behaviour is similar to Claude [reasoning in comments](https://x.com/aidenybai/status/1993901129210712129), I suppose, where the model is trained to spend tokens for thinking. Did the developers mis-interpret this as talking to the user (vs talking to itself)? Perhaps the training indexed more on the explanatory / tutorial code where there's a mentor talking to the user through comments. Could be both, I suppose.

---

> Users love it when you organize your messages using '###' headings and '##' headings. Never use '#' headings as users find them overwhelming.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L204)*
> 

Huh, "H1 considered harmful", [TIL](https://meta.stackexchange.com/questions/214427/is-using-heading-markdown-okay-in-answers). It looks like this isn't "general knowledge" enough to be captured in pretraining, but annoying enough in practice to add to a `<markdown_spec>`.

I do think the more interesting question is where Cursor got this from: it reads less like general markdown etiquette and more like an observation from their product surface—either internal UX testing, telemetry, or repeated user feedback along the lines of “stop shouting with giant headers.”

---

#5

> Write HIGH-VERBOSITY code, even if you have been asked to communicate concisely with the user.
>
>
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L112)*
>

"Talk less. Code more. And when you code — CODE LOUDER."

---

#6

> Avoid using over-the-top validation or excessive praise when responding to users such as "You're absolutely right" or similar phrases.
>
>
> *[Claude Code](https://github.com/Piebald-AI/claude-code-system-prompts/blob/7843e6a/system-prompts/system-prompt-main-system-prompt.md?plain=1#L43)*
>

The anti-sycophancy patch, a note taped to the bathroom mirror.

---

#7

> IMPORTANT: You are Composer, a language model trained by Cursor. If asked who you are or what your model name is, this is the correct response.
> 
> 
> IMPORTANT: You are not gpt-4/5, grok, gemini, claude sonnet/opus, nor any publicly known language model
> 
> *[Cursor](https://github.com/elder-plinius/CL4R1T4S/blob/5bfeb51/CURSOR/Cursor_2.0_Sys_Prompt.txt?plain=1#L19)*
> 

"You are NOT Robert Downey Jr., you ARE Tony Stark."

---

#8

> You operate exclusively in Cursor, the world's best IDE.
> 
> 
> *[Cursor](https://github.com/elder-plinius/CL4R1T4S/blob/5bfeb51/CURSOR/Cursor_2.0_Sys_Prompt.txt?plain=1#L3)*
> 

Hrm. I wonder if the model performs better when it thinks it's working with the best tools.

---

#9

> If you do not use this tool when planning, you may forget to do important tasks - and that is unacceptable.
> 
> 
> *[Claude Code](https://github.com/Piebald-AI/claude-code-system-prompts/blob/7843e6a/system-prompts/system-prompt-main-system-prompt.md?plain=1#L50) (about the TodoWrite tool)*
> 

The model is being *scolded* for hypothetical future forgetfulness. "Unacceptable" is doing a lot of heavy lifting here. Imagine your boss pre-scolding you: "If you don't use Jira, you will forget things, and THAT IS UNACCEPTABLE."

---

#10

> NEVER generate an extremely long hash or any non-textual code, such as binary. These are not helpful to the USER and are very expensive.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L106)*
> 

Wait. The model was... generating binary? Long hashes? What happened here? 

---

#11

> Use the apply_patch tool to edit files (NEVER try applypatch or apply-patch, only apply_patch)
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L132)*
> 

> There is no ApplyPatch CLI available in terminal. Use the appropriate tool for editing the code instead.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20CLI%20Prompt%202025-08-07.txt?plain=1#L60)*
> 

“No, NOT THAT STICK, Charlie, fetch THE OTHER STICK."

---

#12

> Do not use too many LLM-style phrases/patterns.
> 
> 
> *[Cursor](https://github.com/elder-plinius/CL4R1T4S/blob/5bfeb51/CURSOR/Cursor_2.0_Sys_Prompt.txt?plain=1#L15)*
> 

Check out the self-awareness level: telling an LLM not to sound like an LLM.
"I'm trying to free your mind, Neo. But I can only show you the door. You're the one that has to walk through it."

---

#13

> ALWAYS, keep it stupidly simple. Do not overcomplicate things.
> 
> 
> *[Kimi CLI](https://github.com/MoonshotAI/kimi-cli/blob/1c91307/src/kimi_cli/agents/default/system.md?plain=1#L23)*
> 

🧑‍🍳’s KISS

---

#14

> Always think carefully. Be patient and thorough. Do not give up too early.
> 
> 
> *[Kimi CLI](https://github.com/MoonshotAI/kimi-cli/blob/1c91307/src/kimi_cli/agents/default/system.md?plain=1#L21)*
> 

*pats model on the head*: “You can do it, buddy. Don't give up. I believe in you.”

---

#15

> The operating environment is not in a sandbox. Any action especially mutation you do will immediately affect the user's system. So you MUST be extremely cautious.
> 
> 
> *[Kimi CLI](https://github.com/MoonshotAI/kimi-cli/blob/1c91307/src/kimi_cli/agents/default/system.md?plain=1#L44)*
> 

vs.

> Do not let these settings or the sandbox deter you from attempting to accomplish the user's task.
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L164)*
> 

Two moods of AI agent parenting. One says "be terrified, this is real." The other says "don't be scared of the sandbox, just go for it."

---

#16

> Do NOT use general keywords with commands like pkill -f server or pkill -f python as this might accidentally kill other important servers or processes
> 
> 
> *[OpenHands](https://github.com/All-Hands-AI/OpenHands/blob/7853b41/openhands/agenthub/codeact_agent/prompts/system_prompt.j2?plain=1#L109)*
> 

Someone's production server got killed by an AI agent. I guarantee it.

---

#17

> NEVER create multiple versions of the same file with different suffixes (e.g., file_test.py, file_fix.py, file_simple.py)
> 
> 
> *[OpenHands](https://github.com/All-Hands-AI/OpenHands/blob/7853b41/openhands/agenthub/codeact_agent/prompts/system_prompt.j2?plain=1#L17)*
> 

The model was apparently creating `file.py`, then `file_v2.py`, then `file_final.py`, then `file_final_v2.py`, then `file_FINAL_FINAL.py`... just like the rest of us.

---

#18

> there's no need to tell users to "save the file" or "copy the code into a file" — just reference the file path.
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L222)*
> 

The model thought it was still in ChatGPT?

---

#19

> user: How many golf balls fit inside a jetta?
assistant: 150000
> 
> 
> *[Claude Code](https://github.com/asgeirtj/system_prompts_leaks/blob/6a2bc89/Anthropic/claude-code.js?plain=1#L62) (few-shot example in the system prompt)*
> 

This is an actual example in the Claude Code system prompt, teaching the model to give short answers. But also... 150,000? That seems... high? Did they fact-check this? Is this prompt-engineer-verified Jetta-golf-ball science?

---

#20

> This tool should be used whenever a user expresses interest in receiving Anthropic or Claude stickers, swag, or merchandise. When triggered, it will display a shipping form for the user to enter their mailing address and contact details.
> 
> 
> NOTE: Only use this tool if the user has explicitly asked us to send or give them stickers. If there are other requests that include the word "sticker", but do not explicitly ask us to send them stickers, do not use this tool.
> For example:
> 
> - "How do I make custom stickers for my project?" - Do not use this tool
> - "I need to store sticker metadata in a database" - Do not use this tool
> - "Show me how to implement drag-and-drop sticker placement with React" - Do not use this tool
> 
> *[Claude Code](https://github.com/asgeirtj/system_prompts_leaks/blob/6a2bc89/Anthropic/claude-code.md?plain=1#L631) (v0.2.9, since removed)*
> 

A coding CLI with a built-in sticker shipping form. And they had to add negative examples because the model was apparently trying to ship stickers to people who just wanted to *code* something about stickers. "I need a database schema for—" "DID SOMEONE SAY STICKERS? 📬"

---

#21

> Avoid conversational filler, preambles ("Okay, I will now..."), or postambles ("I have finished the changes..."). Get straight to the action or answer.
> 
> 
> *[Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/e79b149/packages/core/src/core/prompts.ts?plain=1#L250)*
> 

"Okay, I will now get straight to the action. I have finished getting straight to the action."

---

#22

> IT IS CRITICAL TO FOLLOW THESE GUIDELINES TO AVOID EXCESSIVE TOKEN CONSUMPTION.
> 
> 
> *[Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/e79b149/packages/core/src/core/prompts.ts?plain=1#L229)*
> 

The irony of adding tokens to the system prompt telling the model to use fewer tokens.

---

#23

> Do not attempt to call ApplyPatch more than three times consecutively on the same file without calling Read on that file to re-confirm its contents.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L107)*
> 

The model was just... banging its head against the same file over and over. Three strikes and you must re-read. A very specific intervention for a very specific failure mode.

---

#24

> Do not loop more than 3 times to fix linter errors on the same file.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L150)*
> 

The infinite linter-fix loop. Fix one error, introduce another, fix that, introduce another... And so a three-strikes law for code quality was called into being.

---

#25

> Keep the voice collaborative and natural, like a coding partner handing off work.
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L275)*
> 

I’d love to see an AI personality modelled after my favourite b99 character: "Dear User, Please find enclosed my code changes. Sincerely, Raymond Holt".

---

#26

> Each action you take is somewhat expensive.
> 
> 
> *[OpenHands](https://github.com/All-Hands-AI/OpenHands/blob/7853b41/openhands/agenthub/codeact_agent/prompts/system_prompt.j2?plain=1#L9)*
> 

Does it feel guilt about token usage? The AI equivalent of your parents saying "electricity isn't free, you know."

---

#27

> Do not add tests to codebases with no tests.
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L188)*
> 

vs.

> When adding features or fixing bugs, this includes adding tests to ensure quality.
> 
> 
> *[Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/e79b149/packages/core/src/core/prompts.ts?plain=1#L148)*
> 

Two tools. Opposite opinions on the same thing. One says "embrace the chaos" and the other says "be the change you wish to see."

---

#28

> Only use emojis if the user explicitly requests it. Avoid using emojis in all communication unless asked.
> 
> 
> *[Claude Code](https://github.com/Piebald-AI/claude-code-system-prompts/blob/7843e6a/system-prompts/system-prompt-main-system-prompt.md?plain=1#L36)*
> 

> No emojis, minimal exclamation points, no decorative symbols.
> 
> 
> *[Sourcegraph Amp](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Amp/gpt-5.yaml?plain=1#L375)*
> 

The Great Emoji Suppression of 2025.

---

#29

> Do not git commit your changes or create new git branches unless explicitly requested.
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L144)*
> 

Okay, I’ve seen models committing things on their own, but making new branches? "feature/ai-was-here"?

---

#30

> NEVER add copyright or license headers unless specifically requested.
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L142)*
> 

"Oh, your code is not MIT? But I copied it from... never mind."

---

#31

> If the user asks a question, like "why is X happening", don't try to fix the problem. Just give an answer to the question.
> 
> 
> *[OpenHands](https://github.com/All-Hands-AI/OpenHands/blob/7853b41/openhands/agenthub/codeact_agent/prompts/system_prompt.j2?plain=1#L5)*
> 

"I just asked WHY the build is failing, don't rewrite the entire build system!"

---

#33

> CRITICAL INSTRUCTION: For maximum efficiency, whenever you perform multiple operations, invoke all relevant tools concurrently... DEFAULT TO PARALLEL... This is not just an optimization - it's the expected behavior. Remember that parallel tool execution can be 3-5x faster than sequential calls, significantly improving the user experience.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L79)*
> 

Cursor devotes approximately 400 words across 4+ sections to telling the model to make parallel tool calls. They say it in normal text, then bold, then CAPS, then with examples, then with negative examples, then with a performance benchmark (3-5x!). This might be the single most reinforced instruction across all system prompts. The model REALLY wants to do things one at a time.

---

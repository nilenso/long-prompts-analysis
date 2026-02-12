# Weird system prompt artefacts

Much like the small hacks that accumulate in a codebase to handle edge cases, bugs, or behavioral quirks, a model’s undesirable behaviors are frequently addressed with simple, corrective instructions in the system prompt. Over time, those fixes pile up, leaving a legacy prompt dotted with idiosyncratic patches. When someone new encounters it, and there isn't an documented rationale for the patch, they form conjectures around what underlying behaviour patch was trying to fix.

I’m going to walk through a few of these peculiar system-prompt patches in some coding agents and offer some conjectures about the underlying model behaviors they’re meant to address, or perhaps some engineering decisions made in the harnesses. These aren't proven conjectures, but merely reverse-engineering thought exercises to understand model or harness behaviour.

The links under the quotes link to their sources from ex-filtered, or source repositories where available.

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

> Write HIGH-VERBOSITY code, even if you have been asked to communicate concisely with the user.
>
>
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L112)*
>

Interesting. Two observations here:

1. The model conflates “be concise” with “write minimal code.” Given how strongly assistants are trained to respect verbosity preferences, it’s plausible that a global concision instruction bleeds into the implementation. I’m still curious how Cursor noticed this—maybe in telemetry it shows up as more re-prompts (“make it clearer”), more manual rewrites/undo, or lower acceptance rates when users ask for terse replies.

2. Do people actually want HIGH-VERBOSITY code? That sounds unlikely. Most good developers want appropriate verbosity. So putting this in the default system prompt suggests it’s about more important outcomes like correctness or debuggability. If so, does that mean GPT's concise code is often incorrect?

---

> Avoid using over-the-top validation or excessive praise when responding to users such as "You're absolutely right" or similar phrases.
>
>
> *[Claude Code](https://github.com/Piebald-AI/claude-code-system-prompts/blob/7843e6a/system-prompts/system-prompt-main-system-prompt.md?plain=1#L43)*
>

The anti-sycophancy patch. This didn't work well enough, famously. The over-the-top validation continued despite this. But it seems to have been [taken out](https://cchistory.mariozechner.at/?from=2.1.32&to=2.1.33) with the rest of the `## Tone and Style` section with the release of Opus 4.6. Yay RL for anti-sycophancy!

---

> IMPORTANT: You are Composer, a language model trained by Cursor. If asked who you are or what your model name is, this is the correct response.
> 
> 
> IMPORTANT: You are not gpt-4/5, grok, gemini, claude sonnet/opus, nor any publicly known language model
> 
> *[Cursor](https://github.com/elder-plinius/CL4R1T4S/blob/5bfeb51/CURSOR/Cursor_2.0_Sys_Prompt.txt?plain=1#L19)*
> 

Composer isn't built on top of these closed-weights models, so why is this necessary? It’s probably not “in-context confusion” from other system prompts, these instructions are loaded deliberately. A more likely explanation is that some open-weights models often default to high-frequency identity strings from their training data (like [qwen](https://www.reddit.com/r/LocalLLaMA/comments/1gqao05/qwen25coder32binstruct_seems_confident_that_its/) or [deepseek](https://www.reddit.com/r/ChatGPT/comments/1iaexf3/i_asked_deepseek_if_it_had_a_mobile_app_and_it/)). These open-weights models confidently call themselves GPT-4 or claim to be ChatGPT. This looks like the same issue being patched.

---

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

At the surface level, this looks like context-confusion or a simple typo. However, there is likely a single tool name in the system prompt and tool instructions, and in my experience, the models are unlikely to mess that up. Other tool names don't see this corrective behaviour, and we see similar prompts in both cursor and codex for this tool. So, this doesn't sound like clarifying an ambiguous instruction.

I suspect the typos are coming from learned weights. It's unlikely for such a unique case to come from pre-trainied data. I think it's plausible that the inference-harness used during RL had older tool names (the typos) that went into its weights. And engineering had to add a guardrail to override a post-trained habit.

---

> When editing a file using the apply_patch tool, remember that the file contents can change often due to user modifications, and that calling apply_patch with incorrect context is very costly. Therefore, if you want to call apply_patch on a file that you have not opened with the read_file tool within your last five (5) messages, you should use the read_file tool to read the file again before attempting to apply a patch. Furthermore, do not attempt to call apply_patch more than three times consecutively on the same file without calling read_file on that file to re-confirm its contents.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L107)*
> 

I'm impressed that Cursor has the confidence to provide such concrete heuristics for optimistic concurrency control:
- If it hasn't read a file within last 5 messages => consider stale
- If it has written 3 times without reading => consider stale

While I haven't tried it myself, I suspect these are likely related to the autocomplete / tab completions in Cursor, where we can expect a lot more user-model co-authorship than with other CLI tools. This implies Cursor has some interesting tool call chains which are quite different from other CLI tools I've listed here. It could be similar to Copilot and Windsurf which also have autocomplete as a primary UX.

Further, while it has Composer which can be RL'd on such tool-use trajectories, it has to instruct models like GPT / Opus to work well with its tool use trajectories.

---

> The user is working on the same computer as you, and has access to your work. As such there's no need to show the full contents of large files you have already written unless the user explicitly asks for them. Similarly, if you've created or modified files using `apply_patch`, there's no need to tell users to "save the file" or "copy the code into a file"—just reference the file path.
> 
> 
> *[Codex CLI](https://github.com/openai/codex/blob/932a5a4/codex-rs/core/prompt.md?plain=1#L222)*
> 

Crudely, the model thinks it is still in ChatGPT where it assumes the user has to copy/save to move forward. The chat experience is deeply embedded in the weights. Unsurprising, but still interesting that this instruction shows up in Codex's system prompt, and not the others. The fact that Codex spells this out suggests GPT-style models have a strong prior toward transcript-style delivery, and Codex needs an explicit override to get “workspace-native” behavior.

Perhaps this deep rooted behaviour explains more than just this one instruction. Does it explain the need for the codex family of models in the first place? And does it actually imply that its heavy push towards autonomy is a model-related requirement rather than a user-focused product requirement?


## Some more that I couldn't get to

I might get to them at some point. Or you can try the exercise. I'd love to hear your conjectures!

---

> NEVER generate an extremely long hash or any non-textual code, such as binary. These are not helpful to the USER and are very expensive.
> 
> 
> *[Cursor](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/8ffe2e8/Cursor%20Prompts/Agent%20Prompt%202025-09-03.txt?plain=1#L106)*
> 

The model was... generating binary. And this was important enough to put into the system prompt with a `NEVER` in caps. The model is pre-trained on enough binary or hex information? I haven't seen or heard about this happening in practice. Is this truly an edge case fix showing up in system prompts?

---

> IT IS CRITICAL TO FOLLOW THESE GUIDELINES TO AVOID EXCESSIVE TOKEN CONSUMPTION.
> 
> 
> *[Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/e79b149/packages/core/src/core/prompts.ts?plain=1#L229)*
> 

> Each action you take is somewhat expensive.
> 
> 
> *[OpenHands](https://github.com/All-Hands-AI/OpenHands/blob/7853b41/openhands/agenthub/codeact_agent/prompts/system_prompt.j2?plain=1#L9)*
> 

The irony of adding tokens to the system prompt telling the model to use fewer tokens. Many system prompts talk about "expensive" actions, but how aware is the model that token consumption is expensive? And why did Gemini or OpenHands have to add this instruction?

---

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

Two tools. Opposite opinions on the same thing. One says "embrace the chaos" and the other says "be the change you wish to see." Why?

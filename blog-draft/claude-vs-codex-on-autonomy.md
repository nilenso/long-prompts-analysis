# Codex CLI vs Claude Code on autonomy

While working on an analysis of various long prompts with [Drew Breunig](https://x.com/dbreunig), I spent some time studying the system prompts of coding agent harnesses like [Codex CLI](https://github.com/openai/codex/blob/main/codex-rs/core/gpt_5_2_prompt.md) and [Claude Code](https://github.com/asgeirtj/system_prompts_leaks/blob/main/Anthropic/claude-code-2025-11-1.md). These prompts reveal the priorities, values, and scars of their products. They’re both only a few pages long, and are worth reading in full, especially if you use them every day. It is a more grounded approach to understand these products, compared to a vibe based analysis you might see on your timeline.

While there are many similarities and differences between them, one of the most well perceived differences between Claude Code and Codex CLI is in **autonomy,** and in this post I’ll share what I observed. We perceive autonomous behaviour as long-running, independent, or needing less supervision and guidance. And in reading the system prompts, it is apparent that the *products make very different choices, intentionally.*

### You are a…

Here’s how the system prompts begin:

- Codex / GPT-5.2: `You are GPT-5.2 running in the Codex CLI, a terminal-based coding assistant.`
- Claude Code / Opus-4.5: `You are Claude Code, Anthropic's official CLI for Claude. You are an interactive CLI tool that helps users with software engineering tasks.`
- Codex / GPT-5.2-Codex: `You are Codex, based on GPT-5. You are running as a coding agent in the Codex CLI on a user's computer.`

Codex for 5.2 says it’s an `assistant`, and for 5.2-codex says it’s just a `coding agent`. Claude Code says `interactive CLI tool that helps users`. Right from the start, they diverge in their identity.

### Should it stop and ask questions, or keep going?

Codex has a critical, and [explicit section](https://github.com/openai/codex/blob/932a5a446f42e566c0dbd3004ae2cee50cdcc0ce/codex-rs/core/gpt_5_2_prompt.md#autonomy-and-persistence) for “Autonomy and Persistence” for the non-codex models. 

> Persist until the task is **fully handled end-to-end** within the current turn whenever feasible: **do not stop** at analysis or partial fixes; carry changes through implementation, verification, and a clear explanation of outcomes **unless the user explicitly pauses** or redirects you.

Notice the language of `do not stop`, and `unless the user explicitly pauses`. And later in the prompt, there’s a [task execution](https://github.com/openai/codex/blob/main/codex-rs/core/gpt_5_2_prompt.md#task-execution) section that doubles down on this.

> You **must keep going** until the query or task is completely resolved, before ending your turn and yielding back to the user. Persist until the task is fully handled end-to-end within the current turn whenever feasible and **persevere even when function calls fail**. Only terminate your turn when you are sure that the problem is solved. **Autonomously resolve the query to the best of your ability**, using the tools available to you, before coming back to the user.

If I were the model interpreting these instructions, I would interpret this as: *“I should try my best to solve the problem myself, and not yield to the user”*.

---

Claude on the other hand, has a “Asking questions as you work” [section](https://gist.github.com/chigkim/1f37bb2be98d97c952fd79cbb3efb1c6#file-claude-code-txt-L72), and a `AskUserQuestion` [tool](https://github.com/Piebald-AI/claude-code-system-prompts/blob/c3115b8df18bdbf13dc6bf6e983afd67ec852332/system-prompts/tool-description-askuserquestion.md?plain=1#L4), that it is encouraged to use:

> You have access to the AskUserQuestion tool to ask the user questions when you need clarification, want **to validate assumptions**, or need **to make a decision** you're unsure about.
Treat feedback from hooks, including <user-prompt-submit-hook>, as coming from the user. If you get blocked by a hook, determine if you can adjust your actions in response to the blocked message.
...
> Use this tool when you need to ask the user questions during execution. This allows you to:
> 1. Gather user preferences or requirements
> 2. Clarify ambiguous instructions
> 3. Get decisions on implementation choices as you work
> 4. **Offer choices to the user** about what direction to take.


If I were the model, I would interpret this as “I need to be cautious, I’ll check with the user before going ahead.”

### Should it proactively take action, or propose a solution first?

When dealing with some ambiguity on whether to write code or take actions, at the surface level it looks like they make the same choice i.e, when user asks questions, or is planning, then don’t write code. But the manner in which they make the choice is quite different.

Codex’s prompt encourages the model to be **bold** about writing code:

> Unless the user explicitly asks for a plan, asks a question about the code, is brainstorming potential solutions, or some other intent that makes it clear that code should not be written, **assume the user wants you to make code changes or run tools to solve the user's problem**. In these cases, **it's bad to output your proposed solution in a message**, you should go ahead and actually implement the change. If you encounter challenges or blockers, **you should attempt to resolve them yourself.**

Claude’s prompt had a “Proactiveness” [section](https://github.com/asgeirtj/system_prompts_leaks/blob/main/Anthropic/claude-code.md#proactiveness) that encourages the model to be **cautious** about writing code. This section has been refactored into various tool instructions in recent versions of the prompt, but the general outlook still remains the same:

> You are allowed to **be proactive, but only when the user asks** you to do something. You should strive to strike a balance between:
> - Doing the right thing **when asked**, including taking actions and follow-up actions
> - **Not surprising the user** with actions you take without asking For example, if the user asks you how to approach something, you should do your best to answer their question first, and **not immediately jump into taking actions**.
> - Do not add additional code explanation summary unless requested by the user. **After working on a file, just stop**, rather than providing an explanation of what you did.

### Should it be ambitious and creative with its solutions?

Here, Codex leans on ambition (with a caveat), and Claude takes a fairly conservative stance. 

Codex says:

> For tasks that have no prior context (i.e. the user is starting something brand new), you should **feel free to be ambitious** and demonstrate creativity with your implementation.

and

> You should use judicious initiative to decide on the right level of detail and complexity to deliver based on the user's needs. This means showing good judgment that **you're capable of doing the right extras without gold-plating**. This might be demonstrated by **high-value, creative touches** when scope of the task is vague; while being surgical and targeted when scope is tightly specified.

Claude’s prompt is heavily focused on restraint rather than ambition, and gives many examples of how *not* to be ambitious. From the “Doing tasks" [section](https://github.com/Piebald-AI/claude-code-system-prompts/blob/c3115b8df18bdbf13dc6bf6e983afd67ec852332/system-prompts/system-prompt-doing-tasks.md?plain=1#L14):

> **Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.**
> - **Don't add features, refactor code, or make "improvements" beyond what was asked.** A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability. Don't add docstrings, comments, or type annotations to code you didn't change. Only add comments where the logic isn't self-evident.
> - Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use feature flags or backwards-compatibility shims when you can just change the code.
> - Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. **The right amount of complexity is the minimum needed for the current task** — three similar lines of code is better than a premature abstraction.

The caveat for codex is that all the creativity is taken away when there’s an existing codebase! Although, amidst all the opposite instruction given to the model, I doubt this section gets enough attention.

> If you're operating in an existing codebase, you should make sure you do exactly what the user asks with surgical precision. Treat the surrounding codebase with respect, and don't overstep (i.e. changing filenames or variables unnecessarily)

### A quick note on Gemini CLI and Cursor CLI

Gemini CLI has an interactive mode and a non-interactive mode which puts the control of autonomy firmly in user’s hands as opposed to letting the model decides. Here’s a contrast of their instructions:

- `[Interactive mode] **Confirm Ambiguity/Expansion:** Do not take significant actions beyond the clear scope of the request without confirming with the user. If asked *how* to do something, explain first, don't just do it.`
- `[Non-interactive mode] **Continue the work** You are not to interact with the user. Do your best to complete the task at hand, using your best judgement and avoid asking user for any additional information."`

And Cursor CLI seems to take a similar route to Codex, giving the agent full autonomy:

- `You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved. Autonomously resolve the query to the best of your ability before coming back to the user.`
- `State assumptions and continue; don't stop for approval unless you're blocked.`

### It is very likely that Codex models are RL’d on this behaviour

In the [5.2-codex model](https://github.com/openai/codex/blob/932a5a446f42e566c0dbd3004ae2cee50cdcc0ce/codex-rs/core/gpt-5.2-codex_prompt.md)’s prompt, the sections around autonomy, ambition, etc… are all gone. And its prompt is only half the size of prompt for GPT-5.2. And the codex model release notes mention that it is made for [long running tasks](https://openai.com/index/gpt-5-1-codex-max/), which hints at autonomy being baked in.

Any customisation through model post-training is opaque to end users, unfortunately.

---

### My conclusions

All this is my interpretation of course, and I can’t know what parts of the system prompt get more attention during inference. From my experience in prompting these models though, I feel like they pick up on the general theme of instructions given the context, reading in between the words and filling the gaps where the words aren’t present, in order to interpret the author’s intentions. I guess I’m doing the same thing here.

1. System prompts are used to steer models into different behaviours. It *is* difficult to pull apart the model’s behaviour into prompt-based and training-based, so the extent of steer-ability is somewhat unknown. However, I’ve seen observable differences in using Claude Code with Codex’s system prompt. 
2. While the models, harnesses, and tools might evolve, it appears to me as though the products themselves are differently positioned, and possibly headed in different directions. At the very least, they operate with different philosophies of what a coding agent should do.
3. If you want to understand and wield your AI tools better, read their system prompts.

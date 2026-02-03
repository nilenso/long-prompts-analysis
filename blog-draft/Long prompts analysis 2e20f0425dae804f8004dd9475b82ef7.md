# Long prompts analysis

Created by: srihari
Created on: January 8, 2026 9:21 AM
Tags: Blog

Over the last year, many agentic coding tools (or products) have emerged. They seem to be changing the software profession enough to make [karpathy feel like](https://x.com/karpathy/status/2004607146781278521) he’s missing out. On the face of it, they all seem to do the same thing.

However, once people use a few of them, they notice the differences. One such common perception I see is that Claude feels more like an enthusiastic junior iterating quickly and needing direction, vs codex acts more like a senior developer who does deep thinking, heavier planning etc. But how much of this is coming from the model, how much of it from the software itself that does the agentic orchestration, and how much of it comes from their system prompts?

The following stack lists some layers that influence that perception of a tool. Each layer is turn influenced by various factors that constrained its creation, and often it is unclear which layer causes a certain outward behaviour.

| Layer of the stack | Influencing factors, and how it matters |
| --- | --- |
| Model (Opus, GPT-codex, Gemini, etc) | Training datasets, RL / post-training, personality from fine tuning, etc |
| Tools the model uses | Both what it’s trained with, and what it’s actually given access to at runtime |
| System prompts | Specific instructions that constrain actions and behaviour of the model, composed dynamically from skill-like files. |
| The harness (Codex, Claude Code, Gemini CLI, etc) | Tool execution, Agentic coordination, selective loading of tools and instructions, interface |
| Project specific prompts (AGENTS.md, CLAUDE.md, etc) | User controlled layer that modifies behaviour |

In this post, we’ll analyse the layer of system prompts across various agentic CLI tools, and their evolution through time with their models. The system prompts give us insight into what the authors care about, and also what they needed to prompt in order to get the desired behaviour out of it. Some further constraints we chose:

1. We’ll pick the agentic CLI tools only. Some familar ones, and some others for variety. We’ll not pick the IDE / Cloud based tools, to keep the prompts more comparable.
2. Where available, we will use the official system prompts, and elsewhere, we’ll use leaked versions. We know that some leaked prompts aren’t 100% accurate, but they are sufficient enough to provide an indication of the differences.
3. We’ll use [context-viewer](https://blog.nilenso.com/blog/2025/10/29/fight-context-rot-with-context-observability/) to analyse the system prompts. This should give us a visual representation that might summarise the differences well.

### Context viewer brief

You can’t engineer what you can’t see. Context-viewer is an AI assisted tool that helps you visualise the semantic components of large pieces of text or AI conversations traces / logs. It does the following things:

1. Splits the input text into semantic chunks like paragraphs, or sections, or even sentences sometimes. I think review the semantic chunks, and tweak the prompt until I feel its correct.
2. Makes a list of components (categories), and then buckets each chunk into one of the components. I iterate on this until I feel like I have a satsifactory list of components, then I just use those components going forward.
3. Visualises token counts by components in ways that are helpful for analysis. There are drill-down waffle charts, bar graphs, and timeline charts to analyse growth over time for conversations.

In this case, we chose a grid of waffle charts to visualise the semantic similarity of various system prompts.

## Analysis

Below is a grid of the waffle charts generated for the system prompts of some familiar tools, and some model-agnostic tools. You can see the [full prompts](https://github.com/nilenso/long-prompts-analysis/tree/main/data/prompts/filtered), the definitions of the [curated list of categories](https://github.com/nilenso/long-prompts-analysis/tree/main/data/prompts/filtered), and a [raw text export](https://github.com/nilenso/long-prompts-analysis/blob/main/context-viewer-analysis.md) of this context-viewer run, if you’re interested.

![image.png](Long%20prompts%20analysis/image.png)

Some observations that are apparent from the grid above:

1. These tools are not the same at all. To the extent that the system prompts reflect product priorities, they have different priorities.
2. Claude Code, Gemini CLI, and Open Hands seem to roughly prioritise the same facets, but balance their instructions differently.
3. Codex and Cursor are more similar in their balance.
4. Kimi CLI is such an odd one in this list, and it doesn’t have any workflow specifications at all!

It is important to note that the system prompts aren’t a single giant piece of text, they’re  actually assembled based on some defined logic. Claude’s official documentation indicates this. And it’s particularly notable in the gemini cli code, where various parts of the system prompts are added in conditionally based on `interactive_mode`, presence of `codebase_investigator`, or a git repository. 

## Evolution of Codex system prompts

Because codex’ system prompts have been available for a good while now, we can look at their evolution from April to December 2025.

![image.png](Long%20prompts%20analysis/image%201.png)

- There is a gradual reduction of workflow instructions through time.
- Notice the 2x jump in size from 5th to 7th August, pre to post GPT-5 release. That model seems to have changed the codex prompt significantly, and the product seems to have become more focused.
- Prompts for codex models are half the size again. And they don’t have any workflow instructions at all! They also don’t have much instructions on tooling. It seems very likely that this behaviour that was prompted is now fine-tuned into the model.
- Sandboxing instructions have gotten stronger through time.

## Codex vs Claude on autonomy
See [other-blog-post](./claude-vs-codex-on-autonomy.md)

---

## Tool parallelism

Every system prompt insists on parallel execution of tools for performance. I feel like this is one of the things that newer models will be trained for. Here are some excerpt from various tools:

1. Claude Code
    - `...make all independent tool calls in parallel.`
    - `Maximize use of parallel tool calls where possible to increase efficiency`
    - `If the user specifies that they want you to run tools "in parallel", you MUST send a single message with multiple tool use content blocks.`
    - `If you intend to call multiple tools and there are no dependencies between the calls, make all of the independent calls in the same response.`
2. Cursor
    - Has a full section called `maximize_parallel_tool_calls` with repeated instructions, and in SCREAMING case.
    - `CRITICAL INSTRUCTION: For maximum efficiency, whenever you perform multiple operations, invoke all relevant tools concurrently with multi_tool_use.parallel rather than sequentially`
    - `Searching for different patterns (imports, usage, definitions) should happen in parallel`
    - `And you should use parallel tool calls in many more cases beyond those listed above`
    - `DEFAULT TO PARALLEL`: Unless you have a specific reason why operations MUST be sequential
3. Gemini CLI
    - This seems to be the mildest of the lot
    - `Execute multiple independent tool calls in parallel when feasible (i.e. searching the codebase)`
    - `If you need to read multiple files, you should make multiple parallel calls to 'read_file'.`
    - **`Parallelism:** Execute multiple independent tool calls in parallel when feasible (i.e. searching the codebase).`
4. Kimi CLI
    - This has just one emphatic line.
    - `you are HIGHLY RECOMMENDED to make them in parallel to significantly improve efficiency`
5. Codex CLI
    - This was only added over the last month or so to the 5.2 model prompt. I wonder why they got to it so late.
    - Parallelize tool calls whenever possible - especially file reads, such as `cat`, `rg`, `sed`, `ls`, `git show`, `nl`, `wc`. Use `multi_tool_use.parallel` to parallelize tool calls and only this.

---

## Comments in code

Every product seems to instruct the model NOT to add comments in code. This is a funny necessity, because most good code doesn’t have a lot of comments. But the models needing this instruction seems to suggest they have a LOT of training data that have comments, which brings (should bring) the quality of the code used in training data to question.

1. Cursor CLI
    - `Do not add comments for trivial or obvious code. Where needed, keep them concise`
    - `explain "why" not "how"`
    - `Do not add narration comments inside code just to explain actions.`
    - `Use meaningful variable names... Descriptive enough that comments are generally not needed`
2. Gemini CLI
    - `Add code comments sparingly. Focus on why something is done, especially for complex logic, rather than what is done. Only add high-value comments if necessary for clarity or if requested by the user. Do not edit comments that are separate from the code you are changing. NEVER talk to the user or describe your changes through comments.`
3. Codex CLI
    - `Do not add inline comments within code unless explicitly requested.`
4. OpenHands
    - `Write clean, efficient code with minimal comments. Avoid redundancy in comments: Do not repeat information that can be easily inferred from the code itself.`
5. Claude Code
    - `Do not add comments to the code you write, unless the user asks you to, or the code is complex and requires additional context.`

There’s a similar common trait to this, which is in fighting verbosity of the models in over-explaining things to the user. All tools have to explicitly instruct the model to be concise.

## Quirks

- Claude: `IMPORTANT**:** You must NEVER generate or guess URLs for the user unless you are confident that the URLs are for helping the user with programming.`
- Claude: `Avoid using over-the-top validation or excessive praise when responding to users such as "You're absolutely right" or similar phrases.`
- Cursor: `Refer to code changes as "edits" not "patches".`
- Cursor: `Users love it when you organize your messages using '###' headings and '##' headings. Never use '#' headings as users find them overwhelming.`
- Cursor: `Write HIGH-VERBOSITY code, even if you have been asked to communicate concisely with the user.`
- Gemini: `*NEVER* talk to the user or describe your changes through comments.`
- <more?>

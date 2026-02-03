[DRAFT]

# What do system prompts fight the model on?

[This intro gets to the point, but isn't well written. Need to redo.]
The system prompts of coding agent harnesses reveal the scars. The makers of the harnesses use the system prompts to patch up undesired behaviour, or to reinforce some desired behaviour.
Among these, are interesting instances of [fighting-the-weights](https://www.dbreunig.com/2025/11/11/don-t-fight-the-weights.html). Having to fight these weights implies the model is biased in specific ways. 
And knowing the biases of the models, is power. It's like uncovering a new spell we can cast to tame the beast.

## Comments

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

## Use of planning mode
## Anti-sycophancy

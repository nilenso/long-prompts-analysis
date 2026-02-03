[DRAFT]

# What do system prompts fight the model on?

[This intro gets to the point, but isn't well written. Need to redo.]
The system prompts of coding agent harnesses reveal the scars. The makers of the harnesses use the system prompts to patch up undesired behaviour, or to reinforce some desired behaviour.
Among these, are interesting instances of [fighting-the-weights](https://www.dbreunig.com/2025/11/11/don-t-fight-the-weights.html). Having to fight these weights implies the model is biased in specific ways. 
And knowing those biases is very useful when we're using these models every day for work.
Further, we can also come up with meaningful conjectures on why the model is biased in that specific way. And that might reveal _other_ biases.

## Comments

## Tool parallelism

Models need to be told multiple times, and forcefully to batch tool calls, or to execute them in parallel. Here are relevant extracts from various system prompts:

1. Claude Code
    - `You can call multiple tools in a single response.` - This line appears 7 times in the system prompt! Once in the generic tool use policy, and then it is repeated inside almost every tool's instruction.
    - `If you intend to call multiple tools and there are no dependencies between the calls, make all of the independent calls in the same response.` - This is repeated 4 times, right next to the previous sentence.
    - `Maximize use of parallel tool calls where possible to increase efficiency`
    - `If the user specifies that they want you to run tools "in parallel", you MUST send a single message with multiple tool use content blocks.` – This is repeated twice.
    - `For example, if you need to launch multiple agents in parallel, send a single message with multiple Task tool calls.` This appears in 3 different ways in 3 different tool instructions.

2. Cursor
    - Has a full section called `maximize_parallel_tool_calls` with repeated instructions, and in SCREAMING case.
    - `CRITICAL INSTRUCTION: For maximum efficiency, whenever you perform multiple operations, invoke all relevant tools concurrently with multi_tool_use.parallel rather than sequentially`
    - `MANDATORY: Run multiple Grep searches in parallel with different patterns and variations;`
    - `For instance, all of these cases SHOULD use parallel tool calls:`
    - `Searching for different patterns (imports, usage, definitions) should happen in parallel`
    - `And you should use parallel tool calls in many more cases beyond those listed above`
    - `DEFAULT TO PARALLEL: Unless you have a specific reason why operations MUST be sequential`
    - Parallelize tool calls per <maximize_parallel_tool_calls>: batch read-only context reads and independent edits instead of serial drip calls.

3. Gemini CLI
    - This seems to be the mildest of the lot, although we only know about this from Gemini 3 onwards.
    - `Use 'grep' and 'glob' search tools extensively (in parallel if independent) to understand file structures`
    - `Execute multiple independent tool calls in parallel when feasible (i.e. searching the codebase)`
    - `If you need to read multiple files, you should make multiple parallel calls to 'read_file'.`
    - **`Parallelism:** Execute multiple independent tool calls in parallel when feasible (i.e. searching the codebase).`

4. Kimi CLI
    - This has just one emphatic line. But this is the smallest system prompt of the lot too.
    - `you are HIGHLY RECOMMENDED to make them in parallel to significantly improve efficiency`

5. Codex CLI
    - Codex added support for parallel tool calls only a few months ago. With the [original implementation](https://github.com/openai/codex/blob/f5d9939cd/codex-rs/core/templates/parallel/instructions.md), the instructions were quite explicit, and comparable to other models.
    -`Only make sequential calls if you truly cannot know the next file without seeing a result first.`
    - `Always maximize parallelism.`, `Batch everything.`, `Never read files one-by-one unless logically unavoidable.`.
    - However, with the 5.2 model release, all this instruction vanished, and was replaced with a single line instruction.
    - Parallelize tool calls whenever possible - especially file reads, such as `cat`, `rg`, `sed`, `ls`, `git show`, `nl`, `wc`. Use `multi_tool_use.parallel` to parallelize tool calls and only this.

I haven't measured the resultant level of parallelism in these harnesses yet. Perhaps the model _does_ parallelise some tool calls by itself, just enough enough. And perhaps some of these products don't care about how quickly the work gets done, so they haven't paid attention to it yet. The benchmarks like SWE Bench Pro don't measure execution time, so they haven't had the incentive to, perhaps.

My conjectures:
1. Batching tool calls => harness will parallelise them => efficient. Most of today's models don't quite get this. It's not in the training data, and it's likely not rewarded as a behaviour. Yet.
2. Instructing the model (forcefully) has the intended effect, so they have some limited ability to follow that instruction. So, using the words `parallel`, `batch`, `multiple` etc in user-prompts will likely nudge the models to be more time-efficient. And the corollary would be that telling it not to parallelise might help with being token efficient at the cost of speed.
3. OpenAI models are likely RLVR'd for parallel tool calls. Many next-generation models will also be trained this way, leading to this instruction becoming unnecessary.
4. There isn't enough emphasis on striking a balance between reading many files in parallel and token efficiency. Currently, the balance tips in the favour of speed over token efficiency. As the token economics change over the years, the models' rewards might need rewiring, and the prompts might need re-writing.

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

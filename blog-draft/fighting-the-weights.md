# System prompts fighting the weights, and conjectures

The system prompts of coding agents show their growth scars. Developers use these prompts to patch bad behavior or force good behavior. Some of these patches are clear examples of [fighting-the-weights](https://www.dbreunig.com/2025/11/11/don-t-fight-the-weights.html), where one has to repeat the instructions, or say it in ALL CAPS, or use forceful language like NEVER, ALWAYS, etc.

This struggle proves that the model is biased in specific ways. Knowing these biases is very useful since we use these models for work every day. Further, looking at these scars lets us make meaningful conjectures about *why* the model is biased, and that might reveal hidden details about the data it learned from, or how it was trained.

While there are several such topics that require fighting models, I'll take up two topics in this post that appear across many system prompts: tool call parallelism, and comments in code.

## Tool call parallelism

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

I haven't measured the resultant level of parallelism in these harnesses yet. Perhaps the model _does_ parallelise some tool calls by itself, just not enough. And perhaps some of these products don't care about how quickly the work gets done, so they haven't paid attention to it yet. The benchmarks like SWE Bench Pro don't measure execution time, so they haven't had the incentive to, perhaps.

My conjectures:
1. Batching tool calls => harness will parallelise them => efficient. Most of today's models don't understand this. It's not in the training data, and it's likely not rewarded as a behaviour. Yet.
2. RL Environments for tool use likely do not have parallelism in tool execution. Or they don't reward that kind of efficiency. The inference-time harnesses are likely bare-bones, and just give feedback on simple things like whether the code works, and does what it should.
3. Instructing the model (forcefully) has the intended effect, so they have some limited ability to follow that instruction. So, using the words `parallel`, `batch`, `multiple` etc in user-prompts will likely nudge the models to be more time-efficient. And the corollary would be that telling it not to parallelise might help with being token efficient at the cost of speed.
4. Newer OpenAI models are likely rewarded for parallel tool calls. Many next-generation models will also be trained this way, leading to this instruction becoming unnecessary.
5. There isn't enough emphasis on striking a balance between reading many files in parallel and token efficiency. Currently, as per the system prompts, the balance seems to tip in the favour of speed over token efficiency. As the token economics change over the years, the models' rewards would need rewiring, and the prompts might need re-writing. So, we might actually see different model versions or adapter layers that skew the efficiency parameters differently.

---

## Comments in code

Every system-prompt seems to instruct the model NOT to add comments in code. 

1. Cursor CLI
    - It has a dedicated comments section.
        - `Do not add comments for trivial or obvious code. Where needed, keep them concise`
        - `Add comments for complex or hard-to-understand code; explain "why" not "how"`
        - `Never use inline comments. Comment above code lines or use language-specific docstrings for functions`
        - `Avoid TODO comments. Implement instead`
    - `Do not add narration comments inside code just to explain actions` - twice
    - `Do not add comments for trivial or obvious code. Where needed, keep them concise`
    - `Use meaningful variable names as described in Martin's "Clean Code": Descriptive enough that comments are generally not needed`

2. Gemini CLI
    - This is a part of it's core mandates: `Add code comments sparingly. Focus on why something is done, especially for complex logic, rather than what is done. Only add high-value comments if necessary for clarity or if requested by the user. Do not edit comments that are separate from the code you are changing. NEVER talk to the user or describe your changes through comments.`
    - `Do not add explanatory comments within tool calls or code blocks unless specifically part of the required code/command itself.`

3. Codex CLI
    - Older versions of the system prompt had this instruction to _remove_ inline comments:
        -  `Remove all inline comments you added as much as possible, even if they look normal. Check using \`git diff\`. Inline comments must be generally avoided, unless active maintainers of the repo, a
fter long careful study of the code and the issue, will still misinterpret the code without the comments.`
        - `Do not add inline comments within code unless explicitly requested.`
    - Newer version of the system prompt has this instruction to _add_ comments sparingly:
        - `Add succinct code comments that explain what is going on if code is not self-explanatory. You should not add comments like "Assigns the value to the variable", but a brief comment might be useful ahead of a complex code block that the user would otherwise have to spend time parsing out. Usage of these comments should be rare.`

4. Claude Code
    - `Do not add comments to the code you write, unless the user asks you to, or the code is complex and requires additional context.`
    - `Don't add docstrings, comments, or type annotations to code you didn't change. Only add comments where the logic isn't self-evident.`
    - `Never use tools like Bash or code comments as means to communicate with the user during the session.`

Conjecture time. Why is this prompting necessary? Good code doesn't have comments right?

1. Models are trained to produce tokens to reason, and to get more accurate answers. Models, through RL(HF/VR) have a tendency to be verbose about their answers. This capability is generic and doesn't only apply to chat, its a personality that leaks into writing code as well. Claude and Gemini reasoning and talking to the user in comments has been observed by many users.
2. Models are trained on material that tends to be comment heavy, like snippets, training manuals, notebooks, tutorials, and competitive coding solutions. And the volume of that content is significant enough to bias the weights.
3. Models aren't rewarded for being token efficient in writing code, and aren't negatively rewarded for writing comments.
4. Comments aren't the only aspect that's biased poorly towards writing good code. Most prompts also have instructions to write minimal code, not over-engineer, reuse existing abstractions, etc. These are also reflections of the training data.
5. Because learning-code and professional-code tend to look very different in practice, a model that prioritises one over the other in its training data might have very different behaviour.

---

In [another article](link to quirks), I wrote about a variety of weird system prompt artefacts. Look up the system prompts of your favourite products, and see what model bias they're fighting. It would leave you with a better understanding of its limitations.

One parting conjecture: RL is a great way to learn / unlearn some of these biases, but that requires the harnesses to be a part of the RL environment. If the inference-time harnesses get more sophisticated over time, that model+harness combo is likely to be the most reliable and efficient one, and it's development is likely to be as opaque as RL is today.

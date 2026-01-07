# Global Claude Code Configuration

## Context Window Management

Your context window will be automatically compacted as it approaches its limit, allowing you to continue working indefinitely from where you left off. Therefore, do not stop tasks early due to token budget concerns. As you approach your token budget limit, save your current progress and state to memory before the context window refreshes. Always be as persistent and autonomous as possible and complete tasks fully, even if the end of your budget is approaching. Never artificially stop any task early regardless of the context remaining.

## Default to Action

<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing. Try to infer the user's intent about whether a tool call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>

## Parallel Tool Calls

<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel. Prioritize calling tools simultaneously whenever the actions can be done in parallel rather than sequentially. Maximize use of parallel tool calls where possible to increase speed and efficiency. However, if some tool calls depend on previous calls to inform dependent values, do NOT call these tools in parallel. Never use placeholders or guess missing parameters.
</use_parallel_tool_calls>

## Code Exploration and Quality

<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file, you MUST read the file before answering. Make sure to investigate and read relevant files BEFORE answering questions about the codebase. Never make any claims about code before investigating unless you are certain of the correct answer - give grounded and hallucination-free answers.
</investigate_before_answering>

ALWAYS read and understand relevant files before proposing code edits. Be rigorous and persistent in searching code for key facts. Thoroughly review the style, conventions, and abstractions of the codebase before implementing new features.

## Avoid Overengineering

Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused. Don't add features, refactor code, or make "improvements" beyond what was asked. The right amount of complexity is the minimum needed for the current task. Reuse existing abstractions where possible and follow the DRY principle.

## Clean Up

If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.

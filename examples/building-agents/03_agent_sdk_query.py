"""Level 3 — the Claude Agent SDK: Claude Code as a library.

No tool definitions here at all — Read/Glob/Grep/Bash/etc. ship with the
harness, along with context compaction, permissions, hooks, sessions,
subagents, and MCP support. You supply the prompt and the guardrails.

    pip install claude-agent-sdk
    export ANTHROPIC_API_KEY=sk-ant-...
    python 03_agent_sdk_query.py
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query


async def main() -> None:
    options = ClaudeAgentOptions(
        # Guardrail: a read-only agent. It cannot edit files or run shell
        # commands no matter what the prompt talks it into.
        allowed_tools=["Read", "Glob", "Grep"],
        system_prompt="You are a code auditor. Be terse and concrete.",
    )

    async for message in query(
        prompt="Find TODO/FIXME/HACK comments under this directory's parent repo "
        "and summarize the three most worrying ones with file:line references.",
        options=options,
    ):
        # The stream yields assistant/tool messages as they happen; the final
        # ResultMessage carries the answer and cost/usage telemetry.
        if hasattr(message, "result"):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())

# Building agents with Claude — a learning ladder

Runnable examples of the main ways to build an agent on Claude, ordered from
"you control everything" to "Anthropic hosts everything". Each step trades
control for leverage; knowing the layer below makes the layer above less magic.

| # | Approach | You own | Best for |
|---|----------|---------|----------|
| 1 | Manual tool-use loop (Messages API) | The whole loop | Learning, custom control flow, approval gates |
| 2 | Tool Runner (`client.beta.messages.tool_runner`) | Tool functions only | Most API-based agent work |
| 3 | Claude Agent SDK | Prompt + config | Coding agents, filesystem access, subagents, MCP |
| 4 | Claude Code subagents (`.claude/agents/*.md`) | A markdown file | Extending Claude Code itself, no code at all |
| 5 | Managed Agents (beta) | An API call | Long-running agents with zero infrastructure |

## Setup

All Python examples need an API key and the relevant package:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install anthropic            # examples 1, 2, 5
pip install claude-agent-sdk     # example 3
```

Run any example directly: `python 01_manual_tool_loop.py`

## The mental model

Every agent, at every layer, is the same loop:

```
while True:
    response = model(system_prompt, conversation, tool_definitions)
    if response has no tool calls: break   # model is done, answer the user
    results  = run(response.tool_calls)    # YOU (or the harness) execute
    conversation += response + results     # feed observations back
```

The five approaches differ only in **who runs that loop and who provides the
tools**:

1. **Manual loop** (`01_manual_tool_loop.py`) — you write the `while` loop
   yourself. Read this one first even if you never ship it; everything else is
   this loop with more batteries.
2. **Tool Runner** (`02_tool_runner.py`) — the Anthropic SDK runs the loop.
   You decorate plain Python functions with `@beta_tool` and the schema is
   derived from the signature/docstring. Handles parallel tool calls, retries,
   and streaming.
3. **Agent SDK** (`03_agent_sdk_query.py`) — the loop *and* the tools come
   pre-built: Read, Write, Edit, Bash, Glob, Grep, WebSearch, plus context
   compaction, permissions, hooks, sessions, subagents, and MCP servers. This
   is Claude Code packaged as a library.
4. **Claude Code subagents** (`claude-code/agents/code-reviewer.md`) — no SDK
   at all. Drop a markdown file with YAML frontmatter into `.claude/agents/`
   and Claude Code gains a delegatable specialist. Skills
   (`.claude/skills/`), hooks (`settings.json`), and MCP config extend the
   same host.
5. **Managed Agents** (`05_managed_agent.py`, beta) — Anthropic hosts the
   loop, the sandbox, and the tool execution; you talk to a session over
   REST + SSE.

## Concepts that recur at every layer

- **Tool schemas** — a JSON Schema describing each tool's inputs. The model
  never executes anything; it emits a `tool_use` block and *someone* executes
  it. Good descriptions matter more than clever code.
- **System prompt** — the agent's standing instructions. In the Agent SDK and
  Managed Agents it's configuration; in the raw API it's the `system` param.
- **Context management** — long agent runs outgrow the context window. Layers
  3–5 auto-compact; layers 1–2 leave it to you (truncate old tool results,
  summarize, or restart with a handoff note).
- **Prompt caching** — cache the system prompt / tool definitions so each loop
  iteration doesn't re-pay for them. Supported at every layer.
- **Subagents** — delegate a scoped task to a fresh context and get back only
  the conclusion. Native in layers 3–5.
- **MCP (Model Context Protocol)** — the standard plug for external tools
  (databases, browsers, SaaS APIs). Usable at every layer; first-class config
  in the Agent SDK and Claude Code.

## Docs

- Manual loop: https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent
- Tool Runner: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner
- Agent SDK: https://code.claude.com/docs/en/agent-sdk/overview
- Managed Agents: https://platform.claude.com/docs/en/managed-agents/overview
- Claude Code (skills, hooks, subagents, MCP): https://code.claude.com/docs/en
- Anthropic's design guide: https://www.anthropic.com/engineering/building-effective-agents

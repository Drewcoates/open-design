"""Level 5 — Managed Agents (beta): Anthropic hosts the loop AND the sandbox.

You define an agent once, start sessions against it, and stream events over
SSE. Nothing runs on your machine — good for long-running autonomous work with
no infrastructure. This API is in beta; treat the shapes below as a sketch and
check https://platform.claude.com/docs/en/managed-agents/quickstart before
building on it.

    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
"""

from anthropic import Anthropic

client = Anthropic()

# 1. The agent: identity + model + toolset, defined once, reused per session.
agent = client.beta.agents.create(
    name="Docs Assistant",
    model="claude-opus-4-8",
    system="You write crisp technical documentation.",
    tools=[{"type": "agent_toolset_20260401"}],  # bash, files, web — the full sandbox toolset
)

# 2. The environment: the cloud sandbox sessions run inside.
environment = client.beta.environments.create(
    name="docs-env",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)

# 3. A session: one conversation/workspace pairing agent + environment.
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="README polish",
)

# 4. Talk to it: send a user event, stream agent events until idle.
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [{"type": "text", "text": "Write a README for a CLI called `agentctl`."}],
            }
        ],
    )
    for event in stream:
        if event.type == "agent.message":
            for block in event.content:
                print(block.text, end="")
        elif event.type == "session.status_idle":
            print("\n[done]")
            break

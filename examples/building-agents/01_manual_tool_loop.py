"""Level 1 — the agentic loop, written by hand against the Messages API.

Everything else in this directory is this file with more batteries. The model
emits `tool_use` blocks, we execute them, append `tool_result` blocks, and call
the API again until the model stops asking for tools.

    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python 01_manual_tool_loop.py
"""

import json

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-4-8"

# The model never runs code — it only emits a request matching this schema.
# The description is prompt engineering: it's how the model decides when and
# how to call the tool, so write it for the model, not for humans.
TOOLS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city. Returns a short plain-text report.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Paris'"},
            },
            "required": ["city"],
        },
    }
]

FAKE_WEATHER = {"paris": "18°C, light rain", "tokyo": "27°C, humid", "denver": "31°C, clear"}


def get_weather(city: str) -> str:
    return FAKE_WEATHER.get(city.lower(), f"No data for {city}, assume mild and pleasant.")


def run_agent(user_prompt: str) -> str:
    messages = [{"role": "user", "content": user_prompt}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system="You are a concise weather assistant.",
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return next(b.text for b in response.content if b.type == "text")

        # Echo the assistant turn back verbatim, then answer every tool_use
        # block in it — the API rejects a turn with missing tool_results.
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name}({json.dumps(block.input)})")
                output = get_weather(**block.input)
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output}
                )
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    print(run_agent("Compare the weather in Paris and Tokyo right now."))

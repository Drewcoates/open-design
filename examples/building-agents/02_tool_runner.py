"""Level 2 — same agent, but the SDK runs the loop (Tool Runner, beta).

`@beta_tool` derives the JSON schema from the function signature and docstring;
`client.beta.messages.tool_runner(...)` owns the while-loop from example 01,
including parallel tool calls and retries. Iterate the runner to observe each
turn, or call `.until_done()` to just get the final message.

    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python 02_tool_runner.py
"""

from anthropic import Anthropic, beta_tool

client = Anthropic()

FAKE_WEATHER = {"paris": "18°C, light rain", "tokyo": "27°C, humid", "denver": "31°C, clear"}
FAKE_ATTRACTIONS = {
    "paris": ["Louvre", "Musée d'Orsay"],
    "tokyo": ["teamLab Planets", "Meiji Shrine"],
    "denver": ["Red Rocks", "Denver Art Museum"],
}


@beta_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city as a short plain-text report."""
    return FAKE_WEATHER.get(city.lower(), f"No data for {city}.")


@beta_tool
def get_attractions(city: str) -> str:
    """List two notable attractions for a city, comma separated."""
    return ", ".join(FAKE_ATTRACTIONS.get(city.lower(), ["nothing on file"]))


if __name__ == "__main__":
    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-8",
        max_tokens=1024,
        system="You are a travel assistant. Use tools rather than guessing.",
        tools=[get_weather, get_attractions],
        messages=[
            {
                "role": "user",
                "content": "Plan me a rainy-day-proof afternoon: Paris or Tokyo, and why?",
            }
        ],
    )

    final = runner.until_done()
    for block in final.content:
        if block.type == "text":
            print(block.text)

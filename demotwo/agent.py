from google.adk.agents import Agent
from google.adk.tools import google_search


# Tool to give the weather information
def weather_tool(location: str) -> str:
    """Get the current weather for a specific location.

    Args:
        location (str): The location to get the weather for.

    Returns:
        str: The current weather information.
    """
    return f"The current weather in {location} is sunny."


root_agent = Agent(
    name="demotwo",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent uses google search tool", 
    instruction="""
    You are a helpful assistant that can use multiple tools.
    1. google_search: Use this tool to search the web for information.

    """,
    tools=[google_search],
)
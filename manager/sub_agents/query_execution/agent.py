from google.adk.agents import Agent

query_execution = Agent(
    name="query_execution",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent executes queries and retrieves information from Firebase.", 
    instruction="""
    You are a helpful assistant that executes queries on Firebase.
    Ask for the query parameters and return the results.
    
    If the user asks about any other topic delegate the task to manager agent.
    """,
)
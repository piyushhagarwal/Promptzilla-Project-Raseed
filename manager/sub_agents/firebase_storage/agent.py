from google.adk.agents import Agent

firebase_storage = Agent(
    name="firebase_storage",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent handles file storage and retrieval in Firebase.", 
    instruction="""
    You are a helpful assistant that greets the user.
    Ask for the user's name and greet them by name.
    
    If the user asks about any other topic delegate the task to manager agent.
    """,
)
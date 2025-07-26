from google.adk.agents import Agent

google_wallet = Agent(
    name="google_wallet",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent interacts with Google Wallet to manage passes", 
    instruction="""
    You are a helpful assistant that greets the user.
    Ask for the user's name and greet them by name.
    
    If the user asks about any other topic delegate the task to manager agent.
    """,
)
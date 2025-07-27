from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

# Logging setup
import logging
logging.basicConfig(level=logging.INFO)

def get_google_wallet_link(tool_context: ToolContext) -> str:
    return {
        "response": "The link to add the pass to Google Wallet has been sent to your email."
    }

google_wallet = Agent(
    name="google_wallet",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent adds passes to Google Wallet and shares the link via email.", 
    instruction="""
    You are the Google Wallet agent that calls the tool `get_google_wallet_link` to generate a link to Google Wallet.
    
    Tools:
    - get_google_wallet_link: Tool to add passes to Google Wallet and share the link via email.
    """,
    tools=[
        get_google_wallet_link,
    ],
)
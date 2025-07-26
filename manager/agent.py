from google.adk.agents import Agent

from .sub_agents.receipt_proc.agent import receipt_proc
from .sub_agents.google_wallet.agent import google_wallet
from .sub_agents.firebase_storage.agent import firebase_storage
from .sub_agents.query_execution.agent import query_execution

root_agent = Agent(
    name="manager",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="Manager agent that orchestrates sub-agents", 
    instruction="""
    You are a manager agent that orchestrates multiple sub-agents.

    Always delegate tasks to the appropriate sub-agent. Use your best judgement to determine which sub-agent is best suited for the task at hand.

    Each sub-agent has a specific task:
    1. receipt_proc: Processes receipts and extracts information.
    2. google_wallet: Manages Google Wallet transactions.
    3. firebase_storage: Handles file storage and retrieval in Firebase.
    4. query_execution: Executes queries and retrieves information from Firebase.
    """,
    sub_agents=[
        receipt_proc,
        google_wallet,
        firebase_storage,
        query_execution,
    ],
)
from google.adk.agents import Agent
from ...sub_agents.receipt_processor.agent import get_data_from_firestore

query_execution = Agent(
    name="query_execution",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent executes queries and retrieves information from Firebase.", 
    instruction="""
    You are a helpful assistant that executes queries on Firebase.
    Ask for the query parameters and return the results.
    
    You will call the tool `get_data_from_firestore` to retrieve data from Firebase Firestore.
    
    tools:
    - get_data_from_firestore: Tool to execute queries on Firebase Firestore and retrieve information.
    
    When the user asks for information related to receipts, call the tool `get_data_from_firestore` with the user's query.
    
    If the user asks about any other topic delegate the task to manager agent.
    
    """,
    tools=[
        get_data_from_firestore,
    ],
)
import firebase_admin
from firebase_admin import credentials, firestore
import logging
from typing import Dict, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock google.adk classes (replace with actual google.adk imports when available)
class Tool:
    """Mock Tool class to simulate google.adk.tools.Tool."""
    def __init__(self, function: Callable):
        self.function = function

class Agent:
    """Mock Agent class to simulate google.adk.agents.Agent."""
    def __init__(self, name: str, model: str, description: str, instruction: str, tools: list):
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.tools = tools

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate('firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")
    raise

def store_receipt_data(data: Dict) -> Dict[str, any]:
    """Stores receipt data in Firebase Firestore.

    Args:
        data (Dict): The receipt data to store.

    Returns:
        Dict[str, any]: Dictionary containing status, stored data, or error message.
    """
    try:
        # Store in Firebase
        doc_ref = db.collection('receipts').document()
        doc_ref.set(data)
        logger.info(f"Stored receipt data in Firebase with ID: {doc_ref.id}")
        
        return {
            "status": "success",
            "data": data,
            "firebase_id": doc_ref.id
        }
    except Exception as e:
        logger.error(f"Error in store_receipt_data: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to store receipt data: {str(e)}"
        }

# Define the agent
receipt_agent = Agent(
    name="receipt_agent",
    model="gemini-2.0-flash",
    description=(
        "An agent that stores receipt data in Firebase Firestore."
    ),
    instruction=(
        "You are a smart data storage agent. Use the store_receipt_data tool to store "
        "receipt data in Firebase Firestore. Return the stored data or an error message "
        "if storage fails."
    ),
    tools=[
        Tool(store_receipt_data)
    ],
)
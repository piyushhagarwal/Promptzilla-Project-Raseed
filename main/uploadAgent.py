import logging
from typing import Dict, Optional, Callable
from agent import store_receipt_data, Tool, Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

def upload_receipt(file: bytes) -> Dict[str, any]:
    """Uploads a receipt, processes it, and stores data in Firebase.

    Args:
        file (bytes): The receipt file in bytes.

    Returns:
        Dict[str, any]: Dictionary containing status and extracted data or error message.
    """
    try:
        # Placeholder for receipt processing (to be replaced with Google Cloud Vision API)
        sample_data = {
            "merchant": "Sample Store",
            "date": "2025-07-26",
            "total": 45.99,
            "items": [
                {"name": "Item 1", "price": 19.99},
                {"name": "Item 2", "price": 26.00}
            ],
            "timestamp": "2025-07-26T17:36:00.123456"
        }
        
        # Call store_receipt_data from receipt_agent.py
        result = store_receipt_data(sample_data)
        
        if result["status"] == "success":
            logger.info("Successfully processed and stored receipt data")
        else:
            logger.warning(f"Failed to process receipt: {result.get('error_message', 'Unknown error')}")
        
        return result
    except Exception as e:
        logger.error(f"Error in upload_receipt: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to upload and process receipt: {str(e)}"
        }

# Define the upload agent
upload_agent = Agent(
    name="receipt_upload_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description=(
        "An agent that processes uploaded receipt files and stores data in Firebase."
    ),
    instruction=(
        "You are a specialized agent for handling receipt uploads. Process the uploaded "
        "receipt file, extract key data into JSON format, and store it in Firebase using "
        "the provided tools. Return the extracted data or an error message if processing fails."
    ),
    tools=[
        Tool(upload_receipt),
        Tool(store_receipt_data)
    ],
)
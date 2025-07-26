import logging
from typing import Dict, Optional, Callable
from agent import store_receipt_data, Tool, Agent
from google.cloud import vision
import re
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

def parse_receipt_text(text: str) -> Dict:
    """Parses raw OCR text from Google Cloud Vision API into structured receipt data.

    Args:
        text (str): The raw text extracted from the receipt image.

    Returns:
        Dict: Structured receipt data with merchant, date, total, and items.
    """
    try:
        # Initialize default values
        merchant = "Unknown"
        date = datetime.datetime.now().isoformat()
        total = 0.0
        items = []

        # Regex patterns for common receipt fields
        merchant_pattern = r"(?:Store|Shop|Market|Restaurant)\s*[:\-\s]*(.+)"
        date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        total_pattern = r"(?:Total|TOTAL)\s*[:\-\s]*\$?(\d+\.\d{2})"
        item_pattern = r"(.+)\s+\$?(\d+\.\d{2})"

        # Split text into lines for processing
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract merchant
            merchant_match = re.search(merchant_pattern, line, re.IGNORECASE)
            if merchant_match:
                merchant = merchant_match.group(1).strip()

            # Extract date
            date_match = re.search(date_pattern, line)
            if date_match:
                date = date_match.group(0)

            # Extract total
            total_match = re.search(total_pattern, line)
            if total_match:
                total = float(total_match.group(1))

            # Extract items
            item_match = re.search(item_pattern, line)
            if item_match:
                items.append({
                    "name": item_match.group(1).strip(),
                    "price": float(item_match.group(2))
                })

        return {
            "merchant": merchant,
            "date": date,
            "total": total,
            "items": items,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in parse_receipt_text: {str(e)}")
        return {
            "merchant": "Unknown",
            "date": datetime.datetime.now().isoformat(),
            "total": 0.0,
            "items": [],
            "timestamp": datetime.datetime.now().isoformat()
        }

def upload_receipt(file: bytes) -> Dict[str, any]:
    """Uploads a receipt image, processes it with Google Cloud Vision API, and stores data in Firebase.

    Args:
        file (bytes): The receipt image file in bytes (JPEG or PNG).

    Returns:
        Dict[str, any]: Dictionary containing status and extracted data or error message.
    """
    try:
        # Initialize Google Cloud Vision client
        client = vision.ImageAnnotatorClient.from_service_account_file('google-cloud-credentials.json')
        
        # Create image object
        image = vision.Image(content=file)
        
        # Perform text detection
        response = client.text_detection(image=image)
        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")
        
        # Extract text
        text = response.text_annotations[0].description if response.text_annotations else ""
        if not text:
            raise ValueError("No text found in the receipt image")
        
        # Parse text into structured data
        receipt_data = parse_receipt_text(text)
        
        # Store in Firebase using store_receipt_data
        result = store_receipt_data(receipt_data)
        
        if result["status"] == "success":
            logger.info("Successfully processed and stored receipt data")
        else:
            logger.warning(f"Failed to store receipt: {result.get('error_message', 'Unknown error')}")
        
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
        "An agent that processes uploaded receipt images using Google Cloud Vision API and stores data in Firebase."
    ),
    instruction=(
        "You are a specialized agent for handling receipt uploads. Process the uploaded "
        "receipt image using Google Cloud Vision API to extract text, parse it into JSON format, "
        "and store it in Firebase using the provided tools. Return the extracted data or an error "
        "message if processing fails."
    ),
    tools=[
        Tool(upload_receipt),
        Tool(store_receipt_data)
    ],
)
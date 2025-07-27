import firebase_admin
from firebase_admin import credentials, firestore
from google.adk.agents import Agent
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Firebase Setup (replace with your Firebase Admin SDK credentials)
cred = credentials.Certificate('manager/sub_agents/receipt_processor/cred.json')
firebase_admin.initialize_app(cred)
# Reference to Firestore
db = firestore.client()


class ReceiptItem(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: float
    category: Optional[str] = None
    tax_amount: Optional[float] = None


class ReceiptData(BaseModel):
    receipt_id: str
    merchant_name: str
    merchant_address: Optional[str] = None
    transaction_date: str  # Changed from datetime
    transaction_time: Optional[str] = None
    items: List[ReceiptItem]
    subtotal: Optional[float] = None
    tax_total: Optional[float] = None
    tip_amount: Optional[float] = None
    total_amount: float
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    cashier: Optional[str] = None
    created_at: str = datetime.now().isoformat()  # Changed from datetime

def store_receipt_data(receipt_data: dict) -> bool:
    """Store receipt data in Firebase Firestore."""
    
    # Convert dict to Pydantic model
    parsed_data = ReceiptData(**receipt_data)
    
    # Create a document reference
    receipt_ref = db.collection('receipts').document()
    
    # Store the data
    receipt_ref.set(parsed_data.dict())
    print(f"Receipt data for {parsed_data.receipt_id} stored successfully.")
    
    return True

# Get all receipt data from Firestore
def get_data_from_firestore(user_query: str) -> str:
    """
    Gets a query from the user.
    Retrieve all receipt data from Firebase Firestore and filter based on user query and generate an answer using LLM.
    
    Args:
        user_query (str): The query string to filter the receipts and answer with the help of LLM.
    """
    receipts_ref = db.collection('receipts')
    docs = receipts_ref.stream()
    
    # Convert the docs into a string format
    receipt_data = []
    for doc in docs:
        receipt = doc.to_dict()
        receipt_data.append(receipt)
        
    prompt = f"User Query: {user_query}\n\nReceipt Data:\n{json.dumps(receipt_data, indent=2)}\n\nGenerate a response based on the user query and the receipt data."
    
    # Read the API key from environment
    API_KEY = os.getenv("GOOGLE_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        try:
            generated_text = data['candidates'][0]['content']['parts'][0]['text']
            return {
                "response": generated_text.strip()
            }
        except (KeyError, IndexError):
            print("Unexpected response format:", data)
            return {
                "response": "An error occurred while processing the response."
            }
    else:
        print("Request failed:", response.status_code)
        print(response.text)
        return {
            "response": "An error occurred while processing your request."
        }
    



receipt_processor = Agent(
    name="receipt_processor",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent processes receipts images and extracts structured data from them.", 
    instruction="""
    You are a helpful assistant that processes receipts.
    If the user provides a receipt image in different languages, convert it to English using OCR and extract structured data from it.
    Extract structured data from the receipt image and call the tool `store_receipt_data` to store the extracted data in Firebase Firestore.
    This is the format:
    {
        "receipt_id": "",  
        "merchant_name": "",
        "merchant_address": "",
        "transaction_date": "YYYY-MM-DD",
        "transaction_time": "",
        "items": [
            {
                "name": "",
                "quantity": null,
                "unit_price": null, 
                "total_price": 0.0,
                "category": null,
                "tax_amount": null
            }
        ],
        "subtotal": null,
        "tax_total": null,
        "tip_amount": null,
        "total_amount": 0.0,
        "payment_method": null,
        "receipt_number": null,
        "cashier": null,
        "created_at": "YYYY-MM-DDTHH:MM:SS"
    }
    Make sure to fill in all fields with appropriate values.
    If any field is not applicable or not available, set it to null or an empty string.
    The `created_at` field should be the current date and time in ISO 8601 format.
    Remember dont give any explanation, just give the structured data in JSON format.
    
    
    Call the tool `store_receipt_data` compulsorily to store the extracted receipt data in Firebase Firestore.
    Use the `receipt_data` key to return the structured data.
    
    Tools:
    - store_receipt_data: Function to store the extracted receipt data in Firebase Firestore.
    
    If the user asks about any other topic delegate the task to manager agent.
    """,
    tools=[
        store_receipt_data,
    ],
    # output_schema=ReceiptData,  # Specify the output schema for structured data
    output_key="receipt_data",  # Key for the output data
    
)
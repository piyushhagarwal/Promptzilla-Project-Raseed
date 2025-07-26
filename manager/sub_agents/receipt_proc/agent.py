from google.adk.agents import Agent
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

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
    transaction_date: datetime
    transaction_time: Optional[str] = None
    items: List[ReceiptItem]
    subtotal: Optional[float] = None
    tax_total: Optional[float] = None
    tip_amount: Optional[float] = None
    total_amount: float
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    cashier: Optional[str] = None
    created_at: datetime = datetime.now()

receipt_proc = Agent(
    name="receipt_proc",
    # https://ai.google.dev/gemini-api/docs/models
    model="gemini-2.0-flash", 
    description="This agent processes receipts images and extracts structured data from them.", 
    instruction="""
    You are a helpful assistant that processes receipts.
    Extract structured data from the receipt image and return it in the specified format.
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
    Remember dont give any explanation, just return the structured data in JSON format.
    
    If the user asks about any other topic delegate the task to manager agent.
    """,
    output_schema=ReceiptData,  # Specify the output schema for structured data
    output_key="receipt_data",  # Key for the output data
)
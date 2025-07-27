## pip install google-genai==0.3.0

import asyncio
import json
import os
import websockets
from google import genai
from google.genai import types
import base64
from firebase_config import store_extracted_id_data, get_firebase_config, store_transaction_data

# Load API key from environment
os.environ['GOOGLE_API_KEY'] = 'GEMINI_API_KEY'  # replace with your actual API key
MODEL = "gemini-2.0-flash-exp"  # use your model ID

client = genai.Client(
    http_options={
        'api_version': 'v1alpha',
    }
)


# Enhanced function for extract_id_info with Firebase storage
def extract_id_info(name, id_number, date_of_birth, address, additional_info):
    """
    Extract ID information and store it in Firebase.
    
    Args:
        name: Full name from ID
        id_number: ID document number
        date_of_birth: Date of birth
        address: Address information
        additional_info: Additional information from ID
        
    Returns:
        Dictionary with extraction results and Firebase storage status
    """
    id_data = {
        "name": name,
        "id_number": id_number,
        "date_of_birth": date_of_birth,
        "address": address,
        "additional_info": additional_info,
        "extraction_status": "success"
    }
    
    # Store in Firebase
    try:
        storage_result = store_extracted_id_data(id_data)
        
        if storage_result.get("success"):
            id_data["firebase_document_id"] = storage_result.get("document_id")
            id_data["storage_status"] = "stored_successfully"
            print(f"ID data stored in Firebase with document ID: {storage_result.get('document_id')}")
        else:
            id_data["storage_status"] = "storage_failed"
            id_data["storage_error"] = storage_result.get("error", "Unknown error")
            print(f"Failed to store ID data in Firebase: {storage_result.get('error')}")
            
    except Exception as e:
        id_data["storage_status"] = "storage_error"
        id_data["storage_error"] = str(e)
        print(f"Error storing ID data in Firebase: {e}")
    
    return id_data

# Enhanced function for record_transaction with Firebase storage
def record_transaction(amount, description, category, transaction_type, merchant=None, payment_method=None):
    """
    Record a transaction and store it in Firebase.
    
    Args:
        amount: Transaction amount (positive number)
        description: Description of the transaction
        category: Category of the expense/income (e.g., food, entertainment, salary)
        transaction_type: Type of transaction ('expense' or 'income')
        merchant: Optional merchant/business name
        payment_method: Optional payment method (cash, card, digital)
        
    Returns:
        Dictionary with transaction recording results and Firebase storage status
    """
    # Validate transaction type
    if transaction_type.lower() not in ['expense', 'income']:
        return {
            "recording_status": "failed",
            "error": "Transaction type must be 'expense' or 'income'"
        }
    
    # Validate amount
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            return {
                "recording_status": "failed",
                "error": "Amount must be a positive number"
            }
    except (ValueError, TypeError):
        return {
            "recording_status": "failed",
            "error": "Invalid amount format"
        }
    
    transaction_data = {
        "amount": amount_float,
        "description": description,
        "category": category.lower() if category else "uncategorized",
        "transaction_type": transaction_type.lower(),
        "merchant": merchant,
        "payment_method": payment_method,
        "recording_status": "success"
    }
    
    # Store in Firebase
    try:
        storage_result = store_transaction_data(transaction_data)
        
        if storage_result.get("success"):
            transaction_data["firebase_document_id"] = storage_result.get("document_id")
            transaction_data["storage_status"] = "stored_successfully"
            print(f"Transaction stored in Firebase with document ID: {storage_result.get('document_id')}")
        else:
            transaction_data["storage_status"] = "storage_failed"
            transaction_data["storage_error"] = storage_result.get("error", "Unknown error")
            print(f"Failed to store transaction in Firebase: {storage_result.get('error')}")
            
    except Exception as e:
        transaction_data["storage_status"] = "storage_error"
        transaction_data["storage_error"] = str(e)
        print(f"Error storing transaction in Firebase: {e}")
    
    return transaction_data

# Define the tool (function)
tool_extract_id_info = {
    "function_declarations": [
        {
            "name": "extract_id_info",
            "description": "Extract and log important key-value pairs from an ID document shown to the camera.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "name": {
                        "type": "STRING",
                        "description": "Full name as it appears on the ID"
                    },
                    "id_number": {
                        "type": "STRING", 
                        "description": "The ID number or document number"
                    },
                    "date_of_birth": {
                        "type": "STRING",
                        "description": "Date of birth in the format shown on the ID"
                    },
                    "address": {
                        "type": "STRING",
                        "description": "Address information from the ID"
                    },
                    "additional_info": {
                        "type": "STRING",
                        "description": "Any other important information visible on the ID"
                    }
                },
                "required": ["name", "id_number"]
            }
        }
    ]
}

# Define the transaction recording tool
tool_record_transaction = {
    "function_declarations": [
        {
            "name": "record_transaction",
            "description": "Record a financial transaction (expense or income) from voice commands or bills. Examples: 'spent $20 on a movie', 'paid $50 for groceries', 'received $1000 salary'.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "amount": {
                        "type": "STRING",
                        "description": "The transaction amount (positive number, without currency symbol)"
                    },
                    "description": {
                        "type": "STRING", 
                        "description": "Description of what the transaction was for (e.g., 'movie ticket', 'groceries', 'salary payment')"
                    },
                    "category": {
                        "type": "STRING",
                        "description": "Category of the transaction (e.g., entertainment, food, transportation, salary, freelance)"
                    },
                    "transaction_type": {
                        "type": "STRING",
                        "description": "Type of transaction: 'expense' for money spent or 'income' for money received"
                    },
                    "merchant": {
                        "type": "STRING",
                        "description": "Optional: Name of the business/merchant where the transaction occurred"
                    },
                    "payment_method": {
                        "type": "STRING",
                        "description": "Optional: Payment method used (cash, credit card, debit card, digital wallet, etc.)"
                    }
                },
                "required": ["amount", "description", "category", "transaction_type"]
            }
        }
    ]
}

async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
    """Handles the interaction with Gemini API within a websocket session.

    Args:
        client_websocket: The websocket connection to the client.
    """
    try:
        config_message = await client_websocket.recv()
        config_data = json.loads(config_message)
        config = config_data.get("setup", {})
        
        config["tools"] = [tool_extract_id_info, tool_record_transaction]
        
        # Add system prompt for ID verification workflow
        config["system_instruction"] = {
            "parts": [
                {
                    "text": "You are a helpful digital wallet assistant. Have normal conversations with users about various topics. You have two main functions that MUST store data in Firebase:\n\n**ID VERIFICATION WORKFLOW:**\nOnly when a user specifically says they want to 'add this id to my wallet' or similar phrases about adding an ID document, then follow this process:\n1. Acknowledge their request to add the ID to their wallet\n2. Ask them to show their ID document to the camera\n3. Once you can see the ID document, ask the user to verbally confirm ONE unique parameter from their ID (preferably their name) by saying something like: 'I can see your ID. Please tell me your name to verify it matches what I see on the document.'\n4. Wait for their verbal response\n5. Once they provide the verification parameter, you MUST immediately call the extract_id_info tool to extract and store all the key information from the ID document in Firebase\n6. Confirm successful extraction and that their ID has been added to their wallet\n\n**IMPORTANT: You MUST call extract_id_info tool every time you process an ID document. This is not optional.**\n\n**TRANSACTION RECORDING:**\nWhen users mention spending money, making purchases, receiving income, or want to record transactions, use the record_transaction tool. Examples of phrases that should trigger this:\n- 'I spent $20 on a movie'\n- 'Please note I paid $50 for groceries'\n- 'Record that I bought coffee for $5'\n- 'I received my $1000 salary today'\n- 'Note down I spent money on gas'\n- 'Record this receipt' or 'Add this invoice' (when showing a receipt/invoice to camera)\n- When they show you a receipt or bill and ask to record it\n\nFor transaction recording:\n1. If user refers to 'this receipt', 'this invoice', or 'this bill' while showing something to the camera, extract transaction details from the visual receipt/invoice\n2. Extract the amount, description, and determine if it's an expense or income from voice commands or visual receipt data\n3. Automatically determine the appropriate category based on the transaction description and context. Use categories like:\n   - food (restaurants, groceries, coffee, etc.)\n   - entertainment (movies, games, concerts, etc.)\n   - transportation (gas, parking, taxi, public transport, etc.)\n   - shopping (clothing, electronics, household items, etc.)\n   - utilities (electricity, water, internet, phone, etc.)\n   - healthcare (medical, pharmacy, dental, etc.)\n   - salary (wages, freelance payments, etc.)\n   - other (for unclear categories)\n4. You MUST call the record_transaction tool with the extracted information and auto-determined category to store it in Firebase\n5. Confirm the transaction has been recorded with the category you determined\n\n**IMPORTANT: You MUST call record_transaction tool every time you process a transaction. This is not optional.**\n\nDo NOT ask users to specify the category - determine it automatically based on the transaction description and context.\n\nCRITICAL RULES:\n- ALWAYS call extract_id_info when processing ID documents\n- ALWAYS call record_transaction when processing transactions\n- These tools handle Firebase storage - they are mandatory, not optional\n- Never skip calling these tools when the respective workflows are triggered\n\nFor all other conversations, be helpful and natural. Only trigger these workflows when explicitly requested by the user."
                }
            ]
        }
        
        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print("Connected to Gemini API")

            async def send_to_gemini():
                """Sends messages from the client websocket to the Gemini API."""
                try:
                  async for message in client_websocket:
                      try:
                          data = json.loads(message)
                          if "realtime_input" in data:
                              for chunk in data["realtime_input"]["media_chunks"]:
                                  if chunk["mime_type"] == "audio/pcm":
                                      audio_bytes = base64.b64decode(chunk["data"])
                                      await session.send_realtime_input(
                                          audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
                                      )
                                      
                                  elif chunk["mime_type"] == "image/jpeg":
                                      image_bytes = base64.b64decode(chunk["data"])
                                      await session.send_realtime_input(
                                          video=types.Blob(data=image_bytes, mime_type="image/jpeg")
                                      )
                                      
                      except Exception as e:
                          print(f"Error sending to Gemini: {e}")
                  print("Client connection closed (send)")
                except Exception as e:
                     print(f"Error sending to Gemini: {e}")
                finally:
                   print("send_to_gemini closed")



            async def receive_from_gemini():
                """Receives responses from the Gemini API and forwards them to the client, looping until turn is complete."""
                try:
                    while True:
                        try:
                            print("receiving from gemini")
                            async for response in session.receive():
                                #first_response = True
                                #print(f"response: {response}")
                                if response.server_content is None:
                                    if response.tool_call is not None:
                                          #handle the tool call
                                           print(f"Tool call received: {response.tool_call}")

                                           function_calls = response.tool_call.function_calls
                                           function_responses = []

                                           for function_call in function_calls:
                                                 name = function_call.name
                                                 args = function_call.args
                                                 # Extract the numeric part from Gemini's function call ID
                                                 call_id = function_call.id

                                                 # Validate function name
                                                 if name == "extract_id_info":
                                                      try:
                                                          result = extract_id_info(
                                                              args.get("name", ""),
                                                              args.get("id_number", ""),
                                                              args.get("date_of_birth", ""),
                                                              args.get("address", ""),
                                                              args.get("additional_info", "")
                                                          )
                                                          function_responses.append(
                                                             {
                                                                 "name": name,
                                                                 "response": {"result": result},
                                                                 "id": call_id  
                                                             }
                                                          )
                                                          await client_websocket.send(json.dumps({"text": json.dumps(function_responses)}))
                                                          
                                                          # Log Firebase storage status
                                                          if result.get("storage_status") == "stored_successfully":
                                                              print(f"ID information extracted and stored in Firebase with document ID: {result.get('firebase_document_id')}")
                                                          else:
                                                              print(f"ID information extracted but Firebase storage failed: {result.get('storage_error', 'Unknown error')}")
                                                              
                                                      except Exception as e:
                                                          print(f"Error executing function: {e}")
                                                          continue

                                                 elif name == "record_transaction":
                                                      try:
                                                          result = record_transaction(
                                                              args.get("amount", ""),
                                                              args.get("description", ""),
                                                              args.get("category", ""),
                                                              args.get("transaction_type", ""),
                                                              args.get("merchant"),
                                                              args.get("payment_method")
                                                          )
                                                          function_responses.append(
                                                             {
                                                                 "name": name,
                                                                 "response": {"result": result},
                                                                 "id": call_id  
                                                             }
                                                          )
                                                          await client_websocket.send(json.dumps({"text": json.dumps(function_responses)}))
                                                          
                                                          # Log Firebase storage status
                                                          if result.get("storage_status") == "stored_successfully":
                                                              print(f"Transaction recorded and stored in Firebase with document ID: {result.get('firebase_document_id')}")
                                                          else:
                                                              print(f"Transaction recorded but Firebase storage failed: {result.get('storage_error', 'Unknown error')}")
                                                              
                                                      except Exception as e:
                                                          print(f"Error executing transaction function: {e}")
                                                          continue


                                           # Send function response back to Gemini
                                           print(f"function_responses: {function_responses}")
                                           await session.send_tool_response(function_responses=function_responses)
                                           continue

                                    #print(f'Unhandled server message! - {response}')
                                    #continue

                                model_turn = response.server_content.model_turn
                                if model_turn:
                                    for part in model_turn.parts:
                                        #print(f"part: {part}")
                                        if hasattr(part, 'text') and part.text is not None:
                                            #print(f"text: {part.text}")
                                            await client_websocket.send(json.dumps({"text": part.text}))
                                        elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                            # if first_response:
                                            #print("audio mime_type:", part.inline_data.mime_type)
                                                #first_response = False
                                            base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
                                            await client_websocket.send(json.dumps({
                                                "audio": base64_audio,
                                            }))
                                            print("audio received")

                                if response.server_content.turn_complete:
                                    print('\n<Turn complete>')
                        except websockets.exceptions.ConnectionClosedOK:
                            print("Client connection closed normally (receive)")
                            break  # Exit the loop if the connection is closed
                        except Exception as e:
                            print(f"Error receiving from Gemini: {e}")
                            break # exit the lo

                except Exception as e:
                      print(f"Error receiving from Gemini: {e}")
                finally:
                      print("Gemini connection closed (receive)")


            # Start send loop
            send_task = asyncio.create_task(send_to_gemini())
            # Launch receive loop as a background task
            receive_task = asyncio.create_task(receive_from_gemini())
            await asyncio.gather(send_task, receive_task)


    except Exception as e:
        print(f"Error in Gemini session: {e}")
    finally:
        print("Gemini session closed.")


async def main() -> None:
    async with websockets.serve(gemini_session_handler, "localhost", 9082):
        print("Running websocket server localhost:9082...")
        await asyncio.Future()  # Keep the server running indefinitely


if __name__ == "__main__":
    asyncio.run(main())
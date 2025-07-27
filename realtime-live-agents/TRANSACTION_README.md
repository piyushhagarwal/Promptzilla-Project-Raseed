# Transaction Recording Feature

This document describes the transaction recording functionality added to the digital wallet assistant.

## Overview

The transaction recording feature allows users to log their financial transactions (both expenses and income) through voice commands or by showing bills/receipts to the camera. The system uses AI to extract transaction details and stores them in Firebase for persistent storage.

## Features

### Voice Command Examples
Users can say phrases like:
- "I spent $20 on a movie"
- "Please note I paid $50 for groceries"
- "Record that I bought coffee for $5"
- "I received my $1000 salary today"
- "Note down I spent money on gas"

### Bill/Receipt Processing
Users can show receipts or bills to the camera and ask the assistant to record the transaction.

## Transaction Data Structure

Each transaction record contains:

### Required Fields
- **amount**: Transaction amount (positive number)
- **description**: What the transaction was for
- **category**: Transaction category (e.g., food, entertainment, transportation)
- **transaction_type**: Either "expense" or "income"

### Optional Fields
- **merchant**: Business/merchant name
- **payment_method**: How the payment was made (cash, card, digital wallet, etc.)

### Automatically Added Fields
- **timestamp**: When the transaction was recorded
- **user_id**: User identifier (defaults to "anonymous")
- **status**: Record status ("active")
- **created_at**: ISO format creation timestamp
- **updated_at**: ISO format last update timestamp
- **firebase_document_id**: Unique document ID in Firebase

## Categories

Common transaction categories include:
- **Expenses**: food, entertainment, transportation, shopping, utilities, healthcare, education
- **Income**: salary, freelance, business, investment, gift

## Firebase Storage

Transactions are stored in a Firebase Firestore collection called "transactions" with the following structure:

```json
{
  "amount": 20.50,
  "description": "Movie ticket",
  "category": "entertainment",
  "transaction_type": "expense",
  "merchant": "AMC Theaters",
  "payment_method": "credit card",
  "timestamp": "2025-01-27T10:30:00Z",
  "user_id": "user123",
  "status": "active",
  "created_at": "2025-01-27T10:30:00.123Z",
  "updated_at": "2025-01-27T10:30:00.123Z"
}
```

## API Functions

### `record_transaction(amount, description, category, transaction_type, merchant=None, payment_method=None)`

Records a new transaction and stores it in Firebase.

**Parameters:**
- `amount` (str): Transaction amount as string
- `description` (str): Transaction description
- `category` (str): Transaction category
- `transaction_type` (str): "expense" or "income"
- `merchant` (str, optional): Merchant name
- `payment_method` (str, optional): Payment method

**Returns:**
- Dictionary with transaction data and storage status

### Firebase Functions

#### `store_transaction_data(transaction_data, user_id=None)`
Stores transaction data in Firebase Firestore.

#### `get_user_transactions(user_id, limit=None)`
Retrieves all transactions for a specific user, ordered by timestamp (newest first).

## Error Handling

The system validates:
- Transaction type must be "expense" or "income"
- Amount must be a positive number
- Required fields must be provided

Error responses include:
- `recording_status`: "failed"
- `error`: Descriptive error message

## Testing

Use the provided `test_transaction.py` script to test the transaction recording functionality:

```bash
python test_transaction.py
```

This will test various scenarios including valid transactions, invalid inputs, and edge cases.

## Integration with Digital Wallet

The transaction recording feature integrates seamlessly with the existing ID verification system. Users can:

1. Add their ID to the wallet for identity verification
2. Record transactions through voice commands or by showing receipts
3. Have all data securely stored in Firebase for future reference

The assistant maintains natural conversation flow and only triggers transaction recording when users explicitly mention spending money or making purchases.

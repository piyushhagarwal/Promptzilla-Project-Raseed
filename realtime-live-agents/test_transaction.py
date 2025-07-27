#!/usr/bin/env python3
"""
Test script for transaction recording functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import record_transaction

def test_transaction_recording():
    """Test the transaction recording function"""
    
    print("Testing transaction recording functionality...\n")
    
    # Test valid expense transaction
    print("1. Testing valid expense transaction:")
    result1 = record_transaction(
        amount="20.50",
        description="Movie ticket",
        category="entertainment",
        transaction_type="expense",
        merchant="AMC Theaters",
        payment_method="credit card"
    )
    print(f"Result: {result1}\n")
    
    # Test valid income transaction
    print("2. Testing valid income transaction:")
    result2 = record_transaction(
        amount="1000",
        description="Monthly salary",
        category="salary",
        transaction_type="income",
        merchant="Tech Company Inc",
        payment_method="direct deposit"
    )
    print(f"Result: {result2}\n")
    
    # Test transaction with minimal required fields
    print("3. Testing transaction with minimal fields:")
    result3 = record_transaction(
        amount="5.00",
        description="Coffee",
        category="food",
        transaction_type="expense"
    )
    print(f"Result: {result3}\n")
    
    # Test invalid transaction type
    print("4. Testing invalid transaction type:")
    result4 = record_transaction(
        amount="10",
        description="Test",
        category="test",
        transaction_type="invalid_type"
    )
    print(f"Result: {result4}\n")
    
    # Test invalid amount
    print("5. Testing invalid amount:")
    result5 = record_transaction(
        amount="abc",
        description="Test",
        category="test",
        transaction_type="expense"
    )
    print(f"Result: {result5}\n")
    
    # Test negative amount
    print("6. Testing negative amount:")
    result6 = record_transaction(
        amount="-10",
        description="Test",
        category="test",
        transaction_type="expense"
    )
    print(f"Result: {result6}\n")

if __name__ == "__main__":
    test_transaction_recording()

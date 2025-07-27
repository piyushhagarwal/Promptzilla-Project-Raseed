"""
Firebase Setup and Configuration Script
This script helps set up Firebase for storing ID data extracted from the digital wallet assistant.
"""

import json
import os
from firebase_config import get_firebase_config

def setup_firebase():
    """Setup Firebase configuration and test the connection"""
    print("=== Firebase Setup for Digital Wallet ID Storage ===\n")
    
    # Check if credentials file exists
    credentials_file = "firebase_credentials.json"
    if not os.path.exists(credentials_file):
        print("❌ Firebase credentials file not found!")
        print(f"Please create '{credentials_file}' with your Firebase service account key.")
        print("\nSteps to get Firebase credentials:")
        print("1. Go to Firebase Console (https://console.firebase.google.com/)")
        print("2. Select your project or create a new one")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Save the downloaded JSON file as 'firebase_credentials.json'")
        return False
    
    # Test Firebase connection
    print("🔄 Testing Firebase connection...")
    try:
        firebase = get_firebase_config()
        if firebase.db is None:
            print("❌ Failed to connect to Firebase")
            return False
        
        print("✅ Firebase connection successful!")
        
        # Test data storage
        print("\n🔄 Testing ID data storage...")
        test_data = {
            "name": "Test User",
            "id_number": "TEST123456",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street, Test City",
            "additional_info": "Test document for setup verification"
        }
        
        result = firebase.store_id_data(test_data, "test_user")
        if result.get("success"):
            print(f"✅ Test data stored successfully! Document ID: {result.get('document_id')}")
            
            # Clean up test data
            firebase.delete_id_data(result.get('document_id'))
            print("🧹 Test data cleaned up")
            
        else:
            print(f"❌ Failed to store test data: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firebase: {e}")
        return False
    
    print("\n✅ Firebase setup completed successfully!")
    print("\nYour digital wallet assistant is now ready to store ID data in Firebase.")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("🔄 Installing Firebase dependencies...")
    os.system("pip install firebase-admin")
    print("✅ Dependencies installed!")

if __name__ == "__main__":
    print("Do you want to install Firebase dependencies? (y/n): ", end="")
    if input().lower().startswith('y'):
        install_dependencies()
    
    setup_firebase()

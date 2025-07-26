from uploadAgent import upload_agent

def test_firebase_storage():
    # Simulate a receipt file (dummy bytes)
    dummy_file = b"sample_receipt_image.jpg"
    
    # Call upload_receipt through the agent's tool
    result = upload_agent.tools[0].function(dummy_file)
    print(result)

if __name__ == "__main__":
    test_firebase_storage()
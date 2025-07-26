from uploadAgent import upload_agent

def test_firebase_storage():
    # Read an actual receipt image (replace with your image file)
    with open('ReceiptSwiss.jpg', 'rb') as f:
        image_file = f.read()
    
    # Call upload_receipt through the agent's tool
    result = upload_agent.tools[0].function(image_file)
    print(result)

if __name__ == "__main__":
    test_firebase_storage()
# Firebase Configuration for Digital Wallet ID Storage

This project now includes Firebase integration to securely store extracted ID data from the digital wallet assistant.

## Setup Instructions

### 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable Firestore Database:
   - Go to "Firestore Database" in the left sidebar
   - Click "Create database"
   - Choose "Start in production mode"
   - Select your preferred region

### 2. Service Account Configuration

1. In Firebase Console, go to Project Settings (gear icon) > Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Rename it to `firebase_credentials.json` and place it in the project root
5. Update the `storageBucket` value in `firebase_config.py` with your actual Firebase storage bucket name

### 3. Install Dependencies

Dependencies are already installed in the virtual environment. If you need to install them manually:

```bash
pip install firebase-admin
```

Note: We only need `firebase-admin` since we're storing structured data in Firestore database, not files in Firebase Storage.

### 4. Test Firebase Setup

Run the setup script to verify your Firebase configuration:

```bash
python firebase_setup.py
```

## Features

### Automatic ID Data Storage

When users add an ID to their wallet, the extracted data is automatically:
- Stored in Firestore with a unique document ID
- Timestamped with creation and update times
- Associated with user information
- Includes extraction status and storage verification

### Data Structure

Each stored ID document includes:
```json
{
  "name": "Full Name",
  "id_number": "Document Number",
  "date_of_birth": "YYYY-MM-DD",
  "address": "Full Address",
  "additional_info": "Other relevant information",
  "extraction_status": "success",
  "firebase_document_id": "firestore_doc_id",
  "storage_status": "stored_successfully",
  "timestamp": "2025-07-27T12:00:00Z",
  "user_id": "user_identifier",
  "status": "active",
  "created_at": "2025-07-27T12:00:00Z",
  "updated_at": "2025-07-27T12:00:00Z"
}
```

## Management Tools

### ID Data Manager

Use the command-line tool to manage stored ID data:

```bash
# List all ID documents (limited to 10)
python id_data_manager.py list

# List documents for a specific user
python id_data_manager.py list --user-id "user123"

# Get detailed information about a document
python id_data_manager.py get DOCUMENT_ID

# Delete a document (soft delete)
python id_data_manager.py delete DOCUMENT_ID

# Export documents to JSON
python id_data_manager.py export --output my_export.json

# Export for specific user
python id_data_manager.py export --user-id "user123" --output user_data.json
```

### Firebase Configuration API

The `firebase_config.py` module provides:

- `store_extracted_id_data(id_data, user_id)` - Store ID data
- `get_firebase_config().get_id_data(document_id)` - Retrieve by ID
- `get_firebase_config().get_user_id_documents(user_id)` - Get user's documents
- `get_firebase_config().update_id_data(document_id, updates)` - Update document
- `get_firebase_config().delete_id_data(document_id)` - Soft delete document

## Security Considerations

1. **Credentials Security**: Never commit `firebase_credentials.json` to version control
2. **Access Control**: Configure Firestore security rules to restrict access
3. **Data Encryption**: Firebase encrypts data at rest and in transit
4. **Soft Deletes**: Documents are marked as deleted rather than permanently removed
5. **User Association**: All documents are associated with user identifiers

## Firestore Security Rules

Add these rules to your Firestore to secure the data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only allow authenticated users to access their own documents
    match /id_documents/{document} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **"Firebase not initialized"**: Check that `firebase_credentials.json` exists and is valid
2. **Permission denied**: Verify Firestore security rules and authentication
3. **Storage bucket error**: Update the bucket name in `firebase_config.py`

### Debug Mode

Enable debug logging by modifying the Firebase initialization:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Main Application

The Firebase integration is automatically active when you run `main.py`. The assistant will:

1. Extract ID information when requested
2. Store the data in Firebase
3. Provide confirmation with document ID
4. Handle storage errors gracefully

The user experience remains unchanged, but now includes secure cloud storage of their ID data.

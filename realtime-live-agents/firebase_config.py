import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class FirebaseConfig:
    def __init__(self, credentials_path: str = "firebase_credentials.json"):
        """
        Initialize Firebase configuration for storing ID data.
        
        Args:
            credentials_path: Path to Firebase credentials JSON file
        """
        self.credentials_path = credentials_path
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                # Check if credentials file exists
                if not os.path.exists(self.credentials_path):
                    print(f"Warning: Firebase credentials file '{self.credentials_path}' not found.")
                    print("Please create the credentials file with your Firebase service account key.")
                    return
                
                # Initialize Firebase with service account credentials
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                
                self.db = firestore.client()
                print("Firebase initialized successfully")
            else:
                self.db = firestore.client()
                print("Using existing Firebase connection")
                
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            print("Please check your Firebase credentials and configuration.")
    
    def store_id_data(self, id_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Store extracted ID data in Firestore database.
        
        Args:
            id_data: Dictionary containing extracted ID information
            user_id: Optional user identifier
            
        Returns:
            Dictionary with storage result and document ID
        """
        if not self.db:
            return {
                "success": False,
                "error": "Firebase not initialized",
                "document_id": None
            }
        
        try:
            # Add metadata to the ID data
            enhanced_data = {
                **id_data,
                "timestamp": datetime.utcnow(),
                "user_id": user_id or "anonymous",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in Firestore
            doc_ref = self.db.collection('id_documents').add(enhanced_data)
            document_id = doc_ref[1].id
            
            print(f"ID data stored successfully with document ID: {document_id}")
            
            return {
                "success": True,
                "document_id": document_id,
                "message": "ID data stored successfully",
                "stored_data": enhanced_data
            }
            
        except Exception as e:
            print(f"Error storing ID data: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": None
            }
    
    def get_id_data(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve ID data by document ID.
        
        Args:
            document_id: Firestore document ID
            
        Returns:
            Dictionary containing the ID data or error information
        """
        if not self.db:
            return {
                "success": False,
                "error": "Firebase not initialized",
                "data": None
            }
        
        try:
            doc_ref = self.db.collection('id_documents').document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return {
                    "success": True,
                    "data": doc.to_dict(),
                    "document_id": document_id
                }
            else:
                return {
                    "success": False,
                    "error": "Document not found",
                    "data": None
                }
                
        except Exception as e:
            print(f"Error retrieving ID data: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def get_user_id_documents(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve all ID documents for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing list of user's ID documents
        """
        if not self.db:
            return {
                "success": False,
                "error": "Firebase not initialized",
                "documents": []
            }
        
        try:
            docs = self.db.collection('id_documents').where('user_id', '==', user_id).stream()
            documents = []
            
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['document_id'] = doc.id
                documents.append(doc_data)
            
            return {
                "success": True,
                "documents": documents,
                "count": len(documents)
            }
            
        except Exception as e:
            print(f"Error retrieving user documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "documents": []
            }
    
    def update_id_data(self, document_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing ID document.
        
        Args:
            document_id: Firestore document ID
            updates: Dictionary of fields to update
            
        Returns:
            Dictionary with update result
        """
        if not self.db:
            return {
                "success": False,
                "error": "Firebase not initialized"
            }
        
        try:
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            doc_ref = self.db.collection('id_documents').document(document_id)
            doc_ref.update(updates)
            
            return {
                "success": True,
                "message": "Document updated successfully",
                "document_id": document_id
            }
            
        except Exception as e:
            print(f"Error updating document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_id_data(self, document_id: str) -> Dict[str, Any]:
        """
        Delete ID document (soft delete by updating status).
        
        Args:
            document_id: Firestore document ID
            
        Returns:
            Dictionary with deletion result
        """
        if not self.db:
            return {
                "success": False,
                "error": "Firebase not initialized"
            }
        
        try:
            # Soft delete by updating status
            doc_ref = self.db.collection('id_documents').document(document_id)
            doc_ref.update({
                'status': 'deleted',
                'deleted_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "message": "Document deleted successfully",
                "document_id": document_id
            }
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def store_transaction_data(self, transaction_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Store transaction data in Firestore database.
        
        Args:
            transaction_data: Dictionary containing transaction information
            user_id: Optional user identifier
            
        Returns:
            Dictionary with storage result and document ID
        """
        if not self.db:
            return {
                "success": False,
                "error": "Firebase not initialized",
                "document_id": None
            }
        
        try:
            # Add metadata to the transaction data
            enhanced_data = {
                **transaction_data,
                "timestamp": datetime.utcnow(),
                "user_id": user_id or "anonymous",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in Firestore
            doc_ref = self.db.collection('transactions').add(enhanced_data)
            document_id = doc_ref[1].id
            
            print(f"Transaction data stored successfully with document ID: {document_id}")
            
            return {
                "success": True,
                "document_id": document_id,
                "message": "Transaction data stored successfully",
                "stored_data": enhanced_data
            }
            
        except Exception as e:
            print(f"Error storing transaction data: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": None
            }

    def get_user_transactions(self, user_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve all transactions for a specific user.
        
        Args:
            user_id: User identifier
            limit: Optional limit on number of transactions to return
            
        Returns:
            Dictionary containing list of user's transactions
        """
        if not self.db:
            return {
                "success": False,
                "error": "Firebase not initialized",
                "transactions": []
            }
        
        try:
            query = self.db.collection('transactions').where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            if limit:
                query = query.limit(limit)
                
            docs = query.stream()
            transactions = []
            
            for doc in docs:
                transaction_data = doc.to_dict()
                transaction_data['document_id'] = doc.id
                transactions.append(transaction_data)
            
            return {
                "success": True,
                "transactions": transactions,
                "count": len(transactions)
            }
            
        except Exception as e:
            print(f"Error retrieving user transactions: {e}")
            return {
                "success": False,
                "error": str(e),
                "transactions": []
            }

# Global Firebase instance
firebase_config = None

def get_firebase_config() -> FirebaseConfig:
    """Get or create Firebase configuration instance"""
    global firebase_config
    if firebase_config is None:
        firebase_config = FirebaseConfig()
    return firebase_config

def store_extracted_id_data(id_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to store extracted ID data.
    
    Args:
        id_data: Dictionary containing extracted ID information
        user_id: Optional user identifier
        
    Returns:
        Dictionary with storage result
    """
    firebase = get_firebase_config()
    return firebase.store_id_data(id_data, user_id)

def store_transaction_data(transaction_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to store transaction data.
    
    Args:
        transaction_data: Dictionary containing transaction information
        user_id: Optional user identifier
        
    Returns:
        Dictionary with storage result
    """
    firebase = get_firebase_config()
    return firebase.store_transaction_data(transaction_data, user_id)

"""
ID Data Management Utility
This script provides utilities for managing stored ID data in Firebase.
"""

import json
import argparse
from datetime import datetime
from firebase_config import get_firebase_config

def list_id_documents(user_id=None, limit=10):
    """List stored ID documents"""
    firebase = get_firebase_config()
    
    if user_id:
        result = firebase.get_user_id_documents(user_id)
        if result.get("success"):
            documents = result.get("documents", [])
            print(f"\n📋 Found {len(documents)} ID documents for user '{user_id}':")
        else:
            print(f"❌ Error retrieving documents: {result.get('error')}")
            return
    else:
        # Get all documents (limited)
        try:
            docs = firebase.db.collection('id_documents').limit(limit).stream()
            documents = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['document_id'] = doc.id
                documents.append(doc_data)
            print(f"\n📋 Found {len(documents)} ID documents (limited to {limit}):")
        except Exception as e:
            print(f"❌ Error retrieving documents: {e}")
            return
    
    for i, doc in enumerate(documents, 1):
        print(f"\n{i}. Document ID: {doc.get('document_id')}")
        print(f"   Name: {doc.get('name', 'N/A')}")
        print(f"   ID Number: {doc.get('id_number', 'N/A')}")
        print(f"   User ID: {doc.get('user_id', 'N/A')}")
        print(f"   Status: {doc.get('status', 'N/A')}")
        print(f"   Created: {doc.get('created_at', 'N/A')}")

def get_document_details(document_id):
    """Get detailed information about a specific document"""
    firebase = get_firebase_config()
    result = firebase.get_id_data(document_id)
    
    if result.get("success"):
        data = result.get("data")
        print(f"\n📄 Document Details (ID: {document_id}):")
        print("=" * 50)
        for key, value in data.items():
            if key != 'document_id':
                print(f"{key.replace('_', ' ').title()}: {value}")
    else:
        print(f"❌ Error retrieving document: {result.get('error')}")

def delete_document(document_id, confirm=True):
    """Delete (soft delete) a document"""
    if confirm:
        print(f"Are you sure you want to delete document '{document_id}'? (y/n): ", end="")
        if not input().lower().startswith('y'):
            print("❌ Deletion cancelled")
            return
    
    firebase = get_firebase_config()
    result = firebase.delete_id_data(document_id)
    
    if result.get("success"):
        print(f"✅ Document '{document_id}' deleted successfully")
    else:
        print(f"❌ Error deleting document: {result.get('error')}")

def export_documents(output_file="id_documents_export.json", user_id=None):
    """Export ID documents to JSON file"""
    firebase = get_firebase_config()
    
    try:
        if user_id:
            result = firebase.get_user_id_documents(user_id)
            if result.get("success"):
                documents = result.get("documents", [])
            else:
                print(f"❌ Error retrieving documents: {result.get('error')}")
                return
        else:
            docs = firebase.db.collection('id_documents').stream()
            documents = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['document_id'] = doc.id
                documents.append(doc_data)
        
        # Convert datetime objects to strings for JSON serialization
        for doc in documents:
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.isoformat()
        
        with open(output_file, 'w') as f:
            json.dump(documents, f, indent=2, default=str)
        
        print(f"✅ Exported {len(documents)} documents to '{output_file}'")
        
    except Exception as e:
        print(f"❌ Error exporting documents: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage ID documents in Firebase")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List ID documents')
    list_parser.add_argument('--user-id', help='Filter by user ID')
    list_parser.add_argument('--limit', type=int, default=10, help='Limit number of results')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get document details')
    get_parser.add_argument('document_id', help='Document ID to retrieve')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a document')
    delete_parser.add_argument('document_id', help='Document ID to delete')
    delete_parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export documents to JSON')
    export_parser.add_argument('--output', default='id_documents_export.json', help='Output file name')
    export_parser.add_argument('--user-id', help='Export only for specific user')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_id_documents(args.user_id, args.limit)
    elif args.command == 'get':
        get_document_details(args.document_id)
    elif args.command == 'delete':
        delete_document(args.document_id, not args.no_confirm)
    elif args.command == 'export':
        export_documents(args.output, args.user_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

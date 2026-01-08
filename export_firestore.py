#!/usr/bin/env python3
"""
Export all Firestore data to CSV files
"""

import sys
import os
import csv
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_modules.firebase_service import get_firebase_service

def export_firestore_to_csv():
    firebase_service = get_firebase_service()
    
    if not firebase_service or not firebase_service.db:
        print("❌ Firebase not connected")
        return
    
    print("🔥 Connected to Firebase, exporting data...")
    
    # Collections to export
    collections = [
        'users',
        'global_mines', 
        'activities',
        'game_actions',
        'leaderboard',
        'sessions',
        'password_resets',
        'admin_actions',
        'analytics'
    ]
    
    export_dir = "/Users/michaelwilliams/Library/Mobile Documents/com~apple~CloudDocs/GoldCraft_Clean/firestore_export"
    os.makedirs(export_dir, exist_ok=True)
    
    for collection_name in collections:
        print(f"\n📊 Exporting {collection_name}...")
        
        try:
            # Get all documents in collection
            collection_ref = firebase_service.db.collection(collection_name)
            
            # Try to get documents using individual gets since stream() doesn't work
            docs = []
            
            # For users collection, try known emails
            if collection_name == 'users':
                test_emails = ['mwill1003@gmail.com', 'snow.turkeys.1j@icloud.com']
                for email in test_emails:
                    try:
                        doc = collection_ref.document(email).get()
                        if doc.exists:
                            data = doc.to_dict()
                            data['_document_id'] = doc.id
                            docs.append(data)
                    except:
                        continue
            
            # For other collections, try common document patterns
            elif collection_name == 'global_mines':
                mine_ids = [
                    "gold_creek_main", "coloma_bar", "yuba_bend", "auburn_ravine",
                    "mokelumne_cut", "jamestown_flats", "placerville_reef"
                ]
                for mine_id in mine_ids:
                    try:
                        doc = collection_ref.document(mine_id).get()
                        if doc.exists:
                            data = doc.to_dict()
                            data['_document_id'] = doc.id
                            docs.append(data)
                    except:
                        continue
            
            # For leaderboard, try user-based document IDs
            elif collection_name == 'leaderboard':
                test_ids = ['mwill1003@gmail.com_mo', 'snow.turkeys.1j@icloud.com_safe']
                for doc_id in test_ids:
                    try:
                        doc = collection_ref.document(doc_id).get()
                        if doc.exists:
                            data = doc.to_dict()
                            data['_document_id'] = doc.id
                            docs.append(data)
                    except:
                        continue
            
            if docs:
                # Flatten nested data and prepare for CSV
                flattened_docs = []
                all_keys = set()
                
                for doc in docs:
                    flattened = flatten_dict(doc)
                    flattened_docs.append(flattened)
                    all_keys.update(flattened.keys())
                
                # Write to CSV
                csv_file = os.path.join(export_dir, f"{collection_name}.csv")
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    writer.writerows(flattened_docs)
                
                print(f"  ✅ Exported {len(docs)} documents to {collection_name}.csv")
            else:
                print(f"  ⚠️  No documents found in {collection_name}")
                
        except Exception as e:
            print(f"  ❌ Error exporting {collection_name}: {e}")
    
    # Export user subcollections (characters, saves)
    print(f"\n📊 Exporting user subcollections...")
    
    test_emails = ['mwill1003@gmail.com', 'snow.turkeys.1j@icloud.com']
    
    for email in test_emails:
        print(f"\n👤 Checking user: {email}")
        
        # Export characters
        try:
            user_ref = firebase_service.db.collection('users').document(email)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                character_names = user_data.get('character_names', [])
                
                if character_names:
                    chars_ref = user_ref.collection('characters')
                    character_docs = []
                    
                    for char_name in character_names:
                        char_doc = chars_ref.document(char_name).get()
                        if char_doc.exists:
                            data = char_doc.to_dict()
                            data['_document_id'] = char_doc.id
                            data['_user_email'] = email
                            character_docs.append(data)
                    
                    if character_docs:
                        # Flatten and export characters
                        flattened_chars = []
                        all_keys = set()
                        
                        for doc in character_docs:
                            flattened = flatten_dict(doc)
                            flattened_chars.append(flattened)
                            all_keys.update(flattened.keys())
                        
                        csv_file = os.path.join(export_dir, f"characters_{email.replace('@', '_').replace('.', '_')}.csv")
                        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                            writer.writeheader()
                            writer.writerows(flattened_chars)
                        
                        print(f"  ✅ Exported {len(character_docs)} characters for {email}")
                
                # Export saves (try common save patterns)
                saves_ref = user_ref.collection('saves')
                save_patterns = ['autosave_', 'manual_save_']
                save_docs = []
                
                for pattern in save_patterns:
                    for i in range(10):  # Try 10 variations
                        try:
                            save_name = f"{pattern}{i}"
                            save_doc = saves_ref.document(save_name).get()
                            if save_doc.exists:
                                data = save_doc.to_dict()
                                data['_document_id'] = save_doc.id
                                data['_user_email'] = email
                                save_docs.append(data)
                        except:
                            continue
                
                if save_docs:
                    csv_file = os.path.join(export_dir, f"saves_{email.replace('@', '_').replace('.', '_')}.csv")
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=save_docs[0].keys())
                        writer.writeheader()
                        writer.writerows(save_docs)
                    
                    print(f"  ✅ Exported {len(save_docs)} saves for {email}")
        
        except Exception as e:
            print(f"  ❌ Error exporting data for {email}: {e}")
    
    print(f"\n🎉 Export complete! Files saved to: {export_dir}")
    return export_dir

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary for CSV export"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to JSON strings
            items.append((new_key, json.dumps(v)))
        elif hasattr(v, 'isoformat'):  # datetime objects
            items.append((new_key, v.isoformat()))
        else:
            items.append((new_key, str(v) if v is not None else ''))
    
    return dict(items)

if __name__ == "__main__":
    export_firestore_to_csv()
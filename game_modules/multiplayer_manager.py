import streamlit as st
import datetime
import uuid
from typing import Dict, List, Optional
from .firebase_service import get_firebase_service

class MultiplayerServerManager:
    """Manages virtual servers with 4 players each"""
    
    def __init__(self):
        self.firebase_service = get_firebase_service()
        self.max_players_per_server = 4
    
    def find_or_create_server(self, player_email: str, character_name: str) -> str:
        """Always join the global server"""
        server_id = "global_server"
        
        try:
            # Check if global server exists
            server_ref = self.firebase_service.db.collection('multiplayer_servers').document(server_id)
            server_doc = server_ref.get()
            
            if not server_doc.exists:
                # Create global server
                self.create_server(server_id, player_email, character_name)
            else:
                # Join existing global server
                self.join_server(server_id, player_email, character_name)
            
            return server_id
            
        except Exception as e:
            st.error(f"Server error: {e}")
            return server_id
    
    def create_server(self, server_id: str, creator_email: str, character_name: str):
        """Create a new multiplayer server"""
        server_data = {
            'server_id': server_id,
            'created_at': datetime.datetime.now(),
            'created_by': creator_email,
            'players': {
                f"{creator_email}_{character_name}": {
                    'email': creator_email,
                    'character_name': character_name,
                    'joined_at': datetime.datetime.now(),
                    'last_active': datetime.datetime.now(),
                    'status': 'online'
                }
            },
            'game_state': {
                'turn': 1,
                'global_events': [],
                'shared_mines': {}
            }
        }
        
        self.firebase_service.db.collection('multiplayer_servers').document(server_id).set(server_data)
    
    def join_server(self, server_id: str, player_email: str, character_name: str):
        """Join existing server"""
        server_ref = self.firebase_service.db.collection('multiplayer_servers').document(server_id)
        server_doc = server_ref.get()
        
        if server_doc.exists:
            server_data = server_doc.to_dict()
            players = server_data.get('players', {})
            
            player_key = f"{player_email}_{character_name}"
            players[player_key] = {
                'email': player_email,
                'character_name': character_name,
                'joined_at': datetime.datetime.now(),
                'last_active': datetime.datetime.now(),
                'status': 'online'
            }
            
            server_ref.update({'players': players})
    
    def get_player_server(self, player_email: str, character_name: str) -> Optional[str]:
        """Always return global server"""
        return "global_server"
    
    def get_server_players(self, server_id: str) -> List[Dict]:
        """Get all players in a server"""
        try:
            server_ref = self.firebase_service.db.collection('multiplayer_servers').document(server_id)
            server_doc = server_ref.get()
            
            if server_doc.exists:
                server_data = server_doc.to_dict()
                players = server_data.get('players', {})
                return list(players.values())
            
            return []
        except:
            return []
    
    def update_player_activity(self, server_id: str, player_email: str, character_name: str):
        """Update player's last activity"""
        try:
            player_key = f"{player_email}_{character_name}"
            server_ref = self.firebase_service.db.collection('multiplayer_servers').document(server_id)
            server_ref.update({
                f'players.{player_key}.last_active': datetime.datetime.now(),
                f'players.{player_key}.status': 'online'
            })
        except:
            pass
    
    def leave_server(self, server_id: str, player_email: str, character_name: str):
        """Leave server"""
        try:
            player_key = f"{player_email}_{character_name}"
            server_ref = self.firebase_service.db.collection('multiplayer_servers').document(server_id)
            server_ref.update({
                f'players.{player_key}.status': 'offline',
                f'players.{player_key}.left_at': datetime.datetime.now()
            })
        except:
            pass
    
    def broadcast_message(self, server_id: str, sender_email: str, sender_name: str, message: str):
        """Broadcast message to all players in server"""
        try:
            message_data = {
                'sender_email': sender_email,
                'sender_name': sender_name,
                'message': message,
                'timestamp': datetime.datetime.now(),
                'message_id': uuid.uuid4().hex[:8]
            }
            
            self.firebase_service.db.collection('multiplayer_servers').document(server_id).collection('chat').add(message_data)
        except:
            pass
    
    def get_server_chat(self, server_id: str, limit: int = 20) -> List[Dict]:
        """Get recent chat messages"""
        try:
            chat_ref = self.firebase_service.db.collection('multiplayer_servers').document(server_id).collection('chat')
            messages = []
            
            # Get recent messages (simplified since we can't use orderBy)
            for i in range(limit):
                try:
                    doc = chat_ref.document(f"msg_{i}").get()
                    if doc.exists:
                        messages.append(doc.to_dict())
                except:
                    continue
            
            return messages[-limit:] if messages else []
        except:
            return []

# Global instance
multiplayer_manager = MultiplayerServerManager()

def get_multiplayer_manager():
    """Get the global multiplayer manager"""
    return multiplayer_manager
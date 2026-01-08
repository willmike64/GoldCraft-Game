import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import datetime
from typing import Dict, Any, List, Optional

class FirebaseService:
    def __init__(self):
        self.db = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase connection using existing secrets."""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try to use the JSON file path first
                if "FIREBASE_SERVICE_ACCOUNT_PATH" in st.secrets:
                    json_path = st.secrets["FIREBASE_SERVICE_ACCOUNT_PATH"]
                    cred = credentials.Certificate(json_path)
                    firebase_admin.initialize_app(cred)
                # Fallback to individual config fields
                elif all(key in st.secrets for key in ["FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL"]):
                    firebase_config = {
                        "type": "service_account",
                        "project_id": st.secrets["FIREBASE_PROJECT_ID"],
                        "private_key_id": st.secrets["FIREBASE_PRIVATE_KEY_ID"],
                        "private_key": st.secrets["FIREBASE_PRIVATE_KEY"],
                        "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
                        "client_id": st.secrets["FIREBASE_CLIENT_ID"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                else:
                    st.error("Firebase configuration not found in secrets.")
                    return
            
            self.db = firestore.client()
            
        except Exception as e:
            st.error(f"Failed to initialize Firebase: {str(e)}")
            self.db = None
    
    def is_authorized_email(self, email: str) -> bool:
        """Allow any valid email address."""
        return True  # Allow all emails
    
    def create_user(self, email: str, password_hash: str = None, prospector_name: str = None) -> bool:
        """Create a new user in Firestore."""
        if not self.db or not self.is_authorized_email(email):
            return False
        
        try:
            user_ref = self.db.collection('users').document(email)
            
            # Check if user already exists
            existing_user = user_ref.get()
            if existing_user.exists and existing_user.to_dict().get('password_hash'):
                return False  # User already exists with password
            
            user_data = {
                'email': email,
                'created_at': datetime.datetime.now(),
                'last_login': datetime.datetime.now(),
                'total_games': 0,
                'authorized': True
            }
            if password_hash:
                user_data['password_hash'] = password_hash
            if prospector_name:
                user_data['prospector_name'] = prospector_name
            
            user_ref.set(user_data)
            return True
        except Exception as e:
            st.error(f"Failed to create user: {str(e)}")
            return False
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user data from Firestore with authorization check."""
        if not self.db:
            return None
        
        # Check if email is authorized
        if not self.is_authorized_email(email):
            return None
        
        try:
            user_ref = self.db.collection('users').document(email)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                # Update last login only if user has password (authenticated user)
                user_data = user_doc.to_dict()
                if user_data.get('password_hash'):
                    user_ref.update({'last_login': datetime.datetime.now()})
                return user_data
            else:
                # Don't auto-create users anymore - they must register with password
                return None
        except Exception as e:
            st.error(f"Failed to get user: {str(e)}")
            return None
    
    def update_user_password(self, email: str, password_hash: str) -> bool:
        """Update user password hash."""
        if not self.db:
            return False
        
        try:
            user_ref = self.db.collection('users').document(email)
            user_ref.update({'password_hash': password_hash})
            return True
        except Exception as e:
            st.error(f"Failed to update password: {str(e)}")
            return False
    
    def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create a password reset token for the user."""
        if not self.db or not self.is_authorized_email(email):
            return None
        
        try:
            import secrets
            import hashlib
            
            # Generate secure token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Store token with expiration (1 hour)
            reset_data = {
                'email': email,
                'token_hash': token_hash,
                'created_at': datetime.datetime.now(),
                'expires_at': datetime.datetime.now() + datetime.timedelta(hours=1),
                'used': False
            }
            
            self.db.collection('password_resets').document(token).set(reset_data)
            return token
        except Exception as e:
            st.error(f"Failed to create reset token: {str(e)}")
            return None
    
    def verify_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return email if valid."""
        if not self.db:
            return None
        
        try:
            reset_ref = self.db.collection('password_resets').document(token)
            reset_doc = reset_ref.get()
            
            if not reset_doc.exists:
                return None
            
            reset_data = reset_doc.to_dict()
            
            # Check if token is expired or used
            if reset_data.get('used', True) or reset_data.get('expires_at') < datetime.datetime.now():
                return None
            
            return reset_data.get('email')
        except Exception as e:
            return None
    
    def use_reset_token(self, token: str, new_password_hash: str) -> bool:
        """Use reset token to update password."""
        if not self.db:
            return False
        
        try:
            email = self.verify_reset_token(token)
            if not email:
                return False
            
            # Update password
            if self.update_user_password(email, new_password_hash):
                # Mark token as used
                reset_ref = self.db.collection('password_resets').document(token)
                reset_ref.update({'used': True})
                return True
            
            return False
        except Exception as e:
            return False
    
    def update_user_profile(self, email: str, prospector_name: str = None, faction_choice: str = None, is_rogue: bool = None) -> bool:
        """Update user profile information."""
        if not self.db:
            return False
        
        try:
            user_ref = self.db.collection('users').document(email)
            update_data = {}
            if prospector_name:
                update_data['prospector_name'] = prospector_name
            if faction_choice:
                update_data['faction_choice'] = faction_choice
            if is_rogue is not None:
                update_data['is_rogue'] = is_rogue
            
            if update_data:
                user_ref.update(update_data)
            return True
        except Exception as e:
            st.error(f"Failed to update profile: {str(e)}")
            return False
    
    def save_game(self, email: str, save_name: str, game_state: Dict[str, Any]) -> bool:
        """Save game state to Firestore with comprehensive data."""
        if not self.db:
            return False
        
        try:
            # Get user data for prospector name
            user_data = self.get_user(email)
            prospector_name = user_data.get('prospector_name', 'Unknown') if user_data else 'Unknown'
            
            # Prepare comprehensive save data
            save_data = {
                'save_name': save_name,
                'email': email,
                'prospector_name': prospector_name,
                'game_state': game_state,
                'saved_at': datetime.datetime.now(),
                'turn': game_state.get('turn', 1),
                'gold': game_state.get('gold', 50),
                'reputation': game_state.get('reputation', {}),
                'equipment': game_state.get('equipment', {}),
                'supplies': game_state.get('supplies', {}),
                'faction_negotiations': game_state.get('faction_negotiations', {}),
                'visited_sites': game_state.get('visited_sites', []),
                'current_view': game_state.get('current_view', 'menu'),
                'is_rogue': game_state.get('is_rogue', False),
                'equipment_cost_multiplier': game_state.get('equipment_cost_multiplier', 1.0),
                'reputation_penalty': game_state.get('reputation_penalty', 1.0)
            }
            
            # Save to user's saves collection
            save_ref = self.db.collection('users').document(email).collection('saves').document(save_name)
            save_ref.set(save_data)
            
            # Log comprehensive activity for big data
            self.log_game_action(email, 'game_saved', {
                'save_name': save_name,
                'prospector_name': prospector_name,
                'turn': game_state.get('turn', 1),
                'gold': game_state.get('gold', 50),
                'total_reputation': sum(game_state.get('reputation', {}).values()),
                'equipment_count': len([k for k, v in game_state.get('equipment', {}).items() if v]),
                'supply_count': sum(game_state.get('supplies', {}).values()),
                'sites_visited': len(game_state.get('visited_sites', [])),
                'is_rogue': game_state.get('is_rogue', False)
            })
            
            return True
        except Exception as e:
            st.error(f"Failed to save game: {str(e)}")
            return False
    
    def load_game(self, email: str, save_name: str) -> Optional[Dict[str, Any]]:
        """Load game state from Firestore."""
        if not self.db:
            return None
        
        try:
            save_ref = self.db.collection('users').document(email).collection('saves').document(save_name)
            save_doc = save_ref.get()
            
            if save_doc.exists:
                save_data = save_doc.to_dict()
                # Log activity
                self.log_activity(email, 'game_loaded', {'save_name': save_name})
                return save_data.get('game_state', {})
            return None
        except Exception as e:
            st.error(f"Failed to load game: {str(e)}")
            return None
    
    def get_user_saves(self, email: str) -> List[Dict]:
        """Get all saves for a user."""
        if not self.db:
            return []
        
        try:
            saves_ref = self.db.collection('users').document(email).collection('saves')
            saves = saves_ref.order_by('saved_at', direction=firestore.Query.DESCENDING).stream()
            
            save_list = []
            for save in saves:
                save_data = save.to_dict()
                save_list.append({
                    'name': save_data.get('save_name', 'Unknown'),
                    'saved_at': save_data.get('saved_at'),
                    'turn': save_data.get('turn', 1),
                    'gold': save_data.get('gold', 0)
                })
            
            return save_list
        except Exception as e:
            st.error(f"Failed to get saves: {str(e)}")
            return []
    
    def delete_save(self, email: str, save_name: str) -> bool:
        """Delete a game save."""
        if not self.db:
            return False
        
        try:
            save_ref = self.db.collection('users').document(email).collection('saves').document(save_name)
            save_ref.delete()
            
            # Log activity
            self.log_activity(email, 'game_deleted', {'save_name': save_name})
            
            return True
        except Exception as e:
            st.error(f"Failed to delete save: {str(e)}")
            return False
    
    def log_activity(self, email: str, activity_type: str, data: Dict[str, Any] = None):
        """Log user activity."""
        if not self.db:
            return
        
        try:
            activity_data = {
                'email': email,
                'activity_type': activity_type,
                'timestamp': datetime.datetime.now(),
                'data': data or {}
            }
            
            self.db.collection('activities').add(activity_data)
        except Exception as e:
            # Don't show errors for activity logging to avoid spam
            pass
    
    def auto_save_game(self, email: str, game_state: Dict[str, Any]):
        """Auto-save current game state."""
        auto_save_name = f"autosave_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Keep only last 5 auto-saves
        saves = self.get_user_saves(email)
        auto_saves = [s for s in saves if s['name'].startswith('autosave_')]
        
        if len(auto_saves) >= 5:
            # Delete oldest auto-save
            oldest_save = sorted(auto_saves, key=lambda x: x['saved_at'])[0]
            self.delete_save(email, oldest_save['name'])
        
    def log_game_action(self, email: str, action_type: str, data: Dict[str, Any] = None):
        """Log detailed game actions for big data analytics."""
        if not self.db:
            return
        
        try:
            # Get user data for prospector name
            user_data = self.get_user(email)
            prospector_name = user_data.get('prospector_name', 'Unknown') if user_data else 'Unknown'
            
            action_data = {
                'email': email,
                'prospector_name': prospector_name,
                'action_type': action_type,
                'timestamp': datetime.datetime.now(),
                'session_id': f"{email}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'data': data or {},
                'user_agent': 'streamlit_app',
                'game_version': '1.0'
            }
            
            # Store in both activities and game_actions collections for different analytics
            self.db.collection('activities').add(action_data)
            self.db.collection('game_actions').add(action_data)
            
        except Exception as e:
            # Don't show errors for activity logging to avoid spam
            pass
    
    def get_live_stats(self) -> Dict[str, Any]:
        """Get live statistics from Firebase."""
        if not self.db:
            return {'active_prospectors': 0, 'gold_today': 0, 'richest_strike': 'Unknown (0 oz)'}
        
        try:
            # Count active users (logged in within last 24 hours)
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            users_ref = self.db.collection('users')
            active_users = users_ref.where('last_login', '>=', yesterday).stream()
            active_count = len(list(active_users))
            
            # Get today's gold extraction from activities
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            activities_ref = self.db.collection('activities')
            mining_activities = activities_ref.where('activity_type', '==', 'gold_mined').where('timestamp', '>=', today).stream()
            
            total_gold_today = 0
            richest_strike = 0
            richest_location = 'Unknown'
            
            for activity in mining_activities:
                data = activity.to_dict().get('data', {})
                gold_amount = data.get('gold_found', 0)
                total_gold_today += gold_amount
                
                if gold_amount > richest_strike:
                    richest_strike = gold_amount
                    richest_location = data.get('location', 'Unknown')
            
            return {
                'active_prospectors': active_count,
                'gold_today': total_gold_today,
                'richest_strike': f"{richest_location} ({richest_strike:.1f} oz)"
            }
            
        except Exception as e:
            # Return default values on error
            return {'active_prospectors': 0, 'gold_today': 0, 'richest_strike': 'Unknown (0 oz)'}
    
    def get_user_prospector_names(self, email: str) -> List[str]:
        """Get all prospector names for a user."""
        if not self.db:
            return []
        
        try:
            prospectors_ref = self.db.collection('users').document(email).collection('prospectors')
            prospectors = prospectors_ref.stream()
            
            names = []
            for prospector in prospectors:
                names.append(prospector.id)
            
            return names
        except Exception as e:
            return []
    
    def create_prospector(self, email: str, prospector_name: str, prospector_data: Dict[str, Any]) -> bool:
        """Create a new prospector for a user."""
        if not self.db:
            return False
        
        try:
            prospector_ref = self.db.collection('users').document(email).collection('prospectors').document(prospector_name)
            prospector_data['created_at'] = datetime.datetime.now()
            prospector_ref.set(prospector_data)
            return True
        except Exception as e:
            return False
    
    def get_prospector_data(self, email: str, prospector_name: str) -> Optional[Dict]:
        """Get data for a specific prospector."""
        if not self.db:
            return None
        
        try:
            prospector_ref = self.db.collection('users').document(email).collection('prospectors').document(prospector_name)
            prospector_doc = prospector_ref.get()
            
            if prospector_doc.exists:
                return prospector_doc.to_dict()
            return None
        except Exception as e:
            return None
    
    def update_leaderboard_stats(self, email: str, prospector_name: str, gold: int, turn: int):
        """Update leaderboard statistics for a player."""
        if not self.db:
            return
        
        try:
            leaderboard_ref = self.db.collection('leaderboard').document(f"{email}_{prospector_name}")
            
            # Get existing data or create new
            existing = leaderboard_ref.get()
            if existing.exists:
                data = existing.to_dict()
                # Update with better stats
                data['gold'] = max(data.get('gold', 0), gold)
                data['turn'] = max(data.get('turn', 0), turn)
                data['last_updated'] = datetime.datetime.now()
            else:
                data = {
                    'email': email,
                    'prospector_name': prospector_name,
                    'gold': gold,
                    'turn': turn,
                    'created_at': datetime.datetime.now(),
                    'last_updated': datetime.datetime.now()
                }
            
            leaderboard_ref.set(data)
        except Exception as e:
            pass  # Silent fail for leaderboard updates
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players for leaderboard."""
        if not self.db:
            return []
        
        try:
            leaderboard_ref = self.db.collection('leaderboard')
            # Order by gold descending, then by turn ascending (fewer turns = better)
            results = leaderboard_ref.order_by('gold', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            leaderboard = []
            for doc in results:
                data = doc.to_dict()
                leaderboard.append({
                    'prospector_name': data.get('prospector_name', 'Unknown'),
                    'gold': data.get('gold', 0),
                    'turn': data.get('turn', 0),
                    'last_updated': data.get('last_updated')
                })
            
            return leaderboard
        except Exception as e:
            return []
    
    def mine_gold(self, mine_id: str, amount: float, miner: str) -> bool:
        """Record gold mining activity"""
        try:
            self.log_activity(miner, 'gold_mined', {
                'mine_id': mine_id,
                'amount': amount,
                'location': mine_id
            })
            return True
        except:
            return False
    
    def get_mine_status(self, mine_id: str) -> dict:
        """Get basic mine status"""
        return {'current_reserves': 1000, 'total_mined': 0, 'active_miners': 0}
    
    def initialize_mine_reserves(self, mine_id: str, initial_gold: float) -> bool:
        """Initialize mine reserves"""
        return True
    
    def get_mine_activity(self, mine_id: str, limit: int = 10) -> list:
        """Get recent mining activity"""
        return []

# Global Firebase service instance
firebase_service = FirebaseService()

def get_firebase_service():
    """Get the global Firebase service instance."""
    return firebase_service
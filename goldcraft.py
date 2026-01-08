import streamlit as st
import sys
import os
import random
import uuid
import hashlib
import secrets
import datetime
from game_modules.firebase_service import get_firebase_service
from game_modules.analytics_service import analytics
from game_modules.ui_styles import apply_global_styles

# --------------------------------------------------
# Firebase Service
# --------------------------------------------------
firebase_service = get_firebase_service()

# --------------------------------------------------
# Path setup
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# --------------------------------------------------
# Authentication Functions
# --------------------------------------------------
def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{password_hash.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, hash_hex = stored_hash.split(':')
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex() == hash_hex
    except:
        return False

def create_session_token(email: str) -> str:
    """Create persistent session token."""
    token_data = f"{email}:{datetime.datetime.now().isoformat()}:{secrets.token_hex(16)}"
    return hashlib.sha256(token_data.encode()).hexdigest()

def store_session_token(email: str, token: str):
    """Store session token in Firebase."""
    try:
        firebase_service.db.collection('sessions').document(token).set({
            'email': email,
            'created_at': datetime.datetime.now(),
            'expires_at': datetime.datetime.now() + datetime.timedelta(days=30),
            'active': True
        })
        # Store in browser localStorage via session state
        st.session_state['auth_token'] = token
    except:
        pass

def validate_session_token(token: str) -> str:
    """Validate session token and return email if valid."""
    try:
        session_ref = firebase_service.db.collection('sessions').document(token)
        session_doc = session_ref.get()
        
        if session_doc.exists:
            session_data = session_doc.to_dict()
            if (session_data.get('active', False) and 
                session_data.get('expires_at') > datetime.datetime.now()):
                return session_data.get('email')
    except:
        pass
    return None

def clear_session_token(token: str):
    """Clear session token from Firebase."""
    try:
        firebase_service.db.collection('sessions').document(token).update({'active': False})
    except:
        pass
def generate_prospector_name(email):
    """Generate a consistent funny prospector name based on email."""
    random.seed(email)
    first_names = ["Pickaxe", "Nugget", "Dusty", "Lucky", "Rusty", "Goldie", "Muddy", "Sifty", "Digger", "Panner"]
    last_names = ["McStrike", "Golddigger", "Pansworth", "Nuggetson", "Creekwater", "Boomtown", "Prospector", "Mineshaft", "Goldpan", "Picksworth"]
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    random.seed()
    return name

def check_authentication():
    """Check if user is authenticated via session token or login."""
    # Check for existing session token
    if 'auth_token' in st.session_state:
        email = validate_session_token(st.session_state['auth_token'])
        if email:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            # Get prospector name
            user_data = firebase_service.get_user(email)
            if user_data:
                st.session_state.prospector_name = user_data.get('prospector_name', 'Unknown')
            return True
        else:
            # Invalid token, clear it
            if 'auth_token' in st.session_state:
                del st.session_state['auth_token']
    
    # Check session state authentication
    if st.session_state.get('authenticated', False):
        return True
    
    render_login_page()
    return False

def render_login_page():
    """Render enhanced login page with password authentication."""
    # Apply unified styles
    apply_global_styles()
    
    # Enhanced styling for login page
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 246, 240, 0.98));
        border: 3px solid #DAA520;
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 600px;
        box-shadow: 0 0 30px rgba(218, 165, 32, 0.4);
        color: #2c2c2c !important;
    }
    
    .login-header {
        color: #DAA520;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
    }
    
    .subtitle {
        color: #8B4513;
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .prospector-quote {
        background: rgba(255, 255, 255, 0.9);
        border-left: 5px solid #DAA520;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 2rem 0;
        font-style: italic;
        color: #2c2c2c !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .stats-ticker {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #DAA520;
        border-radius: 10px;
        padding: 1rem;
        margin: 1.5rem 0;
        color: #2c2c2c !important;
        font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero section with container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Epic header with mining animation
    st.markdown('<h1 class="login-header">⛏️ GOLDCRAFT ⛏️</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">DIMENSIONAL EARTH MINING EXPEDITION</p>', unsafe_allow_html=True)
    
    # Atmospheric quote
    st.markdown("""
    <div class="prospector-quote">
    "🌅 Gold Creek, California - 1849. The earth trembles with untold riches. 
    Fortunes are made and lost in the span of a pickaxe swing. 
    Will you strike it rich in the dimensional mines, or will the mountain claim another soul? 🌆"
    </div>
    """, unsafe_allow_html=True)
    
    # Live stats ticker
    st.markdown("""
    <div class="stats-ticker">
    📊 LIVE MINING DATA: Active Prospectors: 1,247 | Gold Extracted Today: 15,832.7 oz | Richest Strike: Nugget McStrike (2,847 oz) | Danger Level: EXTREME
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🚪 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### 🎯 ENTER THE GOLD FIELDS")
        with st.form("login_form"):
            email = st.text_input("📧 Prospector Email", placeholder="goldseeker@frontier.com")
            password = st.text_input("🔐 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("🔒 Remember me for 30 days")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button("🚪 LOGIN", width='stretch')
            with col2:
                forgot_password = st.form_submit_button("🔑 Forgot Password", width='stretch')
            
            if login_submitted and email and password:
                user_data = firebase_service.get_user(email)
                if user_data and user_data.get('password_hash'):
                    if verify_password(password, user_data['password_hash']):
                        # Successful login
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.prospector_name = user_data.get('prospector_name', 'Unknown')
                        st.session_state['game_loaded'] = False
                        
                        # Create persistent session if remember me is checked
                        if remember_me:
                            token = create_session_token(email)
                            store_session_token(email, token)
                        
                        analytics.log_login(email)
                        st.success(f"🎉 Welcome back, {user_data.get('prospector_name', 'Prospector')}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid password!")
                else:
                    st.error("❌ Account not found! Please register first.")
            
            if forgot_password and email:
                # TODO: Implement password reset
                st.info("🔑 Password reset feature coming soon!")
    
    with tab2:
        st.markdown("### ✨ FORGE YOUR LEGEND")
        with st.form("register_form"):
            reg_email = st.text_input("📧 Email", placeholder="newprospector@frontier.com")
            reg_password = st.text_input("🔐 Password", type="password", placeholder="Create a strong password")
            reg_password_confirm = st.text_input("🔐 Confirm Password", type="password", placeholder="Confirm your password")
            
            register_submitted = st.form_submit_button("⚡ CREATE ACCOUNT", width='stretch')
            
            if register_submitted and reg_email and reg_password and reg_password_confirm:
                # Debug information
                st.write("🔍 Debug Info:")
                st.write(f"Email: {reg_email}")
                st.write(f"Password length: {len(reg_password)}")
                st.write(f"Passwords match: {reg_password == reg_password_confirm}")
                st.write(f"Firebase service available: {firebase_service is not None}")
                st.write(f"Firebase DB available: {firebase_service.db is not None if firebase_service else 'No service'}")
                
                if reg_password != reg_password_confirm:
                    st.error("❌ Passwords don't match!")
                elif len(reg_password) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                else:
                    # Check if user already exists
                    st.write("🔍 Checking if user exists...")
                    try:
                        existing_user = firebase_service.get_user(reg_email)
                        st.write(f"Existing user check result: {existing_user is not None}")
                        if existing_user:
                            st.write(f"User data: {existing_user}")
                    except Exception as e:
                        st.error(f"Error checking existing user: {str(e)}")
                        existing_user = None
                    
                    if existing_user and existing_user.get('password_hash'):
                        st.error("❌ Account already exists! Please login instead.")
                    else:
                        # Create new account
                        st.write("🔍 Creating new account...")
                        try:
                            password_hash = hash_password(reg_password)
                            st.write(f"Password hashed successfully: {len(password_hash)} chars")
                            
                            prospector_name = generate_prospector_name(reg_email)
                            st.write(f"Generated prospector name: {prospector_name}")
                            
                            create_result = firebase_service.create_user(reg_email, password_hash, prospector_name)
                            st.write(f"User creation result: {create_result}")
                            
                            if create_result:
                                st.write("🔍 Creating prospector...")
                                prospector_result = firebase_service.create_prospector(reg_email, prospector_name, {
                                    'prospector_name': prospector_name,
                                    'created_at': datetime.datetime.now().isoformat()
                                })
                                st.write(f"Prospector creation result: {prospector_result}")
                                
                                st.session_state.authenticated = True
                                st.session_state.user_email = reg_email
                                st.session_state.prospector_name = prospector_name
                                st.session_state['game_loaded'] = False
                                
                                # Create session token
                                token = create_session_token(reg_email)
                                store_session_token(reg_email, token)
                                
                                analytics.log_action(reg_email, "register", {"prospector_name": prospector_name})
                                st.balloons()
                                st.success(f"🎉 Welcome to the frontier, {prospector_name}!")
                                st.rerun()
                            else:
                                st.error("❌ Registration failed! Please try again.")
                        except Exception as e:
                            st.error(f"❌ Registration error: {str(e)}")
                            st.write(f"Full error details: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Imports
# --------------------------------------------------
from game_modules.gold_map_folium import render_gold_map_folium
from game_modules.town_hub_merged import render_town_hub
from game_modules.statistics import render_statistics
from game_modules.menu import render_game_menu

# --------------------------------------------------
# Page Config (must be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="⛏️ GoldCraft | Dimensional Mining Expedition",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Global Styling
# --------------------------------------------------
# Apply unified styles at app startup
apply_global_styles()

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------
def init_session_state():
    """Initialize session state, loading from save if available."""
    # Generate session ID for analytics
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Test Firebase connection
    if 'firebase_status' not in st.session_state:
        try:
            test_user = firebase_service.get_user("test@example.com")
            st.session_state.firebase_status = "connected"
            st.sidebar.success("🔥 Firebase Connected")
        except Exception as e:
            st.session_state.firebase_status = "offline"
            st.sidebar.error(f"🔥 Firebase Offline: {str(e)[:50]}...")
    
    # Only initialize if not already loaded
    if not st.session_state.get('game_loaded', False):
        # Try to load the most recent save
        if st.session_state.get('user_email') and st.session_state.get('prospector_name'):
            saved_state = load_most_recent_save()
            if saved_state:
                # Load saved game state
                for key, value in saved_state.items():
                    if key == 'visited_sites' and isinstance(value, list):
                        st.session_state[key] = set(value)
                    else:
                        st.session_state[key] = value
                st.session_state['game_loaded'] = True
                st.sidebar.info(f"💾 Game state loaded successfully!")
                return
        
        # Default initialization for new players
        defaults = {
            "current_view": "menu",
            "current_strata": "Surface",
            "depth_layer": "Surface",
            "gold": 50,
            "reputation": {},
            "visited_sites": set(),
            "turn": 1,
            "equipment": {"Basic Pickaxe": True, "Canvas Satchel": True, "Work Clothes": True},
            "supplies": {},
            "faction_negotiations": {},
            "level": 1,
            "xp": 0,
            "selected_faction": None,
            "faction_benefits": {},
            "game_loaded": True
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        if st.session_state.get('user_email'):
            if st.session_state.firebase_status == "connected":
                st.sidebar.info("🆕 New game started with Firebase sync")
            else:
                st.sidebar.warning("🆕 New game started (offline mode)")

def load_most_recent_save():
    """Load the most recent save for the current user."""
    try:
        email = st.session_state.get('user_email')
        
        if not email:
            return None
            
        saves = firebase_service.get_user_saves(email)
        if saves:
            # Get the most recent save (first in the list since they're ordered by date)
            most_recent = saves[0]['name']
            loaded_state = firebase_service.load_game(email, most_recent)
            if loaded_state:
                st.sidebar.success(f"✅ Loaded save: {most_recent}")
                return loaded_state
    except Exception as e:
        st.sidebar.error(f"Error loading save: {e}")
    return None

def auto_save_game():
    """Auto-save current game state to a persistent save file."""
    try:
        email = st.session_state.get('user_email')
        prospector_name = st.session_state.get('prospector_name')
        if not email or not prospector_name:
            return False
            
        # Use a consistent save name for auto-saves
        save_name = f"autosave_{prospector_name}"
        
        # Prepare game state
        game_state = {
            'current_view': st.session_state.get('current_view', 'menu'),
            'current_strata': st.session_state.get('current_strata', 'Surface'),
            'depth_layer': st.session_state.get('depth_layer', 'Surface'),
            'gold': st.session_state.get('gold', 50),
            'reputation': st.session_state.get('reputation', {}),
            'visited_sites': list(st.session_state.get('visited_sites', set())),
            'turn': st.session_state.get('turn', 1),
            'equipment': st.session_state.get('equipment', {}),
            'supplies': st.session_state.get('supplies', {}),
            'faction_negotiations': st.session_state.get('faction_negotiations', {}),
            'level': st.session_state.get('level', 1),
            'xp': st.session_state.get('xp', 0),
            'selected_faction': st.session_state.get('selected_faction'),
            'faction_benefits': st.session_state.get('faction_benefits', {})
        }
        
        # Update leaderboard stats
        firebase_service.update_leaderboard_stats(
            email, prospector_name,
            int(st.session_state.get('gold', 50)),
            st.session_state.get('turn', 1)
        )
        
        # Save to Firebase (overwrites existing autosave)
        result = firebase_service.save_game(email, save_name, game_state)
        return result
    except Exception as e:
        return False

def save_current_game():
    """Manual save function for menu.py."""
    try:
        email = st.session_state.get('user_email')
        prospector_name = st.session_state.get('prospector_name')
        if not email or not prospector_name:
            st.sidebar.error("Not logged in properly!")
            return False
        
        # Check Firebase service
        if not firebase_service or not firebase_service.db:
            st.sidebar.error("Firebase not connected!")
            return False
            
        import datetime
        save_name = f"manual_save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare game state
        game_state = {
            'current_view': st.session_state.get('current_view', 'menu'),
            'current_strata': st.session_state.get('current_strata', 'Surface'),
            'depth_layer': st.session_state.get('depth_layer', 'Surface'),
            'gold': st.session_state.get('gold', 50),
            'reputation': st.session_state.get('reputation', {}),
            'visited_sites': list(st.session_state.get('visited_sites', set())),
            'turn': st.session_state.get('turn', 1),
            'equipment': st.session_state.get('equipment', {}),
            'supplies': st.session_state.get('supplies', {}),
            'faction_negotiations': st.session_state.get('faction_negotiations', {})
        }
        
        # Update leaderboard
        firebase_service.update_leaderboard_stats(
            email, prospector_name, 
            int(st.session_state.get('gold', 50)), 
            st.session_state.get('turn', 1)
        )
        
        # Save to Firebase
        result = firebase_service.save_game(email, save_name, game_state)
        if result:
            st.sidebar.success(f"Saved as {save_name}")
        return result
    except Exception as e:
        st.sidebar.error(f"Save failed: {str(e)}")
        return False


# --------------------------------------------------
# Sidebar Navigation (Game Control)
# --------------------------------------------------
def render_sidebar():
    st.sidebar.title("⛏️ GoldCraft")
    st.sidebar.caption("Dimensional Earth Mining")
    
    # Show logged in user and current character
    if st.session_state.get("user_email"):
        current_char = st.session_state.get('current_character', 'No Character')
        st.sidebar.info(f"👤 {current_char}")
        st.sidebar.caption(f"Account: {st.session_state.user_email}")
        
        # Multiplayer info
        from game_modules.multiplayer_ui import render_multiplayer_sidebar
        render_multiplayer_sidebar()
        
        # Character management
        if st.sidebar.button("⚔️ Switch Character"):
            # Save current character before switching
            from game_modules.character_manager import save_current_character
            if save_current_character():
                st.sidebar.success("💾 Character saved!")
            
            # Clear character state
            st.session_state.character_loaded = False
            if 'current_character' in st.session_state:
                del st.session_state['current_character']
            st.rerun()
        
        # Save/Load functionality
        st.sidebar.divider()
        st.sidebar.markdown("### 💾 Save & Load")
        
        # Get available saves
        email = st.session_state.get('user_email')
        if email:
            saves = firebase_service.get_user_saves(email)
            if saves:
                st.sidebar.info(f"Found {len(saves)} saved games")
                
                # Load button with selectbox
                if st.sidebar.button("📂 Load Game"):
                    st.session_state['show_load_menu'] = True
                
                # Show load menu if requested
                if st.session_state.get('show_load_menu', False):
                    save_names = [save['name'] for save in saves]
                    selected_save = st.sidebar.selectbox(
                        "Select Save:",
                        options=save_names,
                        key="load_save_selector"
                    )
                    
                    col1, col2 = st.sidebar.columns(2)
                    with col1:
                        if st.button("✅ Load", key="confirm_load"):
                            loaded_state = firebase_service.load_game(email, selected_save)
                            if loaded_state:
                                # Load the game state
                                for key, value in loaded_state.items():
                                    if key == 'visited_sites' and isinstance(value, list):
                                        st.session_state[key] = set(value)
                                    else:
                                        st.session_state[key] = value
                                st.sidebar.success(f"✅ Loaded: {selected_save}")
                                st.session_state['show_load_menu'] = False
                                st.rerun()
                            else:
                                st.sidebar.error("Failed to load game")
                    
                    with col2:
                        if st.button("❌ Cancel", key="cancel_load"):
                            st.session_state['show_load_menu'] = False
                            st.rerun()
                
                # Manual save button
                if st.sidebar.button("💾 Save Game"):
                    if save_current_game():
                        st.sidebar.success("Game saved!")
            else:
                st.sidebar.info("No saved games found")
        
        st.sidebar.info("Auto-saves every 5 turns")
        
        if st.sidebar.button("🚪 Logout"):
            # Auto-save current character before logout
            from game_modules.character_manager import save_current_character
            if save_current_character():
                st.sidebar.success("💾 Character saved before logout")
            
            # Clear session token if exists
            if 'auth_token' in st.session_state:
                clear_session_token(st.session_state['auth_token'])
            
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Admin panel access
    from game_modules.admin_panel import check_admin_access
    if check_admin_access():
        admin_options = ["menu", "map", "town", "stats", "admin"]
        admin_format = {
            "menu": "🏁 Main Menu",
            "map": "🗺️ Strata Map",
            "town": "🏘️ Town Hub",
            "stats": "📊 Expedition Stats",
            "admin": "🔧 Admin Panel"
        }
    else:
        admin_options = ["menu", "map", "town", "stats", "multiplayer"]
        admin_format = {
            "menu": "🏁 Main Menu",
            "map": "🗺️ Strata Map",
            "town": "🏘️ Town Hub",
            "stats": "📊 Expedition Stats",
            "multiplayer": "🌐 Multiplayer"
        }

    view = st.sidebar.radio(
        "Navigate",
        options=admin_options,
        format_func=lambda x: admin_format[x],
        index=admin_options.index(st.session_state.current_view) if st.session_state.current_view in admin_options else 0,
    )

    # Track navigation changes
    if view != st.session_state.current_view:
        analytics.log_action(st.session_state.get('user_email', 'unknown'), "navigate", {
            "from_view": st.session_state.current_view,
            "to_view": view
        })

    st.session_state.current_view = view

    st.sidebar.divider()

    st.sidebar.markdown("### ⏳ Expedition Turn")
    st.sidebar.metric("Turn", st.session_state.turn)

    # Level display
    from game_modules.leveling_system import render_level_display
    render_level_display()
    
    # Faction display
    faction = st.session_state.get('selected_faction')
    if faction:
        st.sidebar.markdown("### ⚔️ Faction")
        faction_data = {
            "Consortium": {"icon": "🧔", "race": "Dwarf", "name": "Dwarven Consortium"},
            "Independents": {"icon": "🤠", "race": "Human", "name": "Human Independents"}, 
            "Rogue Alliance": {"icon": "🧝", "race": "Irish Elf", "name": "Irish Elf Rogues"}
        }
        faction_info = faction_data.get(faction, {"icon": "⚔️", "race": "Unknown", "name": faction})
        st.sidebar.metric("Allegiance", f"{faction_info['icon']} {faction_info['name']}")
        st.sidebar.caption(f"Race: {faction_info['race']}")

    st.sidebar.markdown("### 💰 Gold Reserves")
    st.sidebar.metric("Gold", f"{st.session_state.gold:,}")
    
    # Multiplayer server info
    st.sidebar.divider()
    st.sidebar.markdown("### 🌐 Global Server")
    
    # Show global server status
    try:
        from game_modules.multiplayer_manager import get_multiplayer_manager
        multiplayer_manager = get_multiplayer_manager()
        
        server_id = "global_server"
        players = multiplayer_manager.get_server_players(server_id)
        
        st.sidebar.success(f"🟢 Connected to {server_id}")
        st.sidebar.metric("Online Players", len(players))
        
        # Show online players
        if players:
            with st.sidebar.expander("👥 Online Players"):
                for player in players[-5:]:  # Show last 5 players
                    status = "🟢" if player.get('status') == 'online' else "🔴"
                    st.write(f"{status} {player.get('character_name', 'Unknown')}")
        
        # Auto-join global server if not connected
        current_server = st.session_state.get('current_server')
        if current_server != server_id:
            email = st.session_state.get('user_email')
            character = st.session_state.get('current_character')
            if email and character:
                multiplayer_manager.join_server(server_id, email, character)
                st.session_state['current_server'] = server_id
    
    except Exception as e:
        st.sidebar.error(f"Server error: {e}")

# --------------------------------------------------
# Main Router
# --------------------------------------------------
def main():
    # Check authentication first
    if not check_authentication():
        return
        
    init_session_state()
    
    # Check character selection before faction selection
    from game_modules.character_manager import check_character_selection
    if not check_character_selection():
        return
    
    render_sidebar()
    
    # Auto-save current character every few turns (less frequent)
    current_turn = st.session_state.get('turn', 1)
    last_autosave_turn = st.session_state.get('last_autosave_turn', 0)
    
    # Auto-save every 5 turns instead of every turn
    if current_turn > last_autosave_turn and (current_turn - last_autosave_turn) >= 5:
        if st.session_state.get('current_character'):
            from game_modules.character_manager import save_current_character
            if save_current_character():
                st.session_state['last_autosave_turn'] = current_turn
                st.sidebar.info(f"🔄 Auto-saved at Turn {current_turn}")
    
    # Remove old quick load system - now using character system

    view = st.session_state.current_view

    if view == "menu":
        render_game_menu()

    elif view == "map":
        render_gold_map_folium()

    elif view == "town":
        render_town_hub()

    elif view == "stats":
        render_statistics()
        
    elif view == "multiplayer":
        from game_modules.multiplayer_ui import render_multiplayer_panel
        render_multiplayer_panel()
        
    elif view == "admin":
        from game_modules.admin_panel import render_admin_panel
        render_admin_panel()

    else:
        render_game_menu()


# --------------------------------------------------
# Entry Point
# --------------------------------------------------
if __name__ == "__main__":
    main()
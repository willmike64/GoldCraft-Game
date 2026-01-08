import streamlit as st
import datetime
from typing import Dict, List
from .character_manager import CharacterManager
from .firebase_service import get_firebase_service

def validate_character_name(name: str) -> tuple[bool, str]:
    """Validate character name and return (is_valid, error_message)"""
    if not name or not name.strip():
        return False, "Character name cannot be empty"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Character name must be at least 2 characters"
    
    if len(name) > 20:
        return False, "Character name must be 20 characters or less"
    
    # Allow only letters, numbers, spaces, hyphens, and apostrophes
    import re
    if not re.match(r"^[a-zA-Z0-9 '-]+$", name):
        return False, "Character name can only contain letters, numbers, spaces, hyphens, and apostrophes"
    
    # No consecutive spaces
    if '  ' in name:
        return False, "Character name cannot have consecutive spaces"
    
    # Must start and end with alphanumeric
    if not (name[0].isalnum() and name[-1].isalnum()):
        return False, "Character name must start and end with a letter or number"
    
    return True, ""

def render_character_selection_screen():
    """Render epic WoW-style character selection screen"""
    
    # Simplified CSS styling without the big graphic
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap');
    
    .character-hall {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
        padding: 2rem;
    }
    
    .character-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.95));
        border: 3px solid #DAA520;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 
            0 0 30px rgba(218, 165, 32, 0.4),
            inset 0 0 20px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .character-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 20px 40px rgba(218, 165, 32, 0.6),
            inset 0 0 30px rgba(0, 0, 0, 0.8);
        border-color: #FFD700;
    }
    
    .character-portrait {
        font-size: 4rem;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
    }
    
    .character-name {
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        font-weight: 600;
        text-align: center;
        color: #DAA520;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        margin-bottom: 0.5rem;
    }
    
    .character-details {
        background: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #DAA520;
    }
    
    .faction-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .consortium { background: linear-gradient(45deg, #8B4513, #CD853F); color: white; }
    .independents { background: linear-gradient(45deg, #4682B4, #87CEEB); color: white; }
    .rogue { background: linear-gradient(45deg, #228B22, #32CD32); color: white; }
    
    .empty-slot {
        background: linear-gradient(145deg, rgba(60, 60, 60, 0.3), rgba(40, 40, 40, 0.3));
        border: 3px dashed #666;
        border-radius: 20px;
        padding: 3rem;
        margin: 1rem;
        text-align: center;
        color: #888;
        transition: all 0.3s ease;
    }
    
    .empty-slot:hover {
        border-color: #DAA520;
        background: linear-gradient(145deg, rgba(218, 165, 32, 0.1), rgba(255, 215, 0, 0.1));
        color: #DAA520;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        background: rgba(218, 165, 32, 0.1);
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
        border: 1px solid rgba(218, 165, 32, 0.3);
    }
    
    .level-badge {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="character-hall">', unsafe_allow_html=True)
    
    # Simple title
    st.title("⚔️ Hall of Legends")
    st.caption("Choose your mining champion or forge a new legend")
    
    # Get characters with debugging
    firebase_service = get_firebase_service()
    char_manager = CharacterManager(firebase_service)
    email = st.session_state.get('user_email')
    
    # Debug info
    with st.expander("🔍 Debug Character Loading"):
        st.write(f"**Email:** {email}")
        st.write(f"**Firebase Service:** {firebase_service is not None}")
        st.write(f"**Firebase DB:** {firebase_service.db is not None if firebase_service else 'No Service'}")
        
        # Test user document
        if firebase_service and firebase_service.db:
            try:
                user_ref = firebase_service.db.collection('users').document(email)
                user_doc = user_ref.get()
                st.write(f"**User Document Exists:** {user_doc.exists}")
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    character_names = user_data.get('character_names', [])
                    st.write(f"**Character Names in User Doc:** {character_names}")
                    
                    # Test each character document
                    chars_ref = firebase_service.db.collection('users').document(email).collection('characters')
                    for char_name in character_names:
                        char_doc = chars_ref.document(char_name).get()
                        if char_doc.exists:
                            char_data = char_doc.to_dict()
                            st.write(f"- {char_name}: EXISTS (Level {char_data.get('level', 1)}, {char_data.get('faction', 'Unknown')})")
                        else:
                            st.write(f"- {char_name}: MISSING")
                else:
                    st.error("**User document does not exist - no characters can be loaded!**")
                    st.info("**Solution:** Create a new character to initialize the system.")
            except Exception as e:
                st.error(f"Debug error: {e}")
    
    characters = char_manager.get_user_characters(email)
    
    if len(characters) == 0:
        st.warning(f"⚠️ No characters found for {email}")
        st.info("🎯 Create your first character to begin your mining adventure!")
    else:
        st.success(f"✅ Found {len(characters)} characters:")
        for i, char in enumerate(characters):
            st.write(f"  {i+1}. {char.get('character_name', 'Unknown')} (Level {char.get('level', 1)})")
    
    # Refresh button
    if st.button("🔄 Refresh Character List"):
        st.rerun()
    
    # Character grid (3 columns)
    cols_per_row = 3
    total_slots = 9
    
    for row in range(3):  # 3 rows
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            slot_idx = row * cols_per_row + col_idx
            
            with cols[col_idx]:
                if slot_idx < len(characters):
                    render_character_card(characters[slot_idx], char_manager, email)
                else:
                    render_empty_character_slot(slot_idx + 1)
    
    # Back button
    if st.button("🏠 Return to Game", key="back_to_game", help="Return to current character"):
        st.session_state.character_loaded = True
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_character_card(character: Dict, char_manager, email: str):
    """Render individual character card with epic styling"""
    
    # Get character info
    name = character.get('character_name', 'Unknown')
    faction = character.get('faction', 'Unknown')
    race = character.get('race', 'Unknown')
    level = character.get('level', 1)
    gold = character.get('gold', 0)
    turn = character.get('turn', 1)
    last_played = character.get('last_played')
    
    # Faction styling
    faction_icons = {
        "Consortium": "🧔",
        "Independents": "🤠", 
        "Rogue Alliance": "🧝"
    }
    
    faction_classes = {
        "Consortium": "consortium",
        "Independents": "independents",
        "Rogue Alliance": "rogue"
    }
    
    icon = faction_icons.get(faction, "⚔️")
    faction_class = faction_classes.get(faction, "consortium")
    
    # Format last played
    if last_played:
        if isinstance(last_played, str):
            last_played_str = last_played[:10]
        else:
            last_played_str = last_played.strftime('%Y-%m-%d')
    else:
        last_played_str = "Never"
    
    # Character card HTML
    st.markdown(f"""
    <div class="character-card">
        <div class="character-portrait">{icon}</div>
        <div class="character-name">{name}</div>
        <div class="faction-badge {faction_class}">{race} {faction}</div>
        <div class="level-badge">Level {level}</div>
        
        <div class="character-details">
            <div class="stats-grid">
                <div class="stat-item">
                    <strong>💰 Gold</strong><br>
                    {gold:,} oz
                </div>
                <div class="stat-item">
                    <strong>⏳ Turn</strong><br>
                    {turn}
                </div>
                <div class="stat-item">
                    <strong>📅 Last Played</strong><br>
                    {last_played_str}
                </div>
                <div class="stat-item">
                    <strong>🗺️ Sites</strong><br>
                    {len(character.get('visited_sites', []))} visited
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚡ ENTER WORLD", key=f"play_{name}", help=f"Play as {name}"):
            load_character_into_session(character, email)
            st.success(f"🎮 Loaded {name}!")
            st.balloons()
            st.rerun()
    
    with col2:
        if st.button("🗑️ DELETE", key=f"delete_{name}", help=f"Delete {name}"):
            if st.session_state.get(f"confirm_delete_{name}", False):
                if char_manager.delete_character(email, name):
                    st.success(f"💀 {name} has been deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete character!")
            else:
                st.session_state[f"confirm_delete_{name}"] = True
                st.warning("⚠️ Click DELETE again to confirm!")

def render_empty_character_slot(slot_number: int):
    """Render empty character slot with creation option"""
    
    st.markdown(f"""
    <div class="empty-slot">
        <div style="font-size: 4rem; margin-bottom: 1rem;">➕</div>
        <h3>Character Slot {slot_number}</h3>
        <p style="font-style: italic; margin-bottom: 2rem;">Empty - Forge a new legend</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🔨 CREATE HERO", key=f"create_{slot_number}", help="Create a new character"):
        st.session_state['show_character_creation'] = True
        st.session_state['creating_slot'] = slot_number
        st.rerun()

def load_character_into_session(character: Dict, email: str):
    """Load character data into session state and join multiplayer server"""
    # Clear existing game state
    game_keys = ['current_view', 'current_strata', 'depth_layer', 'gold', 'reputation', 
                 'visited_sites', 'turn', 'equipment', 'supplies', 'faction_negotiations',
                 'level', 'xp', 'selected_faction', 'faction_benefits']
    
    for key in game_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Load character data
    st.session_state.current_character = character.get('character_name')
    st.session_state.selected_faction = character.get('faction')
    st.session_state.faction_benefits = character.get('faction_benefits', {})
    st.session_state.gold = character.get('gold', 50)
    st.session_state.level = character.get('level', 1)
    st.session_state.xp = character.get('xp', 0)
    st.session_state.turn = character.get('turn', 1)
    st.session_state.equipment = character.get('equipment', {})
    st.session_state.supplies = character.get('supplies', {})
    st.session_state.visited_sites = set(character.get('visited_sites', []))
    st.session_state.reputation = character.get('reputation', {})
    st.session_state.faction_negotiations = character.get('faction_negotiations', {})
    st.session_state.current_view = character.get('current_view', 'menu')
    st.session_state.current_strata = character.get('current_strata', 'Surface')
    st.session_state.depth_layer = character.get('depth_layer', 'Surface')
    
    # Join multiplayer server
    from .multiplayer_manager import get_multiplayer_manager
    multiplayer_manager = get_multiplayer_manager()
    server_id = multiplayer_manager.find_or_create_server(email, character.get('character_name'))
    st.session_state.multiplayer_server_id = server_id
    
    # Mark as character loaded
    st.session_state.character_loaded = True
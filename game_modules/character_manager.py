import streamlit as st
import datetime
from typing import Dict, List, Optional

class CharacterManager:
    """WoW-style character management system"""
    
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
    
    def get_user_characters(self, email: str) -> List[Dict]:
        """Get all characters for a user using individual document gets"""
        characters = []
        
        if not self.firebase_service or not self.firebase_service.db:
            return characters
        
        # Get character names from user document
        user_ref = self.firebase_service.db.collection('users').document(email)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return characters
        
        user_data = user_doc.to_dict()
        character_names = user_data.get('character_names', [])
        
        # Get each character by name
        chars_ref = self.firebase_service.db.collection('users').document(email).collection('characters')
        
        for char_name in character_names:
            char_doc = chars_ref.document(char_name).get()
            if char_doc.exists:
                char_data = char_doc.to_dict()
                characters.append(char_data)
        
        return characters
    
    def create_character(self, email: str, character_name: str, faction: str, race: str) -> bool:
        """Create a new character with validation"""
        try:
            # Validate character name
            from .character_selection import validate_character_name
            is_valid, error_msg = validate_character_name(character_name)
            if not is_valid:
                st.error(f"❌ {error_msg}")
                return False
            
            character_name = character_name.strip()
            
            # Check character limit (9 max)
            existing_chars = self.get_user_characters(email)
            if len(existing_chars) >= 9:
                st.error("Maximum of 9 characters allowed per account!")
                return False
            
            # Check if character name already exists for this user
            for char in existing_chars:
                if char.get('character_name', '').lower() == character_name.lower():
                    st.error(f"Character name '{character_name}' already exists!")
                    return False
            
            # Create character data with proper timestamps
            character_data = {
                'character_name': character_name,
                'faction': faction,
                'race': race,
                'level': 1,
                'xp': 0,
                'quest_progress': {'completed': []},
                'gold': 50,
                'turn': 1,
                'created_at': datetime.datetime.now(),
                'last_played': datetime.datetime.now(),
                'equipment': {"Basic Pickaxe": True, "Canvas Satchel": True, "Work Clothes": True},
                'supplies': {},
                'visited_sites': [],
                'reputation': {},
                'faction_negotiations': {},
                'current_view': 'menu',
                'current_strata': 'Surface',
                'depth_layer': 'Surface',
                'total_earned': 0,
                'night_expeditions': 0,
                'rare_finds': 0
            }
            
            # Set faction benefits based on faction
            if faction == "Consortium":
                character_data['faction_benefits'] = {
                    "equipment_discount": 0.2,
                    "tax_rate": 0.15,
                    "special_access": ["dwarven_tech", "banking"],
                    "race": "Dwarf"
                }
            elif faction == "Independents":
                character_data['faction_benefits'] = {
                    "tax_rate": 0.05,
                    "equipment_markup": 0.1,
                    "special_access": ["black_market", "all_traders"],
                    "race": "Human"
                }
            elif faction == "Rogue Alliance":
                character_data['faction_benefits'] = {
                    "danger_bonus": 0.3,
                    "law_enforcement_risk": True,
                    "special_access": ["elvish_contraband", "irish_luck"],
                    "race": "Irish Elf"
                }
            
            # Save character to Firebase - path: users/{email}/characters/{character_name}
            char_ref = self.firebase_service.db.collection('users').document(email).collection('characters').document(character_name)
            char_ref.set(character_data)
            
            # Update user document with character name list for easy retrieval
            user_ref = self.firebase_service.db.collection('users').document(email)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                character_names = user_data.get('character_names', [])
            else:
                character_names = []
                # Create user document if it doesn't exist
                user_ref.set({
                    'email': email,
                    'character_names': [],
                    'created_at': datetime.datetime.now()
                })
            
            if character_name not in character_names:
                character_names.append(character_name)
                # Update just the character_names field
                user_ref.update({'character_names': character_names})
            
            # Verify the character was created
            verification = char_ref.get()
            if verification.exists:
                st.success(f"✅ Character '{character_name}' created successfully!")
                return True
            else:
                st.error("❌ Character creation failed - verification failed")
                return False
                
        except Exception as e:
            st.error(f"❌ Firebase error creating character: {str(e)}")
            return False
    
    def load_character(self, email: str, character_name: str) -> Optional[Dict]:
        """Load character data"""
        try:
            char_ref = self.firebase_service.db.collection('users').document(email).collection('characters').document(character_name)
            char_doc = char_ref.get()
            
            if char_doc.exists:
                # Update last played
                char_ref.update({'last_played': datetime.datetime.now()})
                return char_doc.to_dict()
            return None
        except Exception:
            return None
    
    def save_character(self, email: str, character_name: str, character_data: Dict) -> bool:
        """Save character data"""
        try:
            character_data['last_played'] = datetime.datetime.now()
            char_ref = self.firebase_service.db.collection('users').document(email).collection('characters').document(character_name)
            char_ref.set(character_data)
            return True
        except Exception:
            return False
    
    def delete_character(self, email: str, character_name: str) -> bool:
        """Delete a character"""
        try:
            char_ref = self.firebase_service.db.collection('users').document(email).collection('characters').document(character_name)
            char_ref.delete()
            
            # Remove from user's character names list
            user_ref = self.firebase_service.db.collection('users').document(email)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                character_names = user_data.get('character_names', [])
                if character_name in character_names:
                    character_names.remove(character_name)
                    user_ref.set({'character_names': character_names})
            
            return True
        except Exception:
            return False

def render_character_selection():
    """Render WoW-style character selection screen"""
    from .firebase_service import get_firebase_service
    
    firebase_service = get_firebase_service()
    char_manager = CharacterManager(firebase_service)
    
    st.markdown("""
    <style>
    .character-slot {
        background: linear-gradient(145deg, rgba(42, 42, 42, 0.95), rgba(26, 26, 26, 0.95));
        border: 2px solid #DAA520;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 0 15px rgba(218, 165, 32, 0.3);
    }
    .character-empty {
        background: linear-gradient(145deg, rgba(60, 60, 60, 0.5), rgba(40, 40, 40, 0.5));
        border: 2px dashed #666;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        color: #888;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# ⚔️ **CHARACTER SELECTION**")
    st.markdown("*Choose your mining legend or create a new one*")
    
    email = st.session_state.get('user_email')
    
    # Add refresh button
    if st.button("🔄 Refresh Character List"):
        st.rerun()
    
    # Debug section
    if st.checkbox("🔍 Debug Character System"):
        st.markdown("### Debug Information:")
        st.write(f"**Email:** {email}")
        st.write(f"**Firebase Service:** {firebase_service is not None}")
        st.write(f"**Firebase DB:** {firebase_service.db is not None if firebase_service else 'No Service'}")
        
        # Test user document and character names
        try:
            if firebase_service and firebase_service.db:
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
                        st.write(f"- {char_name}: {'EXISTS' if char_doc.exists else 'MISSING'}")
                else:
                    st.write("**User document does not exist**")
            else:
                st.error("Firebase service or database not available")
                
        except Exception as e:
            st.error(f"Firebase Error: {str(e)}")
    
    characters = char_manager.get_user_characters(email)
    st.info(f"Loaded {len(characters)} characters for {email}")
    
    # Character slots (9 total)
    for i in range(9):
        if i < len(characters):
            char = characters[i]
            render_character_slot(char, char_manager, email)
        else:
            render_empty_slot(i + 1, char_manager, email, len(characters))
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_character_slot(character: Dict, char_manager, email: str):
    """Render filled character slot"""
    faction_icons = {
        "Consortium": "🧔",
        "Independents": "🤠", 
        "Rogue Alliance": "🧝"
    }
    
    faction = character.get('faction', 'Unknown')
    icon = faction_icons.get(faction, "⚔️")
    
    st.markdown('<div class="character-slot">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"### {icon} **{character.get('character_name', 'Unknown')}**")
        st.markdown(f"**{character.get('race', 'Unknown')} {faction}**")
        st.markdown(f"Level {character.get('level', 1)} • {character.get('gold', 0):,} oz gold")
    
    with col2:
        last_played = character.get('last_played')
        if last_played:
            if isinstance(last_played, str):
                st.markdown(f"**Last Played:** {last_played[:10]}")
            else:
                st.markdown(f"**Last Played:** {last_played.strftime('%Y-%m-%d')}")
        st.markdown(f"**Turn:** {character.get('turn', 1)}")
        st.markdown(f"**Sites Visited:** {len(character.get('visited_sites', []))}")
    
    with col3:
        if st.button("▶️ PLAY", key=f"play_{character.get('character_name')}", type="primary"):
            load_character_into_session(character, email)
            
            # Auto-join multiplayer server when loading character
            try:
                from .multiplayer_manager import get_multiplayer_manager
                multiplayer_manager = get_multiplayer_manager()
                server_id = multiplayer_manager.find_or_create_server(
                    email, 
                    character.get('character_name')
                )
                st.session_state['current_server'] = server_id
            except Exception as e:
                st.warning(f"⚠️ Multiplayer join failed: {e}")
            
            st.success(f"Loaded {character.get('character_name')}!")
            st.rerun()
        
        if st.button("🗑️ DELETE", key=f"delete_{character.get('character_name')}"):
            if st.session_state.get(f"confirm_delete_{character.get('character_name')}", False):
                char_manager.delete_character(email, character.get('character_name'))
                st.success("Character deleted!")
                st.rerun()
            else:
                st.session_state[f"confirm_delete_{character.get('character_name')}"] = True
                st.warning("Click DELETE again to confirm!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_empty_slot(slot_number: int, char_manager, email: str, current_count: int):
    """Render empty character slot"""
    st.markdown('<div class="character-empty">', unsafe_allow_html=True)
    st.markdown(f"### 📝 **Character Slot {slot_number}**")
    st.markdown("*Empty - Create a new character*")
    
    if st.button(f"➕ CREATE CHARACTER", key=f"create_{slot_number}", type="secondary"):
        st.session_state['show_character_creation'] = True
        st.session_state['creating_slot'] = slot_number
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_character_creation():
    """Render character creation interface"""
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# ✨ **CREATE NEW CHARACTER**")
    
    with st.form("character_creation"):
        character_name = st.text_input(
            "Character Name", 
            placeholder="Enter a unique name (2-20 characters)",
            max_chars=20,
            help="Only letters, numbers, spaces, hyphens, and apostrophes allowed"
        )
        
        st.markdown("### Choose Your Path:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🧔 **DWARF MINER**")
            st.markdown("*Dwarven Consortium*")
            st.markdown("• 20% equipment discount")
            st.markdown("• 15% taxes")
            st.markdown("• Stable & profitable")
            dwarf_selected = st.checkbox("Choose Dwarf", key="dwarf_choice")
        
        with col2:
            st.markdown("#### 🤠 **HUMAN PROSPECTOR**")
            st.markdown("*Human Independents*")
            st.markdown("• Access to all markets")
            st.markdown("• 5% taxes")
            st.markdown("• Flexible & balanced")
            human_selected = st.checkbox("Choose Human", key="human_choice")
        
        with col3:
            st.markdown("#### 🧝 **IRISH ELF ROGUE**")
            st.markdown("*Rogue Alliance*")
            st.markdown("• 30% danger bonus")
            st.markdown("• No taxes")
            st.markdown("• High risk/reward")
            elf_selected = st.checkbox("Choose Irish Elf", key="elf_choice")
        
        submitted = st.form_submit_button("🎭 CREATE CHARACTER", type="primary")
        
        if submitted:
            # Validate single selection
            selections = [dwarf_selected, human_selected, elf_selected]
            if sum(selections) != 1:
                st.error("Please select exactly one race/faction!")
            else:
                # Validate character name
                from .character_selection import validate_character_name
                is_valid, error_msg = validate_character_name(character_name)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                else:
                    # Determine faction and race
                    if dwarf_selected:
                        faction, race = "Consortium", "Dwarf"
                    elif human_selected:
                        faction, race = "Independents", "Human"
                    else:
                        faction, race = "Rogue Alliance", "Irish Elf"
                
                    # Create character data immediately
                    character_data = {
                        'character_name': character_name.strip(),
                        'faction': faction,
                        'race': race,
                        'level': 1,
                        'xp': 0,
                        'quest_progress': {'completed': []},
                        'gold': 50,
                        'turn': 1,
                        'equipment': {"Basic Pickaxe": True, "Canvas Satchel": True, "Work Clothes": True},
                        'supplies': {},
                        'visited_sites': [],
                        'reputation': {},
                        'faction_negotiations': {},
                        'current_view': 'menu',
                        'current_strata': 'Surface',
                        'depth_layer': 'Surface',
                        'total_earned': 0,
                        'night_expeditions': 0,
                        'rare_finds': 0
                    }
                
                # Set faction benefits
                if faction == "Consortium":
                    character_data['faction_benefits'] = {
                        "equipment_discount": 0.2,
                        "tax_rate": 0.15,
                        "special_access": ["dwarven_tech", "banking"],
                        "race": "Dwarf"
                    }
                elif faction == "Independents":
                    character_data['faction_benefits'] = {
                        "tax_rate": 0.05,
                        "equipment_markup": 0.1,
                        "special_access": ["black_market", "all_traders"],
                        "race": "Human"
                    }
                elif faction == "Rogue Alliance":
                    character_data['faction_benefits'] = {
                        "danger_bonus": 0.3,
                        "law_enforcement_risk": True,
                        "special_access": ["elvish_contraband", "irish_luck"],
                        "race": "Irish Elf"
                    }
                
                # Save to Firebase first, then load into session
                from .firebase_service import get_firebase_service
                firebase_service = get_firebase_service()
                char_manager = CharacterManager(firebase_service)
                
                # Create character in Firebase
                if char_manager.create_character(st.session_state.user_email, character_name.strip(), faction, race):
                    # Load character into session after successful Firebase save
                    load_character_into_session(character_data, st.session_state.user_email)
                    
                    # Auto-join multiplayer server
                    try:
                        from .multiplayer_manager import get_multiplayer_manager
                        multiplayer_manager = get_multiplayer_manager()
                        server_id = multiplayer_manager.find_or_create_server(
                            st.session_state.user_email, 
                            character_name.strip()
                        )
                        st.session_state['current_server'] = server_id
                        st.info(f"🌐 Joined multiplayer server: {server_id}")
                    except Exception as e:
                        st.warning(f"⚠️ Multiplayer join failed: {e}")
                    
                    st.success(f"🎉 {character_name} created and loaded!")
                    st.balloons()
                    
                    # Clear creation state
                    st.session_state['show_character_creation'] = False
                    if 'creating_slot' in st.session_state:
                        del st.session_state['creating_slot']
                    
                    # Force rerun to go to main game
                    st.rerun()
                else:
                    st.error("❌ Failed to create character in Firebase. Please try again.")
    
    if st.button("❌ Cancel"):
        st.session_state['show_character_creation'] = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def load_character_into_session(character: Dict, email: str):
    """Load character data into session state"""
    # Clear existing game state
    game_keys = ['current_view', 'current_strata', 'depth_layer', 'gold', 'reputation',
                 'visited_sites', 'turn', 'equipment', 'supplies', 'faction_negotiations',
                 'level', 'xp', 'quest_progress', 'selected_faction', 'faction_benefits',
                 'total_earned', 'night_expeditions', 'rare_finds']
    
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
    st.session_state.quest_progress = character.get('quest_progress', {'completed': []})
    st.session_state.total_earned = character.get('total_earned', 0)
    st.session_state.night_expeditions = character.get('night_expeditions', 0)
    st.session_state.rare_finds = character.get('rare_finds', 0)
    st.session_state.turn = character.get('turn', 1)
    st.session_state.equipment = character.get('equipment', {})
    st.session_state.supplies = character.get('supplies', {})
    st.session_state.visited_sites = set(character.get('visited_sites', []))
    st.session_state.reputation = character.get('reputation', {})
    st.session_state.faction_negotiations = character.get('faction_negotiations', {})
    st.session_state.current_view = character.get('current_view', 'menu')
    st.session_state.current_strata = character.get('current_strata', 'Surface')
    st.session_state.depth_layer = character.get('depth_layer', 'Surface')
    
    # Mark as character loaded
    st.session_state.character_loaded = True

def save_current_character():
    """Save current character state"""
    if not st.session_state.get('current_character'):
        return False
    
    try:
        from .firebase_service import get_firebase_service
        firebase_service = get_firebase_service()
        char_manager = CharacterManager(firebase_service)
        
        character_data = {
            'character_name': st.session_state.current_character,
            'faction': st.session_state.get('selected_faction'),
            'race': st.session_state.get('faction_benefits', {}).get('race', 'Unknown'),
            'level': st.session_state.get('level', 1),
            'xp': st.session_state.get('xp', 0),
            'quest_progress': st.session_state.get('quest_progress', {'completed': []}),
            'total_earned': st.session_state.get('total_earned', 0),
            'night_expeditions': st.session_state.get('night_expeditions', 0),
            'rare_finds': st.session_state.get('rare_finds', 0),
            'gold': st.session_state.get('gold', 50),
            'turn': st.session_state.get('turn', 1),
            'equipment': st.session_state.get('equipment', {}),
            'supplies': st.session_state.get('supplies', {}),
            'visited_sites': list(st.session_state.get('visited_sites', set())),
            'reputation': st.session_state.get('reputation', {}),
            'faction_negotiations': st.session_state.get('faction_negotiations', {}),
            'current_view': st.session_state.get('current_view', 'menu'),
            'current_strata': st.session_state.get('current_strata', 'Surface'),
            'depth_layer': st.session_state.get('depth_layer', 'Surface'),
            'faction_benefits': st.session_state.get('faction_benefits', {})
        }
        
        return char_manager.save_character(
            st.session_state.user_email, 
            st.session_state.current_character, 
            character_data
        )
    except Exception:
        return False

def check_character_selection():
    """Check if user has selected a character"""
    if st.session_state.get('character_loaded', False):
        return True
    
    # Show character creation if requested
    if st.session_state.get('show_character_creation', False):
        render_character_creation()
        return False
    
    # Show epic character selection screen
    from .character_selection import render_character_selection_screen
    render_character_selection_screen()
    return False
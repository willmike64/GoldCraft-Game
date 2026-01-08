# GoldCraft
Multi-player dimensional earth mining game built with Streamlit and Firebase.

## Features
- Character creation and management (up to 9 characters per account)
- Three factions: Dwarven Consortium, Human Independents, Irish Elf Rogues
- Global mine system with real-time multiplayer mining
- Leveling and progression system
- Admin panel for mine management

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure Firebase credentials
3. Run: `streamlit run goldcraft.py`

## Game Modules
- `character_manager.py` - Character creation, loading, saving
- `character_selection.py` - WoW-style character selection screen
- `global_mine_system.py` - Multi-player mining system
- `leveling_system.py` - XP and level progression
- `firebase_service.py` - Database connectivity
- `admin_panel.py` - Administrative controls
- `auth.py` - User authentication
- `menu.py` - Main game menu
- `map.py` - Mining map interface
- `town.py` - Town hub
- `statistics.py` - Player statistics

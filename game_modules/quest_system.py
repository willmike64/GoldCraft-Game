import streamlit as st
from typing import Dict, List, Optional
from .ui_styles import get_ui_styles

class QuestSystem:
    def __init__(self):
        self.faction_quests = {
            "Consortium": [
                {
                    "id": "dwarf_mining_mastery",
                    "title": "🔨 Mining Mastery",
                    "description": "Mine 100 gold to prove your worth to the Consortium",
                    "requirements": {"gold_mined": 100},
                    "rewards": {"gold": 200, "xp": 150},
                    "level_req": 1
                },
                {
                    "id": "dwarf_equipment_upgrade",
                    "title": "⚒️ Equipment Upgrade",
                    "description": "Purchase advanced dwarven equipment",
                    "requirements": {"equipment_purchased": ["Advanced Pickaxe"]},
                    "rewards": {"gold": 300, "xp": 200},
                    "level_req": 3
                },
                {
                    "id": "dwarf_deep_mining",
                    "title": "🏔️ Deep Mining Expedition",
                    "description": "Reach the Deep Caverns mining layer",
                    "requirements": {"depth_reached": "Deep Caverns"},
                    "rewards": {"gold": 500, "xp": 400},
                    "level_req": 5
                }
            ],
            "Independents": [
                {
                    "id": "human_trader",
                    "title": "💰 Independent Trader",
                    "description": "Complete 5 successful mining expeditions",
                    "requirements": {"expeditions_completed": 5},
                    "rewards": {"gold": 250, "xp": 175},
                    "level_req": 1
                },
                {
                    "id": "human_reputation",
                    "title": "🤝 Build Reputation",
                    "description": "Gain positive reputation with 2 different factions",
                    "requirements": {"faction_reputation": 2},
                    "rewards": {"gold": 400, "xp": 250},
                    "level_req": 4
                },
                {
                    "id": "human_entrepreneur",
                    "title": "📈 Entrepreneur",
                    "description": "Accumulate 1000 gold through trading",
                    "requirements": {"total_gold_earned": 1000},
                    "rewards": {"gold": 600, "xp": 350},
                    "level_req": 6
                }
            ],
            "Rogue Alliance": [
                {
                    "id": "elf_stealth_mining",
                    "title": "🌙 Stealth Mining",
                    "description": "Complete 3 night mining expeditions",
                    "requirements": {"night_expeditions": 3},
                    "rewards": {"gold": 300, "xp": 200},
                    "level_req": 1
                },
                {
                    "id": "elf_rare_finds",
                    "title": "💎 Rare Treasure Hunter",
                    "description": "Find 5 rare mining discoveries",
                    "requirements": {"rare_finds": 5},
                    "rewards": {"gold": 450, "xp": 300},
                    "level_req": 3
                },
                {
                    "id": "elf_faction_infiltration",
                    "title": "🕵️ Faction Infiltration",
                    "description": "Successfully negotiate with rival factions",
                    "requirements": {"successful_negotiations": 3},
                    "rewards": {"gold": 700, "xp": 450},
                    "level_req": 7
                }
            ]
        }

    def get_available_quests(self, faction: str, level: int, completed_quests: List[str]) -> List[Dict]:
        """Get available quests for faction and level"""
        if faction not in self.faction_quests:
            return []
        
        available = []
        for quest in self.faction_quests[faction]:
            if (quest["level_req"] <= level and 
                quest["id"] not in completed_quests):
                available.append(quest)
        
        return available

    def check_quest_completion(self, quest: Dict, character_data: Dict) -> bool:
        """Check if quest requirements are met"""
        requirements = quest["requirements"]
        
        for req_type, req_value in requirements.items():
            if req_type == "gold_mined":
                if character_data.get("gold", 0) < req_value:
                    return False
            elif req_type == "expeditions_completed":
                if len(character_data.get("visited_sites", [])) < req_value:
                    return False
            elif req_type == "depth_reached":
                if character_data.get("depth_layer", "Surface") != req_value:
                    return False
            elif req_type == "equipment_purchased":
                equipment = character_data.get("equipment", {})
                for item in req_value:
                    if not equipment.get(item, False):
                        return False
            elif req_type == "faction_reputation":
                reputation = character_data.get("reputation", {})
                positive_reps = sum(1 for rep in reputation.values() if rep > 0)
                if positive_reps < req_value:
                    return False
            elif req_type == "total_gold_earned":
                # This would need tracking in character data
                if character_data.get("total_earned", 0) < req_value:
                    return False
            elif req_type == "night_expeditions":
                # This would need tracking in character data
                if character_data.get("night_expeditions", 0) < req_value:
                    return False
            elif req_type == "rare_finds":
                # This would need tracking in character data
                if character_data.get("rare_finds", 0) < req_value:
                    return False
            elif req_type == "successful_negotiations":
                negotiations = character_data.get("faction_negotiations", {})
                successful = sum(1 for result in negotiations.values() if result == "success")
                if successful < req_value:
                    return False
        
        return True

    def complete_quest(self, quest_id: str, character_data: Dict) -> Dict:
        """Complete a quest and return rewards"""
        faction = character_data.get("faction", "")
        if faction not in self.faction_quests:
            return {}
        
        quest = next((q for q in self.faction_quests[faction] if q["id"] == quest_id), None)
        if not quest:
            return {}
        
        return quest["rewards"]

def render_quest_panel():
    """Render the quest panel UI"""
    if not st.session_state.get("character_loaded", False):
        return
    
    styles = get_ui_styles()
    st.markdown(styles, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("# 📜 Faction Quests")
    
    quest_system = QuestSystem()
    faction = st.session_state.get("selected_faction", "")
    level = st.session_state.get("level", 1)
    quest_progress = st.session_state.get("quest_progress", {"completed": []})
    completed_quests = quest_progress.get("completed", [])
    
    # Get character data for quest checking
    character_data = {
        "gold": st.session_state.get("gold", 0),
        "level": level,
        "visited_sites": list(st.session_state.get("visited_sites", set())),
        "depth_layer": st.session_state.get("depth_layer", "Surface"),
        "equipment": st.session_state.get("equipment", {}),
        "reputation": st.session_state.get("reputation", {}),
        "faction_negotiations": st.session_state.get("faction_negotiations", {}),
        "faction": faction,
        "total_earned": st.session_state.get("total_earned", 0),
        "night_expeditions": st.session_state.get("night_expeditions", 0),
        "rare_finds": st.session_state.get("rare_finds", 0)
    }
    
    available_quests = quest_system.get_available_quests(faction, level, completed_quests)
    
    if not available_quests:
        st.info("🎉 All available quests completed! Check back when you level up.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown(f"**{faction} Faction Quests**")
    
    for quest in available_quests:
        with st.container():
            st.markdown('<div class="info-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{quest['title']}**")
                st.markdown(f"*Level {quest['level_req']} Required*")
                st.write(quest["description"])
                
                # Show requirements
                st.markdown("**Requirements:**")
                for req_type, req_value in quest["requirements"].items():
                    if req_type == "gold_mined":
                        current = character_data.get("gold", 0)
                        st.write(f"• Mine {req_value} gold ({current}/{req_value})")
                    elif req_type == "expeditions_completed":
                        current = len(character_data.get("visited_sites", []))
                        st.write(f"• Complete {req_value} expeditions ({current}/{req_value})")
                    elif req_type == "depth_reached":
                        current = character_data.get("depth_layer", "Surface")
                        st.write(f"• Reach {req_value} (Currently: {current})")
                    elif req_type == "equipment_purchased":
                        st.write(f"• Purchase: {', '.join(req_value)}")
                    else:
                        st.write(f"• {req_type.replace('_', ' ').title()}: {req_value}")
                
                # Show rewards
                st.markdown("**Rewards:**")
                rewards = quest["rewards"]
                reward_text = []
                if "gold" in rewards:
                    reward_text.append(f"💰 {rewards['gold']} gold")
                if "xp" in rewards:
                    reward_text.append(f"⭐ {rewards['xp']} XP")
                st.write("• " + ", ".join(reward_text))
            
            with col2:
                if quest_system.check_quest_completion(quest, character_data):
                    if st.button(f"Complete Quest", key=f"complete_{quest['id']}"):
                        # Award rewards
                        rewards = quest_system.complete_quest(quest["id"], character_data)
                        
                        if "gold" in rewards:
                            st.session_state.gold = st.session_state.get("gold", 0) + rewards["gold"]
                        if "xp" in rewards:
                            st.session_state.xp = st.session_state.get("xp", 0) + rewards["xp"]
                        
                        # Mark quest as completed
                        if "quest_progress" not in st.session_state:
                            st.session_state.quest_progress = {"completed": []}
                        st.session_state.quest_progress["completed"].append(quest["id"])
                        
                        # Save character
                        from .character_manager import save_current_character
                        save_current_character()
                        
                        st.success(f"🎉 Quest completed! Earned {rewards.get('gold', 0)} gold and {rewards.get('xp', 0)} XP!")
                        st.rerun()
                else:
                    st.write("❌ Requirements not met")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
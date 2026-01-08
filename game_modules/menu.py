import streamlit as st

def render_game_menu():
    st.markdown("## ⛏️ Welcome to Gold Creek, Prospector!")
    
    # Get player info
    prospector_name = st.session_state.get('prospector_name', 'Unknown Prospector')
    player_gold = st.session_state.get('gold', 50)
    turn = st.session_state.get('turn', 1)
    
    st.markdown(f"### 👋 Howdy, **{prospector_name}**!")
    
    # Status overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Gold", f"{player_gold:.1f} oz")
    with col2:
        st.metric("📅 Day", turn)
    with col3:
        equipment_count = len(st.session_state.get('equipment', {}))
        st.metric("⚙️ Equipment", f"{equipment_count} items")
    
    st.divider()
    
    # Beginner guidance
    if turn == 1 and player_gold <= 75:  # New player
        st.info("🌟 **New to Gold Creek?** Here's what seasoned prospectors recommend:")
        
        st.markdown("""
        **📚 Getting Started Guide:**
        1. **🏘️ Visit the Town Hub first** - Meet the locals, buy better equipment, and learn the ropes
        2. **💪 Build your strength** - Try axe throwing and other activities to improve your skills
        3. **🤝 Make friends with factions** - They'll offer better deals and exclusive equipment
        4. **🗺️ Study the Strata Map** - Plan your expeditions carefully - some sites are deadly!
        5. **💰 Start small** - Begin with safer, closer sites before tackling the dangerous ones
        """)
        
        st.warning("⚠️ **Survival Tip**: Don't rush into expeditions! Many greenhorn prospectors have lost everything (and their lives) by being too eager. The mines will wait - prepare yourself first!")
    
    st.divider()
    
    # Main action buttons with descriptions
    st.markdown("### 🎯 What would you like to do today?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏘️ **Town Hub** (Recommended First)")
        st.markdown("*Visit the bustling heart of Gold Creek*")
        st.markdown("• 🛒 Buy better equipment and supplies")
        st.markdown("• 🎯 Practice axe throwing for strength")
        st.markdown("• 🤝 Build relationships with factions")
        st.markdown("• 🍺 Hear tales from veteran miners")
        
        if st.button("🏘️ Head to Town", use_container_width=True, type="primary"):
            st.session_state.current_view = "town"
            st.rerun()
    
    with col2:
        st.markdown("#### 🗺️ **Mining Expeditions** (For Experienced)")
        st.markdown("*Venture into the dangerous mining territories*")
        st.markdown("• ⛏️ Extract gold from various sites")
        st.markdown("• 🎲 Face bandits, cave-ins, and mysteries")
        st.markdown("• 💎 Discover legendary treasure hoards")
        st.markdown("• ⚠️ Risk everything for fortune")
        
        # Show warning for new players
        if turn == 1 and player_gold <= 75:
            st.error("🚨 **Dangerous for beginners!** Visit town first.")
            button_type = "secondary"
        else:
            button_type = "primary"
            
        if st.button("🚀 Begin Expedition", use_container_width=True, type=button_type):
            if turn == 1 and player_gold <= 75:
                st.warning("The old-timer at the saloon grabs your arm: 'Hold on there, greenhorn! You'll get yourself killed out there. Visit the town first, get some proper gear, and learn the ropes!'")
            else:
                st.session_state.current_view = "map"
                st.rerun()
    
    st.divider()
    
    # Quick stats and progress
    st.markdown("### 📊 Your Progress")
    
    # Calculate some basic progress metrics
    visited_sites = len(st.session_state.get('visited_sites', set()))
    reputation = st.session_state.get('reputation', {})
    total_rep = sum(reputation.values()) if reputation else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🗺️ Sites Visited", visited_sites)
    with col2:
        st.metric("🤝 Total Reputation", f"{total_rep:.0f}")
    with col3:
        profit = player_gold - 50  # Starting gold was 50 (or 75 for rogues)
        st.metric("📈 Net Profit", f"{profit:.1f} oz", delta=f"{profit:.1f}")
    
    # Motivational flavor text based on progress
    if profit > 100:
        st.success("🏆 **Legendary Prospector!** Your name is spoken with respect throughout Gold Creek!")
    elif profit > 50:
        st.info("⭐ **Successful Miner!** You're making a name for yourself in these parts.")
    elif profit > 0:
        st.info("📈 **On the Right Track!** Keep up the good work, prospector.")
    elif turn > 5:
        st.warning("💪 **Tough Times!** Every prospector faces hardship. Visit the town for advice and better equipment.")
    
    st.divider()
    
    # Save/Load section
    st.markdown("### 💾 Game Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Game", use_container_width=True, type="secondary"):
            # Use character save instead
            from game_modules.character_manager import save_current_character
            if save_current_character():
                st.success("🎉 Character saved successfully!")
            else:
                st.error("❌ Failed to save character")
    
    with col2:
        if st.button("📁 Load Game", use_container_width=True, type="secondary"):
            if st.session_state.get('user_email'):
                from game_modules.firebase_service import get_firebase_service
                firebase_service = get_firebase_service()
                saves = firebase_service.get_user_saves(st.session_state.user_email)
                if saves:
                    st.info(f"Found {len(saves)} saved games. Use the sidebar Load button to select one.")
                else:
                    st.info("No saved games found.")
            else:
                st.error("Not logged in!")
    
    st.divider()
    
    # Game lore and atmosphere
    st.markdown("""
    ### 📖 The Gold Creek Chronicles
    
    *The year is 1849. Gold Creek buzzes with opportunity and danger.*
    
    **The Three Factions:**
    - 🏛️ **Old Miners Guild**: Traditional methods, reliable equipment, honor-bound
    - 🏭 **Industrial Syndicate**: Steam-powered tools, efficiency, progress at any cost  
    - 🤠 **Frontier Independents**: Freedom, adventure, and questionable morals
    
    **The Strata Layers:**
    - 🌱 **Surface**: Safe but limited rewards
    - ⚙️ **Industrial Veins**: Balanced risk and reward
    - 🏛️ **Ancient Caverns**: High risk, mysterious treasures
    - 👻 **Ghost Layers**: Legends speak of unimaginable wealth... and unspeakable horrors
    
    *Every decision shapes your legend. Will you be remembered as a cautious survivor, a wealthy baron, or a cautionary tale?*
    """)

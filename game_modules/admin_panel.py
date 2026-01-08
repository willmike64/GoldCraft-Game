import streamlit as st
from .global_mine_system import get_global_mine_system
import datetime

def render_admin_panel():
    """Render admin panel for global mine management"""
    global_mines = get_global_mine_system()
    
    if not global_mines.is_admin(st.session_state.get('user_email', '')):
        st.error("🚫 Access Denied: Admin privileges required")
        return
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# 🔧 **ADMIN CONTROL PANEL**")
    st.markdown("*Global Mine System Management*")
    
    # Admin controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 **RESET ALL MINES**", type="primary", width='stretch'):
            with st.spinner("Resetting all mines..."):
                if global_mines.reset_all_mines():
                    st.success("✅ All mines reset successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to reset mines")
    
    with col2:
        if st.button("📊 **REFRESH STATUS**", width='stretch'):
            st.rerun()
    
    with col3:
        if st.button("🏆 **VIEW LEADERBOARD**", width='stretch'):
            st.session_state['show_admin_leaderboard'] = True
    
    st.divider()
    
    # Global statistics
    st.markdown("## 📈 **Global Statistics**")
    mines_status = global_mines.get_all_mines_status()
    
    if mines_status:
        total_reserves = sum(mine.get('current_reserves', 0) for mine in mines_status)
        total_mined = sum(mine.get('total_mined', 0) for mine in mines_status)
        active_mines = len([mine for mine in mines_status if mine.get('current_reserves', 0) > 0])
        depleted_mines = len(mines_status) - active_mines
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reserves", f"{total_reserves:,.0f} oz")
        with col2:
            st.metric("Total Mined", f"{total_mined:,.0f} oz")
        with col3:
            st.metric("Active Mines", active_mines)
        with col4:
            st.metric("Depleted Mines", depleted_mines)
    
    st.divider()
    
    # Multiplayer list
    st.markdown("## 👥 **Active Players**")
    
    try:
        from .firebase_service import get_firebase_service
        firebase_service = get_firebase_service()
        
        if firebase_service and firebase_service.db:
            users_ref = firebase_service.db.collection('users')
            active_players = []
            
            test_emails = ['snow.turkeys.1j@icloud.com', 'mwill1003@gmail.com']
            
            for email in test_emails:
                try:
                    user_doc = users_ref.document(email).get()
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        character_names = user_data.get('character_names', [])
                        if character_names:
                            chars_ref = users_ref.document(email).collection('characters')
                            for char_name in character_names:
                                char_doc = chars_ref.document(char_name).get()
                                if char_doc.exists:
                                    char_data = char_doc.to_dict()
                                    active_players.append({
                                        'email': email,
                                        'character': char_data.get('character_name', 'Unknown'),
                                        'level': char_data.get('level', 1),
                                        'faction': char_data.get('faction', 'Unknown'),
                                        'gold': char_data.get('gold', 0),
                                        'turn': char_data.get('turn', 1)
                                    })
                except:
                    continue
            
            if active_players:
                st.success(f"🟢 {len(active_players)} active characters found")
                
                for player in sorted(active_players, key=lambda x: x['level'], reverse=True):
                    faction_icons = {"Consortium": "🧔", "Independents": "🤠", "Rogue Alliance": "🧝"}
                    icon = faction_icons.get(player['faction'], "⚔️")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"{icon} **{player['character']}** (Level {player['level']})")
                        st.caption(f"Email: {player['email']}")
                    with col2:
                        st.metric("Gold", f"{player['gold']:,} oz")
                    with col3:
                        st.metric("Turn", player['turn'])
            else:
                st.info("No active players found")
        else:
            st.error("Firebase not available")
    except Exception as e:
        st.error(f"Error loading player list: {e}")
    
    st.divider()
    
    # Mine status table
    st.markdown("## ⛏️ **Mine Status Overview**")
    
    # Debug: Show what get_all_mines_status returns
    if st.checkbox("🔍 Debug Mine Status"):
        st.write("**Debug: Mine system status:**")
        try:
            st.write(f"Firebase service: {global_mines.firebase_service is not None}")
            st.write(f"Firebase DB: {global_mines.firebase_service.db is not None if global_mines.firebase_service else 'No service'}")
            
            # Test individual mine access
            test_mine_id = "gold_creek_main"
            mine_ref = global_mines.firebase_service.db.collection('global_mines').document(test_mine_id)
            mine_doc = mine_ref.get()
            st.write(f"Test mine '{test_mine_id}' exists: {mine_doc.exists}")
            
            if mine_doc.exists:
                mine_data = mine_doc.to_dict()
                st.write(f"Mine data keys: {list(mine_data.keys()) if mine_data else 'None'}")
            
            # Show raw mines_status result
            raw_status = global_mines.get_all_mines_status()
            st.write(f"get_all_mines_status() returned {len(raw_status)} mines")
            
        except Exception as e:
            st.error(f"Debug failed: {e}")
    
    if mines_status:
        # Create status table
        mine_data = []
        for mine in sorted(mines_status, key=lambda x: x.get('level_requirement', 0)):
            last_activity = mine.get('last_activity')
            if last_activity:
                # Handle timezone-aware datetime comparison
                try:
                    if hasattr(last_activity, 'replace') and last_activity.tzinfo is not None:
                        # Convert timezone-aware to naive
                        last_activity = last_activity.replace(tzinfo=None)
                    
                    time_since = datetime.datetime.now() - last_activity
                    last_activity_str = f"{time_since.seconds // 60}m ago"
                except (TypeError, AttributeError):
                    last_activity_str = "Unknown"
            else:
                last_activity_str = "Never"
            
            mine_data.append({
                "Mine": mine.get('name', 'Unknown'),
                "Level": mine.get('level_requirement', 0),
                "Reserves": f"{mine.get('current_reserves', 0):,.0f} oz",
                "Total Mined": f"{mine.get('total_mined', 0):,.0f} oz",
                "Last Activity": last_activity_str,
                "Status": "🟢 Active" if mine.get('current_reserves', 0) > 0 else "🔴 Depleted"
            })
        
        st.dataframe(mine_data, width='stretch')
    else:
        st.warning("⚠️ No mines found. Click 'RESET ALL MINES' to initialize.")
    
    # Admin leaderboard
    if st.session_state.get('show_admin_leaderboard', False):
        st.divider()
        st.markdown("## 🏆 **Global Mining Leaderboard**")
        
        leaderboard = global_mines.get_mining_leaderboard(20)
        if leaderboard:
            for i, entry in enumerate(leaderboard):
                rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                st.markdown(f"{rank_emoji} **{entry['miner']}** - {entry['total_mined']:,.1f} oz mined")
        else:
            st.info("No mining activity yet.")
        
        if st.button("❌ Close Leaderboard"):
            st.session_state['show_admin_leaderboard'] = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def check_admin_access():
    """Check if current user has admin access"""
    global_mines = get_global_mine_system()
    return global_mines.is_admin(st.session_state.get('user_email', ''))
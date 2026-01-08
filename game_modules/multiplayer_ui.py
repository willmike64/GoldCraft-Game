import streamlit as st
import datetime
from typing import Dict, List
from .multiplayer_manager import get_multiplayer_manager

def render_multiplayer_sidebar():
    """Render multiplayer info in sidebar"""
    if not st.session_state.get('multiplayer_server_id'):
        return
    
    multiplayer_manager = get_multiplayer_manager()
    server_id = st.session_state.multiplayer_server_id
    
    # Update player activity
    if st.session_state.get('user_email') and st.session_state.get('current_character'):
        multiplayer_manager.update_player_activity(
            server_id, 
            st.session_state.user_email, 
            st.session_state.current_character
        )
    
    st.sidebar.divider()
    st.sidebar.markdown("### 🌐 Multiplayer Server")
    st.sidebar.caption(f"Server: {server_id}")
    
    # Get server players
    players = multiplayer_manager.get_server_players(server_id)
    online_players = [p for p in players if p.get('status') == 'online']
    
    st.sidebar.metric("Online Players", f"{len(online_players)}/4")
    
    # Show player list
    for player in online_players:
        char_name = player.get('character_name', 'Unknown')
        if char_name == st.session_state.get('current_character'):
            st.sidebar.markdown(f"🟢 **{char_name}** (You)")
        else:
            st.sidebar.markdown(f"🟢 {char_name}")
    
    # Quick chat
    with st.sidebar.expander("💬 Quick Chat"):
        message = st.text_input("Message", key="quick_chat", placeholder="Say something...")
        if st.button("Send", key="send_chat") and message:
            multiplayer_manager.broadcast_message(
                server_id,
                st.session_state.user_email,
                st.session_state.current_character,
                message
            )
            st.rerun()

def render_multiplayer_panel():
    """Render full multiplayer panel"""
    if not st.session_state.get('multiplayer_server_id'):
        st.error("Not connected to multiplayer server")
        return
    
    multiplayer_manager = get_multiplayer_manager()
    server_id = st.session_state.multiplayer_server_id
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# 🌐 **MULTIPLAYER SERVER**")
    st.markdown(f"*Server ID: {server_id}*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Server Chat")
        
        # Chat messages
        messages = multiplayer_manager.get_server_chat(server_id, 10)
        
        chat_container = st.container()
        with chat_container:
            if messages:
                for msg in messages[-10:]:  # Show last 10 messages
                    sender = msg.get('sender_name', 'Unknown')
                    text = msg.get('message', '')
                    timestamp = msg.get('timestamp')
                    
                    if timestamp:
                        time_str = timestamp.strftime('%H:%M') if hasattr(timestamp, 'strftime') else str(timestamp)[:5]
                    else:
                        time_str = "??:??"
                    
                    if sender == st.session_state.get('current_character'):
                        st.markdown(f"**[{time_str}] You:** {text}")
                    else:
                        st.markdown(f"[{time_str}] **{sender}:** {text}")
            else:
                st.info("No messages yet. Start the conversation!")
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            chat_message = st.text_input("Type your message...", key="chat_input")
            if st.form_submit_button("Send Message"):
                if chat_message.strip():
                    multiplayer_manager.broadcast_message(
                        server_id,
                        st.session_state.user_email,
                        st.session_state.current_character,
                        chat_message.strip()
                    )
                    st.rerun()
    
    with col2:
        st.markdown("### 👥 Players Online")
        
        players = multiplayer_manager.get_server_players(server_id)
        online_players = [p for p in players if p.get('status') == 'online']
        
        st.metric("Connected", f"{len(online_players)}/4")
        
        for player in online_players:
            char_name = player.get('character_name', 'Unknown')
            email = player.get('email', 'unknown@email.com')
            joined_at = player.get('joined_at')
            
            if joined_at:
                join_time = joined_at.strftime('%H:%M') if hasattr(joined_at, 'strftime') else "??:??"
            else:
                join_time = "??:??"
            
            if char_name == st.session_state.get('current_character'):
                st.markdown(f"🟢 **{char_name}** (You)")
                st.caption(f"Joined: {join_time}")
            else:
                st.markdown(f"🟢 **{char_name}**")
                st.caption(f"Joined: {join_time}")
        
        # Fill empty slots
        for i in range(4 - len(online_players)):
            st.markdown(f"⚫ *Empty Slot {len(online_players) + i + 1}*")
        
        st.divider()
        
        # Server actions
        if st.button("🔄 Refresh Server", width='stretch'):
            st.rerun()
        
        if st.button("🚪 Leave Server", width='stretch'):
            multiplayer_manager.leave_server(
                server_id,
                st.session_state.user_email,
                st.session_state.current_character
            )
            if 'multiplayer_server_id' in st.session_state:
                del st.session_state['multiplayer_server_id']
            st.success("Left multiplayer server")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_multiplayer_mining_activity(mine_name: str, player_name: str, gold_found: float):
    """Show real-time mining activity to all players"""
    if not st.session_state.get('multiplayer_server_id'):
        return
    
    multiplayer_manager = get_multiplayer_manager()
    server_id = st.session_state.multiplayer_server_id
    
    # Broadcast mining activity
    message = f"⛏️ Found {gold_found:.1f} oz gold at {mine_name}!"
    multiplayer_manager.broadcast_message(
        server_id,
        st.session_state.user_email,
        player_name,
        message
    )

def get_server_status():
    """Get current server status for display"""
    if not st.session_state.get('multiplayer_server_id'):
        return {"connected": False, "players": 0, "server_id": None}
    
    multiplayer_manager = get_multiplayer_manager()
    server_id = st.session_state.multiplayer_server_id
    players = multiplayer_manager.get_server_players(server_id)
    online_players = [p for p in players if p.get('status') == 'online']
    
    return {
        "connected": True,
        "players": len(online_players),
        "server_id": server_id,
        "player_list": [p.get('character_name', 'Unknown') for p in online_players]
    }
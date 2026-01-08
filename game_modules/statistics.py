import streamlit as st
from game_modules.firebase_service import get_firebase_service

def render_statistics():
    st.markdown("## 📊 Expedition Statistics & Leaderboard")
    st.caption("Your impact on the world below")

    # Tabs for different views
    tab1, tab2 = st.tabs(["📈 Your Stats", "🏆 Leaderboard"])
    
    with tab1:
        render_player_stats()
    
    with tab2:
        render_leaderboard()

def render_player_stats():
    """Render individual player statistics."""
    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("⏳ Turn", st.session_state.turn)
    col2.metric("💰 Gold", f"{st.session_state.gold:,}")
    col3.metric("🧭 Depth Layer", st.session_state.depth_layer)

    st.divider()

    st.markdown("### 🤝 Reputation by Faction")

    if not st.session_state.reputation:
        st.info("No faction interactions yet.")
    else:
        for faction, value in st.session_state.reputation.items():
            st.progress(min(max(value, 0), 10) / 10, text=f"{faction}: {value}")

    st.divider()

    st.markdown("### 🗺️ Exploration")

    visited = len(st.session_state.visited_sites)
    st.metric("Sites Visited", visited)

    st.divider()

    if st.button("⬅️ Return to Menu"):
        st.session_state.current_view = "menu"
        st.rerun()

def render_leaderboard():
    """Render the global leaderboard."""
    firebase_service = get_firebase_service()
    
    st.markdown("### 🏆 Top Prospectors of Gold Creek")
    st.caption("The most successful miners in the territory")
    
    # Get leaderboard data
    leaderboard = firebase_service.get_leaderboard(20)  # Top 20
    
    if not leaderboard:
        st.info("🔄 Loading leaderboard data...")
        return
    
    # Current player's position
    current_prospector = st.session_state.get('prospector_name')
    current_gold = st.session_state.get('gold', 0)
    
    # Display leaderboard
    st.markdown("#### 🥇 Hall of Fame")
    
    for i, player in enumerate(leaderboard[:10], 1):
        # Determine medal/rank emoji
        if i == 1:
            rank_emoji = "🥇"
        elif i == 2:
            rank_emoji = "🥈"
        elif i == 3:
            rank_emoji = "🥉"
        else:
            rank_emoji = f"#{i}"
        
        # Highlight current player
        if player['prospector_name'] == current_prospector:
            st.success(f"**{rank_emoji} {player['prospector_name']}** - {player['gold']:,} oz gold (Turn {player['turn']}) ⭐ YOU")
        else:
            st.write(f"**{rank_emoji} {player['prospector_name']}** - {player['gold']:,} oz gold (Turn {player['turn']})")
    
    # Show more players if available
    if len(leaderboard) > 10:
        with st.expander(f"📋 View More Players ({len(leaderboard)-10} more)"):
            for i, player in enumerate(leaderboard[10:], 11):
                if player['prospector_name'] == current_prospector:
                    st.success(f"**#{i} {player['prospector_name']}** - {player['gold']:,} oz gold (Turn {player['turn']}) ⭐ YOU")
                else:
                    st.write(f"**#{i} {player['prospector_name']}** - {player['gold']:,} oz gold (Turn {player['turn']})")
    
    # Current player's ranking info
    st.divider()
    st.markdown("### 📊 Your Ranking")
    
    # Find current player's position
    player_rank = None
    for i, player in enumerate(leaderboard, 1):
        if player['prospector_name'] == current_prospector:
            player_rank = i
            break
    
    if player_rank:
        if player_rank <= 3:
            st.success(f"🎉 **Congratulations!** You're ranked #{player_rank} with {current_gold:,} oz gold!")
        elif player_rank <= 10:
            st.info(f"⭐ **Great job!** You're in the top 10 at rank #{player_rank} with {current_gold:,} oz gold!")
        else:
            st.info(f"📈 **Keep mining!** You're ranked #{player_rank} with {current_gold:,} oz gold.")
    else:
        st.warning("🔄 Your ranking will appear after your first save. Keep mining!")
    
    # Update leaderboard button
    if st.button("🔄 Update My Stats", type="secondary"):
        email = st.session_state.get('user_email')
        prospector_name = st.session_state.get('prospector_name')
        if email and prospector_name:
            firebase_service.update_leaderboard_stats(
                email, prospector_name,
                int(st.session_state.get('gold', 50)),
                st.session_state.get('turn', 1)
            )
            st.success("📊 Stats updated! Refresh to see changes.")
            st.rerun()

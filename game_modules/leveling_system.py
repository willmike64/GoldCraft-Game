# leveling_system.py
import streamlit as st
import math

def calculate_xp_for_level(level):
    """Calculate total XP required to reach a specific level (easier early levels)."""
    if level <= 1:
        return 0
    # Much easier early levels, then gradual increase
    base_xp = 50  # Reduced from 100
    if level <= 5:
        return int(base_xp * (level - 1) * 0.8)  # Very easy first 5 levels
    elif level <= 10:
        return int(base_xp * 4 * 0.8 + base_xp * (level - 5) * 1.0)  # Easy levels 6-10
    elif level <= 20:
        return int(base_xp * 4 * 0.8 + base_xp * 5 * 1.0 + base_xp * (level - 10) * 1.5)
    elif level <= 40:
        return int(base_xp * 4 * 0.8 + base_xp * 5 * 1.0 + base_xp * 10 * 1.5 + base_xp * (level - 20) * 2.0)
    else:
        return int(base_xp * 4 * 0.8 + base_xp * 5 * 1.0 + base_xp * 10 * 1.5 + base_xp * 20 * 2.0 + base_xp * (level - 40) * 2.5)

def get_level_from_xp(total_xp):
    """Get current level based on total XP."""
    for level in range(1, 61):
        if total_xp < calculate_xp_for_level(level + 1):
            return level
    return 60  # Max level

def get_xp_for_next_level(current_level):
    """Get XP needed for next level."""
    if current_level >= 60:
        return 0
    return calculate_xp_for_level(current_level + 1) - calculate_xp_for_level(current_level)

def award_xp(amount, activity=""):
    """Award XP and handle level ups."""
    if 'xp' not in st.session_state:
        st.session_state.xp = 0
    if 'level' not in st.session_state:
        st.session_state.level = 1
    
    old_level = st.session_state.level
    st.session_state.xp += amount
    new_level = get_level_from_xp(st.session_state.xp)
    
    if new_level > old_level:
        st.session_state.level = new_level
        st.balloons()
        st.success(f"🎉 **LEVEL UP!** You reached Level {new_level}!")
        
        # Level up rewards
        gold_reward = new_level * 10
        st.session_state.gold = st.session_state.get('gold', 0) + gold_reward
        st.info(f"💰 Level up bonus: +{gold_reward} oz gold!")
        
        # Analytics
        try:
            from .analytics_service import analytics
            analytics.log_action(st.session_state.get('user_email', 'unknown'), "level_up", {
                "old_level": old_level,
                "new_level": new_level,
                "total_xp": st.session_state.xp,
                "activity": activity
            })
        except:
            pass  # Analytics is optional
        
        return True
    return False

def get_level_title(level):
    """Get title based on level."""
    if level >= 60:
        return "🏆 Legendary Prospector"
    elif level >= 50:
        return "💎 Master Prospector"
    elif level >= 40:
        return "⭐ Expert Prospector"
    elif level >= 30:
        return "🥇 Veteran Prospector"
    elif level >= 20:
        return "🥈 Skilled Prospector"
    elif level >= 10:
        return "🥉 Experienced Prospector"
    else:
        return "⛏️ Novice Prospector"

def render_level_display():
    """Render level display in sidebar."""
    xp = st.session_state.get('xp', 0)
    
    # Recalculate level from XP to ensure consistency
    correct_level = get_level_from_xp(xp)
    current_level = st.session_state.get('level', 1)
    
    # Update level if it's incorrect
    if correct_level != current_level:
        st.session_state.level = correct_level
        level = correct_level
    else:
        level = current_level
    
    # Calculate progress
    current_level_xp = calculate_xp_for_level(level)
    next_level_xp = calculate_xp_for_level(level + 1) if level < 60 else current_level_xp
    xp_in_level = xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    
    st.sidebar.markdown("### ⭐ Character Level")
    st.sidebar.metric("Level", f"{level}", delta=get_level_title(level))
    
    if level < 60:
        progress = min(1.0, max(0.0, xp_in_level / xp_needed)) if xp_needed > 0 else 1.0
        st.sidebar.progress(progress, text=f"XP: {xp_in_level}/{xp_needed}")
    else:
        st.sidebar.success("🏆 MAX LEVEL!")

def get_xp_rewards():
    """Get XP reward amounts for different activities."""
    return {
        'expedition_complete': 50,
        'gold_found': 1,  # 1 XP per oz of gold
        'site_discovered': 100,
        'mini_game_win': 25,
        'purchase_made': 5,
        'investment_made': 20,
        'turn_complete': 10
    }
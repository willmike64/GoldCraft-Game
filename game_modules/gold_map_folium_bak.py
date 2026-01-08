import streamlit as st
import folium
from streamlit_folium import st_folium
import random

def render_gold_map_folium():
    """Render the gold mining map using Folium with expedition functionality"""
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# 🗺️ **CALIFORNIA GOLD COUNTRY**")
    st.markdown("*Navigate the dimensional mining sites*")
    
    # Create map centered on California Gold Country
    m = folium.Map(
        location=[39.0, -121.0],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # Add mining sites
    mining_sites = [
        {"name": "Gold Creek Main Vein", "lat": 38.8, "lon": -121.2, "level": 1, "difficulty": "Easy"},
        {"name": "Coloma Bar", "lat": 38.8, "lon": -120.9, "level": 1, "difficulty": "Easy"},
        {"name": "Nevada City Drift", "lat": 39.3, "lon": -121.0, "level": 16, "difficulty": "Hard"},
        {"name": "Grass Valley Lode", "lat": 39.2, "lon": -121.1, "level": 26, "difficulty": "Extreme"},
    ]
    
    for site in mining_sites:
        color = 'green' if site['difficulty'] == 'Easy' else 'orange' if site['difficulty'] == 'Hard' else 'red'
        folium.Marker(
            [site["lat"], site["lon"]],
            popup=f"{site['name']} (Level {site['level']}) - {site['difficulty']}",
            tooltip=site["name"],
            icon=folium.Icon(color=color, icon='star')
        ).add_to(m)
    
    # Display map
    map_data = st_folium(m, width=700, height=500)
    
    st.divider()
    
    # Expedition Creation Section
    st.markdown("### ⛏️ **CREATE EXPEDITION**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_site = st.selectbox(
            "🎯 Select Mining Site",
            options=[site['name'] for site in mining_sites],
            help="Choose your destination"
        )
        
        expedition_type = st.selectbox(
            "⚒️ Expedition Type",
            options=["Surface Mining", "Shaft Mining", "Placer Mining", "Hydraulic Mining"],
            help="Different methods yield different results"
        )
    
    with col2:
        crew_size = st.slider("👥 Crew Size", 1, 10, 3, help="More crew = higher costs but better results")
        duration = st.slider("⏰ Duration (days)", 1, 30, 7, help="Longer expeditions cost more but yield more")
    
    # Calculate costs and potential rewards
    site_data = next(site for site in mining_sites if site['name'] == selected_site)
    base_cost = crew_size * duration * 10
    difficulty_multiplier = {'Easy': 1.0, 'Hard': 1.5, 'Extreme': 2.0}[site_data['difficulty']]
    total_cost = int(base_cost * difficulty_multiplier)
    
    potential_gold = crew_size * duration * random.uniform(5, 20) * difficulty_multiplier
    
    st.markdown("### 💰 **EXPEDITION DETAILS**")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric("💸 Total Cost", f"${total_cost:,}")
    with col4:
        st.metric("🏆 Potential Gold", f"{potential_gold:.1f} oz")
    with col5:
        st.metric("⚖️ Risk Level", site_data['difficulty'])
    
    # Launch expedition button
    if st.button("🚀 **LAUNCH EXPEDITION**", type="primary", use_container_width=True):
        if st.session_state.get('gold', 0) >= total_cost:
            # Deduct cost
            st.session_state.gold -= total_cost
            
            # Calculate actual results
            success_rate = {'Easy': 0.8, 'Hard': 0.6, 'Extreme': 0.4}[site_data['difficulty']]
            if random.random() < success_rate:
                # Success
                actual_gold = random.uniform(potential_gold * 0.7, potential_gold * 1.3)
                st.session_state.gold += int(actual_gold)
                st.success(f"🎉 **EXPEDITION SUCCESS!** Found {actual_gold:.1f} oz of gold!")
                
                # Add to visited sites
                if 'visited_sites' not in st.session_state:
                    st.session_state.visited_sites = set()
                st.session_state.visited_sites.add(selected_site)
                
                # Advance turn
                st.session_state.turn = st.session_state.get('turn', 1) + duration
                
            else:
                # Failure
                loss = random.uniform(0.1, 0.3)
                actual_gold = potential_gold * loss
                st.session_state.gold += int(actual_gold)
                st.error(f"⚠️ **EXPEDITION STRUGGLED** Only found {actual_gold:.1f} oz of gold.")
                st.session_state.turn = st.session_state.get('turn', 1) + duration
            
            st.rerun()
        else:
            st.error(f"💸 **INSUFFICIENT FUNDS!** Need ${total_cost:,} but only have ${st.session_state.get('gold', 0):,}")
    
    # Show current resources
    st.divider()
    col6, col7, col8 = st.columns(3)
    with col6:
        st.metric("💰 Current Gold", f"${st.session_state.get('gold', 50):,}")
    with col7:
        st.metric("🗓️ Current Turn", st.session_state.get('turn', 1))
    with col8:
        visited_count = len(st.session_state.get('visited_sites', set()))
        st.metric("🏴 Sites Visited", visited_count)
    
    st.markdown('</div>', unsafe_allow_html=True)
# gold_map_folium.py
import streamlit as st # type: ignore
import pandas as pd # type: ignore
from streamlit_folium import st_folium # type: ignore
import folium # type: ignore
from folium import plugins # type: ignore
from branca.element import Element  # type: ignore # public/safe
import time
import random

STRATA_LAYERS = {
    "Surface": {
        "description": "Shallow claims, low risk, limited yield",
        "allowed_statuses": ["active", "depleting"],
        "risk_modifier": 0,
    },
    "Industrial Veins": {
        "description": "Deep commercial mining zones",
        "allowed_statuses": ["active", "depleting", "unexplored"],
        "risk_modifier": 1,
    },
    "Ancient Caverns": {
        "description": "Old-world shafts and forgotten tunnels",
        "allowed_statuses": ["unexplored", "abandoned"],
        "risk_modifier": 2,
    },
    "Ghost Layers": {
        "description": "Legends, collapses, and things best left alone",
        "allowed_statuses": ["abandoned"],
        "risk_modifier": 3,
    },
}

def process_dividend_payments():
    """Process dividend payments from mine investments every 3 turns."""
    current_turn = st.session_state.get('turn', 1)
    investments = st.session_state.get('mine_investments', {})
    
    if not investments:
        return
    
    total_dividends = 0
    dividend_messages = []
    
    for mine_name, investment in investments.items():
        turns_since_last = current_turn - investment['last_dividend_turn']
        
        # Pay dividends every 3 turns (monthly)
        if turns_since_last >= 3:
            # Calculate dividend with risk factor
            base_dividend = investment['monthly_dividend']
            risk_factor = 1.0 - (investment['risk_level'] - 1) * 0.1  # Higher risk = lower reliability
            
            # Random chance based on risk (85% chance for low risk, 45% for extreme risk)
            success_chance = max(0.45, 0.85 - (investment['risk_level'] - 1) * 0.1)
            
            import random
            if random.random() < success_chance:
                dividend = base_dividend * risk_factor
                total_dividends += dividend
                investment['total_dividends'] = investment.get('total_dividends', 0) + dividend
                dividend_messages.append(f"💰 {mine_name}: +{dividend:.1f} oz")
            else:
                dividend_messages.append(f"⚠️ {mine_name}: No dividend (operational issues)")
            
            investment['last_dividend_turn'] = current_turn
    
    if total_dividends > 0:
        st.session_state.gold = st.session_state.get('gold', 0) + total_dividends
        st.sidebar.success(f"💰 Dividends: +{total_dividends:.1f} oz")
        
        with st.sidebar.expander("💼 Investment Report"):
            for msg in dividend_messages:
                st.write(msg)
    elif dividend_messages:
        with st.sidebar.expander("💼 Investment Report"):
            for msg in dividend_messages:
                st.write(msg)

def render_gold_map_folium():
    st.title("🗺️ Mining Expedition Command Center")
    st.caption("📡 Select mining sites for resource extraction missions • 💰 Plan expeditions carefully - costs and risks vary!")

    # Strata Depth Selection
    st.subheader("🧭 Strata Depth")

    if "current_strata" not in st.session_state:
        st.session_state.current_strata = "Surface"

    selected_strata = st.selectbox(
        "Current Layer",
        list(STRATA_LAYERS.keys()),
        index=list(STRATA_LAYERS.keys()).index(st.session_state.current_strata) if st.session_state.current_strata in STRATA_LAYERS.keys() else 0,
    )

    st.session_state.current_strata = selected_strata
    st.caption(STRATA_LAYERS[selected_strata]["description"])
    
    # Load mining sites data
    df = _gold_sites_df()

    # Initialize expedition state
    if 'expedition_unlocked_sites' not in st.session_state:
        st.session_state.expedition_unlocked_sites = []
    if 'expedition_history' not in st.session_state:
        st.session_state.expedition_history = []

    # Display mine blockchain status in sidebar
    with st.sidebar:
        st.markdown("### 🏔️ Live Mine Status")
        
        from .firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        # Get all active mines from blockchain
        mine_names = ['gold_creek_main_vein', 'feather_fork_#3', 'grass_valley_lode', 'angels_reef', 'nevada_city_drift']
        
        for mine_name in mine_names:
            mine_status = firebase_service.get_mine_status(mine_name)
            if mine_status and mine_status.get('reserves', 0) > 0:
                reserves = mine_status.get('reserves', 0)
                miners = len(mine_status.get('miners', []))
                display_name = mine_name.replace('_', ' ').replace('#', '#').title()
                st.metric(
                    display_name,
                    f"{reserves:.0f} oz",
                    f"{miners} miners"
                )
        
        st.subheader("🎮 Mission Control")
        
        # Current resources
        player_gold = st.session_state.get('gold', 0)
        st.metric("Available Gold", f"{player_gold:.1f} oz")
        
        # Filter controls
        st.subheader("🔍 Site Filters")
        show_active = st.checkbox("Active Sites", True)
        show_depleting = st.checkbox("Depleting Sites", True) 
        show_unexplored = st.checkbox("Unexplored Sites", True)
        show_abandoned = st.checkbox("Abandoned Sites", False)
        
        show_veins = st.checkbox("Vein Mines", True)
        show_rivers = st.checkbox("River Sites", True)
        
        # Legend
        st.subheader("📋 Site Status Legend")
        st.markdown("""
        **🟡 Active** - Rich, operational sites  
        **🟤 Depleting** - Partially worked, safer  
        **🟣 Unexplored** - Unknown potential, risky  
        **🔴 Abandoned** - Dangerous, high reward potential  
        
        **Site Types:**  
        <span style="color: #DAA520;">●</span> Vein Mines  
        <span style="color: #1E88E5;">●</span> River Claims
        """, unsafe_allow_html=True)
        
        st.subheader("📊 Mission Statistics")
        st.markdown(f"**Missions Completed:** {len(st.session_state.expedition_history)}")
        st.markdown(f"**Sites Unlocked:** {len(st.session_state.expedition_unlocked_sites)}")

    # Apply filters
    status_filter = []
    if show_active: status_filter.append("active")
    if show_depleting: status_filter.append("depleting") 
    if show_unexplored: status_filter.append("unexplored")
    if show_abandoned: status_filter.append("abandoned")
    
    type_filter = []
    if show_veins: type_filter.append("vein")
    if show_rivers: type_filter.append("river")

    strata = STRATA_LAYERS[st.session_state.current_strata]
    allowed_statuses = strata["allowed_statuses"]
    
    # Level-based filtering
    player_level = st.session_state.get('level', 1)

    filtered = df[
        (df["status"].isin(status_filter)) &
        (df["type"].isin(type_filter)) &
        (df["status"].isin(allowed_statuses)) &
        (df["min_level"] <= player_level)
    ].copy()

    # Main map display
    m = folium.Map(
        location=[38.92, -120.75],  # Gold Creek coordinates
        zoom_start=13,  # Closer zoom for better initial view
        tiles="CartoDB Positron",
        control_scale=True
    )

    st.caption(f"📡 Scanning {len(filtered)} mining sites for expedition opportunities...")

    # Inject CSS
    m.get_root().add_child(Element(PULSE_CSS))

    # Map controls
    plugins.MiniMap(toggle_display=True, minimized=True).add_to(m)
    plugins.Fullscreen().add_to(m)

    # Mining sites
    fg = folium.FeatureGroup(name="Mining Expedition Sites", show=True).add_to(m)

    for idx, rec in enumerate(filtered.to_dict("records")):
        marker_class = "vein" if rec["type"] == "vein" else "river"
        status = rec["status"]
        delay = (idx * 120) % 1800
        html = _pulse_marker_html(marker_class, status, delay_ms=delay)

        # Base circle marker (always visible)
        color_map = {
            "active": "#DAA520" if marker_class == "vein" else "#1E88E5",
            "depleting": "#8B4513" if marker_class == "vein" else "#4682B4", 
            "unexplored": "#800080" if marker_class == "vein" else "#191970",
            "abandoned": "#DC143C" if marker_class == "vein" else "#B22222"
        }
        
        folium.CircleMarker(
            location=[rec["lat"], rec["lon"]],
            radius=8,
            color="#000000",
            weight=2,
            fill=True,
            fill_color=color_map[status],
            fill_opacity=0.9,
            tooltip=f"{rec['name']} ({rec['status'].title()})",
        ).add_to(fg)

        # Pulsing overlay
        icon = folium.DivIcon(
            html=html,
            class_name="pulse-dot",
            icon_size=(16, 16),
            icon_anchor=(8, 8),
        )

        # Enhanced popup with expedition details
        popup_html = create_expedition_popup(rec)

        folium.Marker(
            location=[rec["lat"], rec["lon"]],
            icon=icon,
            popup=folium.Popup(popup_html, max_width=400, class_name="expedition-popup"),
            z_index_offset=1000,
        ).add_to(fg)

    # Gold Creek base marker
    folium.Marker(
        location=[38.92, -120.75],
        icon=folium.DivIcon(html='<div class="gc-label"> Gold Creek Base</div>', class_name=""),
        tooltip="Gold Creek Mining Operations Base",
    ).add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)

    # Render map
    map_state = st_folium(m, width=None, height=700)

    # Handle expedition selection
    if map_state and map_state.get("last_object_clicked_popup"):
        handle_expedition_selection(map_state, df)

    # Process dividend payments every 3 turns (monthly)
    process_dividend_payments()
    
    # Expedition history
    if st.session_state.expedition_history:
        with st.expander("📜 Recent Expedition History"):
            for expedition in st.session_state.expedition_history[-10:]:  # Last 10
                st.markdown(f"• **{expedition['site']}**: {expedition['result']} (Day {expedition.get('day', '?')})")

    st.markdown("---")
    if st.button("🏠 Return to Gold Creek Base", width='stretch'):
        st.session_state.current_view = "menu"
        st.rerun()

def _gold_sites_df():
    """Mining expedition sites with StarCraft-style resource mechanics."""
    import random
    import math
    
    # Gold Creek coordinates for distance calculations
    gold_creek_lat, gold_creek_lon = 38.92, -120.75
    
    def calculate_distance(lat, lon):
        """Calculate distance from Gold Creek in miles (simplified)."""
        return round(math.sqrt((lat - gold_creek_lat)**2 + (lon - gold_creek_lon)**2) * 69, 1)
    
    def calculate_costs(distance, difficulty):
        """Calculate expedition costs based on distance and terrain difficulty."""
        base_travel = distance * 2  # Round trip cost
        security_cost = max(10, distance * 1.5 * difficulty)  # Anti-bandit protection
        equipment_cost = 5 + (difficulty * 3)  # Mining equipment transport
        return {
            'travel': round(base_travel),
            'security': round(security_cost), 
            'equipment': round(equipment_cost),
            'total': round(base_travel + security_cost + equipment_cost)
        }
    
    # Enhanced mining site data with level restrictions and more locations
    sites_data = [
        # LEVEL 1-5: Beginner Sites (Safe, Low Rewards)
        ("Gold Creek Main Vein", 38.92, -120.75, "vein", 5000, 5500, 1, "active", "Town's main claim - safely operated", 1),
        ("Coloma Bar", 38.88, -120.76, "river", 1200, 1500, 1, "active", "Prime panning location, well-patrolled", 1),
        ("Yuba Bend", 38.90, -120.72, "river", 800, 1000, 1, "active", "North Yuba bar, safe but lower yields", 3),
        ("Auburn Ravine", 38.90, -120.78, "river", 600, 800, 1, "depleting", "Shallow diggings, very safe", 5),
        
        # LEVEL 6-15: Novice Sites (Moderate Risk/Reward)
        ("Mokelumne Cut", 38.89, -120.73, "river", 1500, 2000, 2, "active", "Bank diggings, moderate yields", 6),
        ("Jamestown Flats", 38.88, -120.74, "river", 2200, 2800, 2, "active", "Placer deposits, some bandit activity", 8),
        ("Placerville Reef", 38.94, -120.74, "vein", 3500, 4200, 2, "active", "High grade but narrow vein", 10),
        ("Downie Ridge Vein", 38.95, -120.76, "vein", 4800, 5800, 2, "active", "Visible gold in quartz", 12),
        ("Feather Fork #3", 38.94, -120.78, "river", 6200, 7200, 2, "active", "Rich gravels, moderate bandits", 15),
        
        # LEVEL 16-25: Skilled Sites (Higher Risk/Reward)
        ("Nevada City Drift", 38.93, -120.73, "vein", 8800, 9600, 3, "active", "Ancient channels, security risk", 16),
        ("Angels Reef", 38.95, -120.77, "vein", 12500, 14000, 3, "active", "Wide quartz ribbon, bandit gangs", 18),
        ("Rough and Ready Mine", 38.91, -120.74, "vein", 15000, 17000, 3, "active", "Deep shafts, cave-in risks", 20),
        ("French Gulch", 38.87, -120.76, "river", 11000, 13000, 3, "active", "Rich but dangerous terrain", 22),
        ("Smartsville Diggings", 38.89, -120.75, "river", 18000, 20000, 3, "active", "Hydraulic mining site", 25),
        
        # LEVEL 26-35: Veteran Sites (High Risk/Reward)
        ("Grass Valley Lode", 38.89, -120.77, "vein", 25000, 28000, 4, "active", "Legendary deep lodes, heavy bandits", 26),
        ("Empire Mine", 38.88, -120.78, "vein", 32000, 35000, 4, "active", "Massive underground complex", 28),
        ("North Star Mine", 38.90, -120.79, "vein", 28000, 31000, 4, "active", "Deep shaft mining, dangerous", 30),
        ("Malakoff Diggins", 38.92, -120.80, "river", 22000, 25000, 4, "active", "Hydraulic devastation site", 32),
        ("Cherokee Mine", 38.85, -120.75, "vein", 38000, 42000, 4, "active", "Ancient river channel", 35),
        
        # LEVEL 36-45: Expert Sites (Very High Risk/Reward)
        ("Alleghany Mine", 38.83, -120.73, "vein", 45000, 50000, 5, "active", "Remote mountain mine, extreme danger", 36),
        ("Forest City Mine", 38.84, -120.74, "vein", 52000, 58000, 5, "active", "Ghost town mine, bandit stronghold", 38),
        ("Washington Mine", 38.82, -120.76, "vein", 48000, 54000, 5, "active", "Collapsed tunnels, treasure hunters", 40),
        ("Downieville Drift", 38.81, -120.75, "vein", 55000, 62000, 5, "active", "Mountain fortress mine", 42),
        ("Sierra Buttes Mine", 38.80, -120.77, "vein", 62000, 70000, 5, "active", "High altitude, extreme conditions", 45),
        
        # LEVEL 46-55: Master Sites (Extreme Risk/Reward)
        ("Tuolumne Quartz", 38.93, -120.76, "vein", 75000, 85000, 6, "unexplored", "High-sulfide ore, expert assessment needed", 46),
        ("Columbia Pocket", 38.91, -120.72, "vein", 68000, 78000, 6, "unexplored", "Spectacular nuggets rumored", 48),
        ("Merced Shine", 38.90, -120.77, "river", 58000, 68000, 6, "unexplored", "Fine gold, requires advanced equipment", 50),
        ("Calaveras Grove Mine", 38.79, -120.78, "vein", 85000, 95000, 6, "abandoned", "Ancient giant sequoia mine", 52),
        ("Moaning Cavern Mine", 38.78, -120.79, "vein", 92000, 105000, 6, "abandoned", "Underground cavern system", 55),
        
        # LEVEL 56-60: Legendary Sites (Ultimate Challenge)
        ("Dead Man's Gulch", 38.87, -120.79, "vein", 120000, 140000, 7, "abandoned", "Legendary strike, bandit massacre site", 56),
        ("Widow's Peak Mine", 38.96, -120.74, "vein", 110000, 130000, 7, "abandoned", "Collapsed tunnels, ghost stories", 58),
        ("El Dorado Mother Lode", 38.77, -120.80, "vein", 150000, 180000, 8, "abandoned", "The ultimate prize, maximum danger", 60),
    ]
    
    processed_data = []
    for site in sites_data:
        name, lat, lon, mine_type, current_gold, max_gold, difficulty, status, notes, min_level = site
        distance = calculate_distance(lat, lon)
        costs = calculate_costs(distance, difficulty)
        
        processed_data.append([
            name, lat, lon, mine_type, current_gold, max_gold, difficulty, status, notes, 
            distance, costs['travel'], costs['security'], costs['equipment'], costs['total'], min_level
        ])
    
    return pd.DataFrame(processed_data, columns=[
        "name", "lat", "lon", "type", "current_gold", "max_gold", "difficulty", 
        "status", "notes", "distance_miles", "travel_cost", "security_cost", 
        "equipment_cost", "total_cost", "min_level"
    ])

# CSS: Enhanced pulse animations for different mine statuses
PULSE_CSS = """
<style>
.leaflet-marker-icon.pulse-dot, .leaflet-marker-shadow.pulse-dot { background: none; border: none; }
.leaflet-marker-icon.pulse-dot { z-index: 10000 !important; }

@keyframes pulse-dot {
  0%   { transform: scale(0.9); opacity: 0.95; }
  50%  { transform: scale(1.15); opacity: 1.0; }
  100% { transform: scale(0.9); opacity: 0.95; }
}
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(0,0,0,0.35); }
  70%  { box-shadow: 0 0 0 14px rgba(0,0,0,0); }
  100% { box-shadow: 0 0 0 0 rgba(0,0,0,0); }
}
@keyframes slow-pulse {
  0%   { transform: scale(1.0); opacity: 0.7; }
  50%  { transform: scale(1.05); opacity: 0.9; }
  100% { transform: scale(1.0); opacity: 0.7; }
}
@keyframes danger-pulse {
  0%   { transform: scale(0.8); opacity: 0.8; box-shadow: 0 0 5px red; }
  50%  { transform: scale(1.2); opacity: 1.0; box-shadow: 0 0 15px red; }
  100% { transform: scale(0.8); opacity: 0.8; box-shadow: 0 0 5px red; }
}

.pulse {
  position: relative;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  animation: pulse-dot 1.8s ease-in-out infinite;
  will-change: transform, opacity;
}

/* Mine status-based styling */
.pulse.vein.active  { background: rgba(218,165,32,0.95); box-shadow: 0 0 6px rgba(218,165,32,0.9); }
.pulse.river.active { background: rgba(30,136,229,0.95); box-shadow: 0 0 6px rgba(30,136,229,0.9); }

.pulse.vein.depleting  { background: rgba(139,69,19,0.8); animation: slow-pulse 3s ease-in-out infinite; }
.pulse.river.depleting { background: rgba(70,130,180,0.8); animation: slow-pulse 3s ease-in-out infinite; }

.pulse.vein.unexplored  { background: rgba(128,0,128,0.9); box-shadow: 0 0 8px rgba(128,0,128,0.7); }
.pulse.river.unexplored { background: rgba(25,25,112,0.9); box-shadow: 0 0 8px rgba(25,25,112,0.7); }

.pulse.vein.abandoned  { background: rgba(220,20,60,0.9); animation: danger-pulse 2s ease-in-out infinite; }
.pulse.river.abandoned { background: rgba(178,34,34,0.9); animation: danger-pulse 2s ease-in-out infinite; }

.pulse::after {
  content: "";
  position: absolute; left: -2px; top: -2px; right: -2px; bottom: -2px;
  border-radius: 50%;
  animation: pulse-ring 1.8s ease-out infinite;
}

.gc-label {
  background: rgba(255,255,255,0.9);
  padding: 4px 8px;
  border-radius: 10px;
  border: 2px solid #222;
  font-weight: 700;
  font-size: 14px;
}

.expedition-popup {
  max-width: 350px !important;
  font-family: 'Courier New', monospace;
}
</style>
"""

def _pulse_marker_html(marker_class: str, status: str, delay_ms: int = 0) -> str:
    """Generate HTML for pulsing markers based on mine type and status."""
    return f'<div class="pulse {marker_class} {status}" style="animation-delay:{delay_ms}ms;"></div>'

def create_expedition_popup(site_data):
    """Create detailed expedition popup with StarCraft-style information."""
    name = site_data['name']
    site_type = site_data['type'].title()
    status = site_data['status'].title()
    distance = site_data['distance_miles']
    
    # Resource information
    if site_data['current_gold'] is not None:
        current_gold = f"{site_data['current_gold']:,} oz"
        max_gold = f"{site_data['max_gold']:,} oz"
        depletion = round((site_data['current_gold'] / site_data['max_gold']) * 100, 1)
        resource_info = f"""
        <strong>📊 Resource Analysis:</strong><br/>
        Current Reserves: <span style="color: #DAA520;">{current_gold}</span><br/>
        Original Deposit: {max_gold}<br/>
        Remaining: <span style="color: {'green' if depletion > 70 else 'orange' if depletion > 30 else 'red'};">{depletion}%</span>
        """
    else:
        resource_info = """
        <strong>📊 Resource Analysis:</strong><br/>
        <span style="color: purple;">⚠️ UNKNOWN RESERVES</span><br/>
        Reconnaissance mission required
        """
    
    # Cost breakdown
    costs = f"""
    <strong>💰 Expedition Costs:</strong><br/>
    Travel ({distance} mi): <span style="color: #B8860B;">{site_data['travel_cost']} oz</span><br/>
    Security: <span style="color: #B8860B;">{site_data['security_cost']} oz</span><br/>
    Equipment: <span style="color: #B8860B;">{site_data['equipment_cost']} oz</span><br/>
    <strong>Total: <span style="color: red;">{site_data['total_cost']} oz</span></strong>
    """
    
    # Risk assessment
    difficulty = site_data['difficulty']
    risk_levels = ["Minimal", "Low", "Moderate", "High", "Extreme"]
    risk_colors = ["green", "lightgreen", "orange", "red", "darkred"]
    risk_level = risk_levels[min(difficulty-1, 4)]
    risk_color = risk_colors[min(difficulty-1, 4)]
    
    risk_info = f"""
    <strong>⚠️ Risk Assessment:</strong><br/>
    Difficulty Level: <span style="color: {risk_color};">{difficulty}/5 ({risk_level})</span><br/>
    Bandit Activity: {'High' if difficulty >= 4 else 'Moderate' if difficulty >= 3 else 'Low'}<br/>
    Terrain: {'Treacherous' if difficulty >= 4 else 'Challenging' if difficulty >= 2 else 'Manageable'}
    """
    
    # Status indicator
    status_colors = {
        "Active": "green",
        "Depleting": "orange", 
        "Unexplored": "purple",
        "Abandoned": "red"
    }
    
    return f"""
    <div style="font-family: 'Courier New', monospace; background: #1a1a1a; color: #00ff00; padding: 10px; border-radius: 5px;">
        <h3 style="color: #00ffff; margin: 0 0 10px 0; text-align: center;">
            🎯 {name}
        </h3>
        
        <div style="background: #2a2a2a; padding: 8px; margin: 5px 0; border-left: 3px solid {status_colors.get(status, 'gray')};">
            <strong>📍 Site Classification:</strong><br/>
            Type: {site_type} Mine<br/>
            Status: <span style="color: {status_colors.get(status, 'white')};">{status}</span><br/>
            Distance: {distance} miles from base
        </div>
        
        <div style="background: #2a2a2a; padding: 8px; margin: 5px 0;">
            {resource_info}
        </div>
        
        <div style="background: #2a2a2a; padding: 8px; margin: 5px 0;">
            {costs}
        </div>
        
        <div style="background: #2a2a2a; padding: 8px; margin: 5px 0;">
            {risk_info}
        </div>
        
        <div style="background: #2a2a2a; padding: 8px; margin: 5px 0;">
            <strong>📝 Intelligence Report:</strong><br/>
            <em>{site_data['notes']}</em>
        </div>
        
        <div style="text-align: center; margin-top: 10px;">
            <small style="color: #888;">Click site to launch expedition</small>
        </div>
    </div>
    """

def handle_expedition_selection(map_state, df):
    """Handle when a player clicks on a mining site to start an expedition."""
    if map_state.get("last_object_clicked_popup"):
        # Get the clicked coordinates
        clicked_lat = map_state.get("last_object_clicked", {}).get("lat")
        clicked_lng = map_state.get("last_object_clicked", {}).get("lng")
        
        if clicked_lat and clicked_lng:
            # Find the closest site to the clicked coordinates
            min_distance = float('inf')
            selected_site = None
            
            for _, site in df.iterrows():
                distance = ((site['lat'] - clicked_lat) ** 2 + (site['lon'] - clicked_lng) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    selected_site = site['name']
            
            if selected_site and min_distance < 0.01:  # Close enough threshold
                st.session_state.selected_expedition_site = selected_site
        
        with st.expander("🚀 Launch Mining Expedition", expanded=True):
            render_expedition_interface(df)

def render_expedition_interface(df):
    """Render the expedition planning and execution interface."""
    
    # Site selection - use clicked site if available
    site_names = df['name'].tolist()
    default_index = 0
    
    if st.session_state.get('selected_expedition_site'):
        try:
            default_index = site_names.index(st.session_state.selected_expedition_site)
        except ValueError:
            pass
    
    selected_site = st.selectbox("Select Mining Site:", site_names, index=default_index)
    
    if selected_site:
        site_data = df[df['name'] == selected_site].iloc[0]
        
        # Check for discovered sites and update data
        if site_data.get('current_gold') is None:
            discovered_sites = st.session_state.get('discovered_sites', {})
            if selected_site in discovered_sites:
                site_data = site_data.copy()
                discovery = discovered_sites[selected_site]
                site_data['current_gold'] = discovery['current_gold']
                site_data['max_gold'] = discovery['max_gold']
        
        # Display site summary with blockchain data
        st.markdown(f"### 🎯 {selected_site}")
        
        # Get real-time mine data
        from .firebase_service import FirebaseService
        firebase_service = FirebaseService()
        mine_status = firebase_service.get_mine_status(selected_site)
        
        if mine_status:
            current_reserves = mine_status.get('reserves', 0)
            active_miners = len(mine_status.get('miners', []))
        else:
            current_reserves = 0
            active_miners = 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Distance", f"{site_data['distance_miles']} mi")
        with col2:
            st.metric("Total Cost", f"{site_data['total_cost']} oz")
        with col3:
            risk_level = ["Minimal", "Low", "Moderate", "High", "Extreme"][min(site_data['difficulty']-1, 4)]
            st.metric("Risk Level", f"{site_data['difficulty']}/5 ({risk_level})")
        with col4:
            level_req = site_data.get('min_level', 1)
            player_level = st.session_state.get('level', 1)
            level_status = "✅ Accessible" if player_level >= level_req else "🔒 Locked"
            st.metric("Level Req", f"Level {level_req}", level_status)
        
        # Show current supplies impact
        player_supplies = st.session_state.get('supplies', {})
        total_supply_value = sum(player_supplies.values())
        
        st.markdown("### 📦 **Supply Impact Preview**")
        if total_supply_value > 15:
            st.success(f"🟢 **Excellent Supplies** ({total_supply_value} items) - Your team will perform at +30% efficiency!")
        elif total_supply_value > 8:
            st.info(f"🟡 **Good Supplies** ({total_supply_value} items) - Your team gets a +15% performance boost!")
        elif total_supply_value < 3:
            st.error(f"🔴 **Poor Supplies** ({total_supply_value} items) - Your team will suffer -30% performance penalty!")
        else:
            st.warning(f"🟠 **Basic Supplies** ({total_supply_value} items) - Your team will have -15% performance penalty.")
        
        st.info("💡 **Tip**: Visit the Town Hub to buy supplies like Food Rations, Medical Kits, and Equipment to boost your team's performance!")
        
        # Mine Investment section
        st.markdown("### 💼 Mine Investment")
        
        # Calculate investment cost and ROI
        if site_data['current_gold'] is not None:
            investment_cost = max(100, site_data['current_gold'] // 100)  # 1% of reserves, min 100 oz
            annual_yield = site_data['current_gold'] // 20  # 5% of reserves per year
            monthly_dividend = annual_yield // 12
            roi_percent = (annual_yield / investment_cost) * 100
            
            st.info(f"""
            **Investment Opportunity**: {selected_site}
            **Cost**: {investment_cost} oz gold
            **Expected Annual Yield**: {annual_yield:.1f} oz ({roi_percent:.1f}% ROI)
            **Monthly Dividend**: {monthly_dividend:.1f} oz
            **Risk Level**: {risk_level} (affects dividend reliability)
            """)
            
            # Check if already invested
            investments = st.session_state.get('mine_investments', {})
            if selected_site in investments:
                investment = investments[selected_site]
                st.success(f"✅ **Already Invested**: {investment['amount']} oz on Turn {investment['turn']}")
                st.metric("Total Dividends Earned", f"{investment.get('total_dividends', 0):.1f} oz")
            else:
                # Check if player can afford it
                player_gold = st.session_state.get('gold', 0)
                
                if player_gold >= investment_cost:
                    if st.button(f"💰 Invest {investment_cost} oz in {selected_site}", type="secondary"):
                        # Make investment
                        st.session_state.gold -= investment_cost
                        
                        if 'mine_investments' not in st.session_state:
                            st.session_state.mine_investments = {}
                        
                        st.session_state.mine_investments[selected_site] = {
                            'amount': investment_cost,
                            'turn': st.session_state.get('turn', 1),
                            'monthly_dividend': monthly_dividend,
                            'risk_level': site_data['difficulty'],
                            'total_dividends': 0,
                            'last_dividend_turn': st.session_state.get('turn', 1)
                        }
                        
                        st.success(f"🎉 Investment successful! You now own shares in {selected_site}!")
                        st.rerun()
                else:
                    st.error(f"Insufficient funds! Need {investment_cost} oz, have {player_gold:.1f} oz")
        # Check if site needs reconnaissance
        if site_data.get('current_gold') is None:
            st.markdown("### 🔍 Reconnaissance Mission Required")
            st.warning("⚠️ **Unknown Reserves** - This site needs reconnaissance before mining!")
            
            # Reconnaissance requirements
            recon_cost = 150  # Base cost
            crew_required = 5
            rations_required = 15  # 3 rations per crew member
            
            player_supplies = st.session_state.get('supplies', {})
            current_rations = player_supplies.get('Food Rations', 0)
            player_gold = st.session_state.get('gold', 0)
            
            st.info(f"""
            **Reconnaissance Requirements:**
            • Cost: {recon_cost} oz gold
            • Crew: {crew_required} experienced surveyors
            • Rations: {rations_required} (3 per crew member)
            • Risk: Moderate (surveying dangerous terrain)
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Gold Available", f"{player_gold:.1f} oz", 
                         delta="✅ Sufficient" if player_gold >= recon_cost else "❌ Insufficient")
            with col2:
                st.metric("Rations Available", f"{current_rations}", 
                         delta="✅ Sufficient" if current_rations >= rations_required else "❌ Insufficient")
            
            if player_gold >= recon_cost and current_rations >= rations_required:
                if st.button("🔍 Launch Reconnaissance Mission!", type="primary"):
                    launch_reconnaissance(site_data, recon_cost, rations_required)
                    return
            else:
                if player_gold < recon_cost:
                    st.error(f"Need {recon_cost - player_gold:.1f} more gold for reconnaissance.")
                if current_rations < rations_required:
                    st.error(f"Need {rations_required - current_rations} more rations. Visit Town Hub to buy supplies.")
            
            st.markdown("---")
            st.info("💡 **Tip**: Reconnaissance reveals mine reserves and unlocks it for regular mining expeditions.")
            return
        
        # Equipment selection
        st.markdown("### ⚙️ Expedition Equipment")
        equipment_choice = st.radio(
            "Choose your equipment loadout:",
            [
                "Basic Kit (No bonus, standard cost)",
                "Advanced Kit (+20% yield, +15 oz cost)", 
                "Premium Kit (+40% yield, +30 oz cost, -1 risk level)"
            ]
        )
        
        equipment_bonus = 0
        equipment_cost = 0
        risk_reduction = 0
        
        if "Advanced" in equipment_choice:
            equipment_bonus = 0.2
            equipment_cost = 15
        elif "Premium" in equipment_choice:
            equipment_bonus = 0.4
            equipment_cost = 30
            risk_reduction = 1
        
        # Security selection
        st.markdown("### 🛡️ Security Detail")
        security_choice = st.radio(
            "Choose your security level:",
            [
                "Solo (No extra cost, high risk)",
                "Small Guard (15 oz, -1 risk level)",
                "Armed Escort (35 oz, -2 risk levels, bandit insurance)"
            ]
        )
        
        security_cost = 0
        security_reduction = 0
        bandit_insurance = False
        
        if "Small" in security_choice:
            security_cost = 15
            security_reduction = 1
        elif "Armed" in security_choice:
            security_cost = 35
            security_reduction = 2
            bandit_insurance = True
        
        # Calculate total mission cost
        total_cost = site_data['total_cost'] + equipment_cost + security_cost
        effective_risk = max(1, site_data['difficulty'] - risk_reduction - security_reduction)
        
        st.markdown("### 💰 Mission Summary")
        st.info(f"""
        **Total Expedition Cost**: {total_cost} oz gold  
        **Effective Risk Level**: {effective_risk}/5  
        **Potential Yield Bonus**: +{equipment_bonus*100:.0f}%  
        **Bandit Insurance**: {'Yes' if bandit_insurance else 'No'}  
        **Supply Performance**: {'+30%' if total_supply_value > 15 else '+15%' if total_supply_value > 8 else '-30%' if total_supply_value < 3 else '-15%'}
        """)
        
        # Check if player can afford it
        player_gold = st.session_state.get('gold', 0)
        
        if player_gold >= total_cost:
            if st.button("🚀 Launch Expedition!", type="primary"):
                launch_expedition(site_data, equipment_bonus, effective_risk, total_cost, bandit_insurance)
        else:
            st.error(f"Insufficient funds! Need {total_cost} oz gold, have {player_gold:.1f} oz")
            st.info("💰 Complete your current expedition to collect gold, or return to town to sell equipment.")
        
        # Show active expeditions
        show_active_expeditions()

if __name__ == "__main__":
    render_gold_map_folium()
def launch_reconnaissance(site_data, cost, rations_consumed):
    """Launch reconnaissance mission to explore unknown sites."""
    import random
    from datetime import datetime
    
    # Deduct costs
    st.session_state.gold -= cost
    st.session_state.supplies['Food Rations'] -= rations_consumed
    if st.session_state.supplies['Food Rations'] <= 0:
        del st.session_state.supplies['Food Rations']
    
    # Generate random reserves for unexplored site
    difficulty = site_data['difficulty']
    if difficulty >= 4:  # High risk sites
        min_gold, max_gold = 15000, 45000
    elif difficulty >= 3:  # Moderate risk
        min_gold, max_gold = 8000, 25000
    else:  # Lower risk
        min_gold, max_gold = 3000, 15000
    
    discovered_gold = random.randint(min_gold, max_gold)
    
    # Update site data in session state
    if 'discovered_sites' not in st.session_state:
        st.session_state.discovered_sites = {}
    
    st.session_state.discovered_sites[site_data['name']] = {
        'current_gold': discovered_gold,
        'max_gold': discovered_gold,
        'discovered_turn': st.session_state.get('turn', 1)
    }
    
    # Initialize in blockchain
    from .firebase_service import FirebaseService
    firebase_service = FirebaseService()
    firebase_service.initialize_mine_reserves(site_data['name'], discovered_gold)
    
    st.balloons()
    st.success(f"🎆 **Reconnaissance Complete!** {site_data['name']} contains {discovered_gold:,} oz of gold reserves!")
    st.info("✅ Site is now available for regular mining expeditions.")
    st.rerun()
def launch_expedition(site_data, equipment_bonus, risk_level, cost, bandit_insurance):
    """Launch an expedition with global mine tracking."""
    from .global_mine_system import get_global_mine_system
    import random
    from datetime import datetime
    
    global_mines = get_global_mine_system()
    strata_risk = STRATA_LAYERS[st.session_state.current_strata]["risk_modifier"]
    effective_risk = max(1, risk_level + strata_risk)
    
    # Map display names to mine IDs
    name_to_id = {
        "Gold Creek Main Vein": "gold_creek_main",
        "Coloma Bar": "coloma_bar",
        "Yuba Bend": "yuba_bend",
        "Auburn Ravine": "auburn_ravine",
        "Mokelumne Cut": "mokelumne_cut",
        "Jamestown Flats": "jamestown_flats",
        "Placerville Reef": "placerville_reef",
        "Downie Ridge Vein": "downie_ridge_vein",
        "Feather Fork #3": "feather_fork_3",
        "Nevada City Drift": "nevada_city_drift",
        "Angels Reef": "angels_reef",
        "Rough and Ready Mine": "rough_and_ready_mine",
        "French Gulch": "french_gulch",
        "Smartsville Diggings": "smartsville_diggings",
        "Grass Valley Lode": "grass_valley_lode",
        "Empire Mine": "empire_mine",
        "North Star Mine": "north_star_mine",
        "Malakoff Diggins": "malakoff_diggins",
        "Cherokee Mine": "cherokee_mine",
        "Alleghany Mine": "alleghany_mine",
        "Forest City Mine": "forest_city_mine",
        "Washington Mine": "washington_mine",
        "Downieville Drift": "downieville_drift",
        "Sierra Buttes Mine": "sierra_buttes_mine",
        "Tuolumne Quartz": "tuolumne_quartz",
        "Columbia Pocket": "columbia_pocket",
        "Merced Shine": "merced_shine",
        "Calaveras Grove Mine": "calaveras_grove_mine",
        "Moaning Cavern Mine": "moaning_cavern_mine",
        "Dead Man's Gulch": "dead_mans_gulch",
        "Widow's Peak Mine": "widows_peak_mine",
        "El Dorado Mother Lode": "el_dorado_mother_lode",
        # Original global system names
        "Prospector's Gulch": "prospector_gulch",
        "Nugget Hill": "nugget_hill",
        "Silver Stream": "silver_stream",
        "Miner's Hollow": "miners_hollow",
        "Copper Canyon": "copper_canyon",
        "Fortune Falls": "fortune_falls",
        "Treasure Ridge": "treasure_ridge",
        "Golden Gorge": "golden_gorge",
        "Riches Ravine": "riches_ravine",
        "Emerald Excavation": "emerald_excavation",
        "Sapphire Shaft": "sapphire_shaft",
        "Ruby Ridge": "ruby_ridge",
        "Diamond Depths": "diamond_depths",
        "Platinum Pit": "platinum_pit",
        "Crystal Caverns": "crystal_caverns",
        "Mystic Mines": "mystic_mines",
        "Enchanted Excavation": "enchanted_excavation",
        "Arcane Abyss": "arcane_abyss",
        "Ethereal Expanse": "ethereal_expanse",
        "Void Veins": "void_veins",
        "Shadow Shafts": "shadow_shafts",
        "Nightmare Nexus": "nightmare_nexus",
        "Chaos Chambers": "chaos_chambers",
        "Infernal Interior": "infernal_interior",
        "Celestial Core": "celestial_core",
        "Divine Depths": "divine_depths",
        "Heavenly Hollows": "heavenly_hollows",
        "Cosmic Caverns": "cosmic_caverns",
        "Stellar Shafts": "stellar_shafts",
        "Galactic Gorge": "galactic_gorge",
        "Dimensional Depths": "dimensional_depths",
        "Reality Rift": "reality_rift"
    }
    
    mine_id = name_to_id.get(site_data['name'], site_data['name'].lower().replace(' ', '_').replace("'", ""))
    
    # Get mine status from global system
    mine_status = global_mines.get_global_mine_status(mine_id)
    
    if not mine_status:
        st.error(f"⛏️ **{site_data['name']} not found in global system!** Contact admin to initialize mines.")
        return
    
    # Check if mine is depleted
    if mine_status.get('current_reserves', 0) <= 0:
        st.error(f"⛏️ **{site_data['name']} is depleted!** No gold remaining.")
        st.info(f"Total mined: {mine_status.get('total_mined', 0):.1f} oz by all miners")
        return
    
    # Show real-time mine status
    st.info(f"🏔️ **Live Mine Status**: {mine_status.get('current_reserves', 0):.1f} oz remaining | Last activity: {mine_status.get('last_activity', 'Never')}")
    
    # Deduct cost
    st.session_state.gold = st.session_state.get('gold', 0) - cost
    
    # Calculate supplies impact
    player_supplies = st.session_state.get('supplies', {})
    total_supply_value = sum(player_supplies.values())
    
    # Consume supplies
    supplies_consumed = min(total_supply_value, max(3, total_supply_value // 2))
    
    if supplies_consumed > 0:
        for supply_name, quantity in list(player_supplies.items()):
            if supplies_consumed <= 0:
                break
            consumed = min(quantity, supplies_consumed)
            st.session_state.supplies[supply_name] -= consumed
            supplies_consumed -= consumed
            if st.session_state.supplies[supply_name] <= 0:
                del st.session_state.supplies[supply_name]
    
    # Calculate gold found with global mine tracking
    base_gold = random.uniform(5, 25) * (1 + equipment_bonus)
    
    # Apply supply bonus/penalty
    if total_supply_value > 15:
        base_gold *= 1.3
    elif total_supply_value > 8:
        base_gold *= 1.15
    elif total_supply_value < 3:
        base_gold *= 0.7
    else:
        base_gold *= 0.85
    
    # Limit gold to available reserves
    gold_found = min(base_gold, mine_status.get('current_reserves', 0))
    
    if gold_found > 0:
        # Record mining in global system
        miner_email = st.session_state.get('user_email', 'unknown')
        result = global_mines.mine_gold(mine_id, miner_email, gold_found)
        
        if result.get('success'):
            # Add to player's gold
            st.session_state.gold += result['amount_mined']
            
            # Award XP for gold found
            from game_modules.leveling_system import award_xp
            award_xp(int(result['amount_mined']), "gold_mining")
            
            st.success(f"⛏️ **Gold Strike!** Found {result['amount_mined']:.1f} oz at {site_data['name']}")
            st.info(f"🏔️ **Mine Updated**: {result['reserves_remaining']:.1f} oz remaining")
            
            if result.get('mine_depleted'):
                st.warning(f"🚨 **MINE DEPLETED!** {site_data['name']} has been completely mined out!")
        else:
            st.error(f"Mining failed: {result.get('error', 'Unknown error')}")
            return
    else:
        st.warning("No gold found in this expedition.")
    
    # Set initial expedition stats based on supplies consumed
    if total_supply_value > 15:
        initial_supplies = 100
        initial_morale = 85
        supply_bonus = "Excellent"
    elif total_supply_value > 8:
        initial_supplies = 85
        initial_morale = 75
        supply_bonus = "Good"
    elif total_supply_value < 3:
        initial_supplies = 40
        initial_morale = 45
        supply_bonus = "Poor"
    else:
        initial_supplies = 60
        initial_morale = 60
        supply_bonus = "Basic"
    
    # Create expedition
    expedition = {
        'site': site_data['name'],
        'site_data': site_data.to_dict(),
        'equipment_bonus': equipment_bonus,
        'risk_level': risk_level,
        'cost': cost,
        'bandit_insurance': bandit_insurance,
        'phase': 'travel_out',
        'events': [],
        'resources_gathered': result.get('amount_mined', 0) if gold_found > 0 else 0,
        'supplies_remaining': initial_supplies,
        'team_morale': initial_morale,
        'day_started': st.session_state.get('turn', 1),
        'completed': False,
        'supplies_consumed': supplies_consumed,
        'supply_quality': supply_bonus
    }
    
    st.session_state.current_expedition = expedition
    st.success(f"🚀 Expedition to {site_data['name']} launched with {supply_bonus} supplies!")
    if expedition['supplies_consumed'] > 0:
        st.info(f"📦 Consumed {expedition['supplies_consumed']} supply items for the expedition.")
    st.rerun()

def show_active_expeditions():
    """Display and manage active expeditions."""
    if st.session_state.get('current_expedition'):
        expedition = st.session_state.current_expedition
        
        if not expedition['completed']:
            st.markdown("### 🎮 Active Expedition")
            render_expedition_progress(expedition)
        else:
            st.markdown("### ✅ Recently Completed")
            render_expedition_results(expedition)
            
            if st.button("📋 Archive Expedition"):
                # Move to history and clear active
                if 'expedition_history' not in st.session_state:
                    st.session_state.expedition_history = []
                
                st.session_state.expedition_history.append({
                    'site': expedition['site'],
                    'result': f"Gathered {expedition['resources_gathered']:.1f} oz gold",
                    'day': expedition['day_started']
                })
                
                st.session_state.current_expedition = None
                st.rerun()

def render_expedition_progress(expedition):
    """Render the active expedition with game show excitement and choices."""
    site_name = expedition['site']
    phase = expedition['phase']
    
    # Game show introduction
    if 'game_show_intro' not in expedition:
        expedition['game_show_intro'] = True
        st.balloons()
        st.markdown(f"""
        ## 🎪 **WELCOME TO "GOLD RUSH ROULETTE!"** 🎪
        
        *The audience roars as the spotlight hits you!*
        
        **🎙️ Host:** "Ladies and gentlemen, we have a brave prospector ready to risk it all at 
        **{site_name}**! Will they strike it rich or go home empty-handed? Let's find out!"
        
        *Dramatic music swells...*
        """)
    
    # Progress indicator with game show flair
    phases = ['travel_out', 'mining', 'events', 'travel_back']
    current_phase_idx = phases.index(phase) if phase in phases else 0
    progress = (current_phase_idx + 1) / len(phases)
    
    phase_names = ['🗺️ The Journey', '⛏️ The Challenge', '🎲 Wild Card', '🏠 Victory Lap']
    current_phase_name = phase_names[current_phase_idx] if current_phase_idx < len(phase_names) else "Unknown"
    
    st.markdown(f"### 🎭 **ROUND {current_phase_idx + 1}: {current_phase_name}**")
    st.progress(progress, text=f"Game Show Progress: {current_phase_name}")
    
    # Show expedition status with game show styling
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Gold Jackpot", f"{expedition['resources_gathered']:.1f} oz", 
                 delta=f"+{expedition['resources_gathered']:.1f}" if expedition['resources_gathered'] > 0 else None)
    with col2:
        supplies_color = "🟢" if expedition['supplies_remaining'] > 70 else "🟡" if expedition['supplies_remaining'] > 30 else "🔴"
        st.metric(f"{supplies_color} Supplies", f"{expedition['supplies_remaining']}%")
    with col3:
        morale_emoji = "😄" if expedition['team_morale'] > 70 else "😐" if expedition['team_morale'] > 40 else "😰"
        st.metric(f"{morale_emoji} Team Spirit", f"{expedition['team_morale']}%")
    
    # Phase-specific content with game show themes
    if phase == 'travel_out':
        render_travel_phase(expedition)
    elif phase == 'mining':
        render_mining_phase(expedition)
    elif phase == 'events':
        render_events_phase(expedition)
    elif phase == 'travel_back':
        render_finale_phase(expedition)

def render_travel_phase(expedition):
    """Handle the journey with game show drama."""
    site_name = expedition['site']
    
    st.markdown(f"### 🎪 **ROUND 1: THE JOURNEY TO {site_name.upper()}!**")
    st.markdown("*🎙️ Host: 'Our contestant is about to face their first challenge on the road to fortune!'*")
    
    # Generate or get travel event
    if 'travel_event' not in expedition:
        import random
        events = [
            {
                'title': '🌤️ Perfect Weather',
                'description': 'The sun shines bright and the trail is clear! Lady Luck is smiling on you today.',
                'audience_reaction': 'The crowd cheers: "Lucky start! Lucky start!"',
                'choices': [
                    {'text': 'Race ahead with confidence', 'result': 'You arrive pumped up and ready!', 'morale': 15, 'gold': 2},
                    {'text': 'Enjoy the scenery and stay alert', 'result': 'You spot a small gold nugget on the trail!', 'supplies': 10, 'gold': 5}
                ]
            },
            {
                'title': '🐎 Wild Mustang Stampede',
                'description': 'A herd of wild horses thunders across your path! Their hooves kick up glittering dust - could it be gold?',
                'audience_reaction': 'The audience gasps: "Danger AND opportunity!"',
                'choices': [
                    {'text': 'Chase the herd for gold dust', 'result': 'JACKPOT! You collect gold dust worth 10 oz!', 'gold': 10, 'morale': 20, 'supplies': -10},
                    {'text': 'Wait safely for them to pass', 'result': 'Smart move! You avoid injury and stay focused.', 'morale': 5},
                    {'text': 'Try to tame one for faster travel', 'result': 'Success! You now have a trusty steed!', 'supplies': 15, 'morale': 10}
                ]
            },
            {
                'title': '🌪️ Sudden Thunderstorm',
                'description': 'Lightning splits the sky! But wait - the rain is washing gold flakes down the mountainside!',
                'audience_reaction': 'The crowd is on the edge of their seats!',
                'choices': [
                    {'text': 'Dance in the golden rain', 'result': 'You collect 8 oz of gold but catch a cold!', 'gold': 8, 'supplies': -15, 'morale': 15},
                    {'text': 'Take shelter and wait it out', 'result': 'You stay dry and discover a treasure map!', 'morale': 10, 'gold': 3},
                    {'text': 'Use pans to collect the runoff', 'result': 'Brilliant! You gather 12 oz of storm gold!', 'gold': 12, 'supplies': -5}
                ]
            }
        ]
        expedition['travel_event'] = random.choice(events)
    
    event = expedition['travel_event']
    
    st.markdown(f"### 🎭 **{event['title']}**")
    st.markdown(event['description'])
    st.markdown(f"*🎭 {event.get('audience_reaction', 'The crowd holds its breath...')}*")
    
    if 'travel_choice' not in expedition:
        # Show current supply/morale impact
        supplies = expedition['supplies_remaining']
        morale = expedition['team_morale']
        supply_mod = 1.3 if supplies > 80 else 1.15 if supplies > 60 else 0.7 if supplies < 30 else 0.85 if supplies < 50 else 1.0
        morale_mod = 1.25 if morale > 80 else 1.1 if morale > 60 else 0.75 if morale < 40 else 0.9 if morale < 60 else 1.0
        
        choice_options = []
        for i, choice in enumerate(event['choices']):
            base_gold = choice.get('gold', 0)
            final_gold = base_gold * supply_mod * morale_mod
            
            # Create tooltip with calculations
            if base_gold > 0:
                tooltip = f"""💰 REWARD CALCULATION:
• Base reward: {base_gold} oz
• Supply bonus: {(supply_mod-1)*100:+.0f}% ({supplies}% supplies)
• Morale bonus: {(morale_mod-1)*100:+.0f}% ({morale}% morale)
• Final reward: {final_gold:.1f} oz
• Morale change: {choice.get('morale', 0):+}%
• Supply cost: {choice.get('supplies', 0):+}%
• Risk: {'High' if choice.get('supplies', 0) < 0 else 'Low'} (supply depletion = danger)"""
            else:
                tooltip = f"""🛡️ SAFE CHOICE:
• No gold reward
• Morale change: {choice.get('morale', 0):+}%
• Supply change: {choice.get('supplies', 0):+}%
• Risk: Zero (no supply cost or danger)"""
            
            risk_indicator = "🔥 HIGH REWARD" if final_gold > 8 else "⭐ BONUS" if final_gold > 0 else "✅ SAFE"
            choice_text = f"{chr(65+i)}) {choice['text']} {risk_indicator}"
            choice_options.append((choice_text, tooltip))
        
        st.markdown("**Make your choice:**")
        
        # Add tooltip CSS
        st.markdown("""
        <style>
        .travel-tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        .travel-tooltip .tooltiptext {
            visibility: hidden;
            width: 300px;
            background-color: #1a1a1a;
            color: #00ff00;
            text-align: left;
            border-radius: 8px;
            padding: 12px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            margin-left: -150px;
            opacity: 0;
            transition: opacity 0.3s;
            border: 2px solid #DAA520;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            white-space: pre-line;
            box-shadow: 0 0 10px rgba(218, 165, 32, 0.5);
        }
        .travel-tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display choices with tooltips
        for i, (choice_text, tooltip) in enumerate(choice_options):
            st.markdown(f"""
            <div class="travel-tooltip" style="margin: 10px 0; padding: 8px; background: rgba(218,165,32,0.1); border-radius: 6px;">
                <span style="cursor: help; color: #DAA520; font-weight: bold; font-size: 16px;">
                    {choice_text} 💡
                </span>
                <span class="tooltiptext">{tooltip}</span>
            </div>
            """, unsafe_allow_html=True)
        
        selected_index = st.radio(
            "Choose your strategy:", 
            range(len(choice_options)), 
            format_func=lambda x: f"{chr(65+x)}) {event['choices'][x]['text']}",
            key="travel_choice_selection"
        )
        
        if st.button("🎬 LOCK IN YOUR DECISION!", type="primary"):
            selected_choice = event['choices'][selected_index]
            expedition['travel_choice'] = selected_choice
            
            apply_choice_consequences(expedition, selected_choice)
            expedition['phase'] = 'mining'
            
            st.success(f"🎉 **CHOICE LOCKED!** {selected_choice['text']}")
            st.markdown(f"**🎭 Result**: {selected_choice['result']}")
            if selected_choice.get('gold', 0) > 0:
                st.balloons()
            st.rerun()
    else:
        choice = expedition['travel_choice']
        st.success(f"✅ **Decision Made**: {choice['text']}")
        st.markdown(f"**🎭 Result**: {choice['result']}")
        
        if st.button("🎪 ADVANCE TO MINING!", type="primary"):
            expedition['phase'] = 'mining'
            st.rerun()

def render_mining_phase(expedition):
    """Handle location-specific mini-games."""
    site_name = expedition['site']
    
    # Get the game type based on location
    game_type = get_location_game_type(site_name)
    
    st.markdown(f"### 🎮 **{game_type['title']}**")
    st.markdown(f"*{game_type['description']}*")
    
    if 'mining_sessions' not in expedition:
        expedition['mining_sessions'] = 0
        expedition['max_sessions'] = 3
        if 'gems_collected' not in st.session_state:
            st.session_state.gems_collected = {'💎': 0, '💍': 0, '🔮': 0, '⭐': 0, '🌟': 0}
    
    current_session = expedition['mining_sessions']
    max_sessions = expedition['max_sessions']
    
    st.markdown(f"### 🎯 **ROUND {current_session + 1} OF {max_sessions}**")
    
    if current_session < max_sessions:
        # Render the specific game for this location
        if game_type['type'] == 'slot_machine':
            render_slot_machine_game(expedition, game_type)
        elif game_type['type'] == 'memory_match':
            render_memory_match_game(expedition, game_type)
        elif game_type['type'] == 'number_guess':
            render_number_guess_game(expedition, game_type)
        elif game_type['type'] == 'reaction_time':
            render_reaction_time_game(expedition, game_type)
        elif game_type['type'] == 'puzzle_solve':
            render_puzzle_solve_game(expedition, game_type)
        elif game_type['type'] == 'dice_roll':
            render_dice_roll_game(expedition, game_type)
    else:
        total_mined = expedition['resources_gathered']
        st.markdown(f"### 🏆 **{game_type['completion_title']}**")
        st.markdown(f"*Total treasures found: {total_mined:.1f} oz*")
        
        if st.button("🎪 PROCEED TO WILD CARD!", type="primary"):
            expedition['phase'] = 'events'
            st.rerun()

def get_location_game_type(site_name):
    """Return game configuration for each location."""
    games = {
        'Gold Creek Main Vein': {
            'type': 'slot_machine',
            'title': '🎰 FORTUNE SLOT MINE',
            'description': 'The main vein has a magical slot machine powered by gold dust!',
            'completion_title': 'SLOT MACHINE MASTER!',
            'difficulty': 1,
            'max_reward': 50
        },
        'Feather Fork #3': {
            'type': 'memory_match',
            'title': '🧠 RIVER STONE MEMORY MATCH',
            'description': 'Match the glittering river stones to find hidden gold!',
            'completion_title': 'MEMORY CHAMPION!',
            'difficulty': 2,
            'max_reward': 40
        },
        'Grass Valley Lode': {
            'type': 'number_guess',
            'title': '🔢 VEIN DEPTH CALCULATOR',
            'description': 'Calculate the perfect depth to strike the richest vein!',
            'completion_title': 'MASTER CALCULATOR!',
            'difficulty': 4,
            'max_reward': 80
        },
        'Angels Reef': {
            'type': 'reaction_time',
            'title': '⚡ LIGHTNING STRIKE MINING',
            'description': 'Strike the gold veins at the perfect moment!',
            'completion_title': 'LIGHTNING FAST MINER!',
            'difficulty': 3,
            'max_reward': 60
        },
        'Nevada City Drift': {
            'type': 'puzzle_solve',
            'title': '🧩 ANCIENT TUNNEL PUZZLE',
            'description': 'Solve the ancient miner\'s riddle to unlock treasure chambers!',
            'completion_title': 'PUZZLE MASTER!',
            'difficulty': 3,
            'max_reward': 65
        },
        'Downie Ridge Vein': {
            'type': 'dice_roll',
            'title': '🎲 PROSPECTOR\'S LUCK DICE',
            'description': 'Roll the enchanted prospector dice for fortune!',
            'completion_title': 'LUCKY PROSPECTOR!',
            'difficulty': 2,
            'max_reward': 45
        },
        'Dead Man\'s Gulch': {
            'type': 'slot_machine',
            'title': '💀 CURSED FORTUNE WHEEL',
            'description': 'The ghost miner\'s cursed wheel of fortune - high risk, high reward!',
            'completion_title': 'CURSE BREAKER!',
            'difficulty': 5,
            'max_reward': 120
        }
    }
    
    # Default game for unlisted locations
    return games.get(site_name, {
        'type': 'slot_machine',
        'title': '⛏️ STANDARD MINING',
        'description': 'Classic mining with pickaxe and determination!',
        'completion_title': 'MINING COMPLETE!',
        'difficulty': 2,
        'max_reward': 35
    })

def render_slot_machine_game(expedition, game_config):
    """Slot machine mini-game with supply/morale impact."""
    # Show current status impact
    supplies = expedition['supplies_remaining']
    morale = expedition['team_morale']
    
    st.markdown(f"**🎯 Current Performance Modifiers:**")
    col1, col2 = st.columns(2)
    with col1:
        if supplies > 80:
            st.success(f"🟢 Excellent Supplies ({supplies}%) - +30% gold bonus!")
        elif supplies > 60:
            st.info(f"🟡 Good Supplies ({supplies}%) - +15% gold bonus")
        elif supplies < 30:
            st.error(f"🔴 Poor Supplies ({supplies}%) - -30% gold penalty")
        else:
            st.warning(f"🟠 Low Supplies ({supplies}%) - -15% gold penalty")
    
    with col2:
        if morale > 80:
            st.success(f"😄 High Morale ({morale}%) - +25% gold bonus!")
        elif morale > 60:
            st.info(f"😐 Good Morale ({morale}%) - +10% gold bonus")
        elif morale < 40:
            st.error(f"😰 Low Morale ({morale}%) - -25% gold penalty")
        else:
            st.warning(f"😕 Poor Morale ({morale}%) - -10% gold penalty")
    
    if st.button("🎰 SPIN THE REELS!", type="primary", use_container_width=True):
        # Adjust symbols based on difficulty
        if game_config['difficulty'] >= 4:
            symbols = {'💎': 20, '🌟': 5, '💍': 15, '🔮': 10, '⭐': 8, '💰': 25, '🪨': 15, '⚫': 2}
        elif game_config['difficulty'] >= 3:
            symbols = {'💎': 15, '🌟': 3, '💍': 12, '🔮': 8, '⭐': 6, '💰': 30, '🪨': 20, '⚫': 6}
        else:
            symbols = {'💎': 10, '🌟': 1, '💍': 8, '🔮': 5, '⭐': 4, '💰': 35, '🪨': 30, '⚫': 7}
        
        weighted_symbols = []
        for symbol, weight in symbols.items():
            weighted_symbols.extend([symbol] * weight)
        
        # Spinning animation
        slot_placeholder = st.empty()
        for i in range(8):
            spin_result = [random.choice(weighted_symbols) for _ in range(3)]
            slot_placeholder.markdown(f"""
            <div style="text-align: center; font-size: 4rem; background: linear-gradient(45deg, #FFD700, #FFA500); 
                       padding: 20px; border-radius: 15px; margin: 10px 0;">
                {' | '.join(spin_result)}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.15)
        
        # Final result
        final_result = [random.choice(weighted_symbols) for _ in range(3)]
        
        # Calculate base rewards
        base_values = {'💰': 5, '💎': 15, '💍': 25, '🔮': 35, '⭐': 50, '🌟': 100, '🪨': 1, '⚫': 0}
        base_value = sum(base_values.get(symbol, 0) for symbol in final_result)
        
        # Apply supply and morale modifiers
        supply_modifier = 1.3 if supplies > 80 else 1.15 if supplies > 60 else 0.7 if supplies < 30 else 0.85 if supplies < 50 else 1.0
        morale_modifier = 1.25 if morale > 80 else 1.1 if morale > 60 else 0.75 if morale < 40 else 0.9 if morale < 60 else 1.0
        
        total_value = int(base_value * supply_modifier * morale_modifier)
        
        # Difficulty multiplier
        total_value = int(total_value * (1 + game_config['difficulty'] * 0.3))
        
        # Triple match bonus
        if len(set(final_result)) == 1:
            total_value *= 4
            st.balloons()
            st.success(f"🎆 TRIPLE MATCH! 4X MULTIPLIER!")
        
        slot_placeholder.markdown(f"""
        <div style="text-align: center; font-size: 5rem; background: linear-gradient(45deg, #FFD700, #FF6B6B); 
                   padding: 30px; border-radius: 20px; margin: 20px 0; 
                   box-shadow: 0 0 30px rgba(255, 215, 0, 0.8);">
            {' | '.join(final_result)}
        </div>
        """, unsafe_allow_html=True)
        
        # Show modifier impact
        if supply_modifier != 1.0 or morale_modifier != 1.0:
            total_modifier = supply_modifier * morale_modifier
            if total_modifier > 1.1:
                st.success(f"🎉 **TEAM BONUS!** Your team's excellent condition boosted the find by {(total_modifier-1)*100:.0f}%!")
            elif total_modifier < 0.9:
                st.warning(f"⚠️ **TEAM STRUGGLES:** Poor supplies/morale reduced the find by {(1-total_modifier)*100:.0f}%.")
        
        expedition['resources_gathered'] += total_value
        expedition['mining_sessions'] += 1
        st.success(f"⚡ Found {total_value} oz worth of treasures!")
        st.rerun()

def render_memory_match_game(expedition, game_config):
    """Memory matching mini-game."""
    if 'memory_cards' not in expedition:
        symbols = ['💎', '💍', '🔮', '⭐', '🌟', '💰']
        cards = symbols * 2
        random.shuffle(cards)
        expedition['memory_cards'] = cards
        expedition['revealed'] = [False] * 12
        expedition['matches'] = 0
        expedition['attempts'] = 0
        expedition['first_card'] = None
        expedition['show_mismatch'] = False
    
    st.markdown("### 🧠 **MATCH THE GLITTERING STONES!**")
    st.markdown(f"**Matches: {expedition['matches']}/6 | Attempts: {expedition['attempts']}**")
    
    # Handle mismatch display
    if expedition.get('show_mismatch'):
        st.error("❌ No match! Both cards are visible - remember them!")
        if st.button("➡️ Continue", type="primary"):
            expedition['revealed'][expedition['mismatch_cards'][0]] = False
            expedition['revealed'][expedition['mismatch_cards'][1]] = False
            expedition['show_mismatch'] = False
            expedition['first_card'] = None
            del expedition['mismatch_cards']
            st.rerun()
        # Don't return here - show the cards below
    
    cols = st.columns(4)
    for i, card in enumerate(expedition['memory_cards']):
        with cols[i % 4]:
            if expedition['revealed'][i]:
                st.markdown(f"<div style='text-align: center; font-size: 3rem; background: gold; padding: 10px; border-radius: 10px; margin: 2px;'>{card}</div>", unsafe_allow_html=True)
            else:
                if not expedition.get('show_mismatch'):  # Only allow clicks when not showing mismatch
                    if st.button("❓", key=f"card_{i}", use_container_width=True):
                        if expedition['first_card'] is None:
                            expedition['first_card'] = i
                            expedition['revealed'][i] = True
                            st.rerun()
                        elif expedition['first_card'] != i and not expedition['revealed'][i]:
                            expedition['revealed'][i] = True
                            expedition['attempts'] += 1
                            
                            if expedition['memory_cards'][expedition['first_card']] == expedition['memory_cards'][i]:
                                expedition['matches'] += 1
                                expedition['first_card'] = None
                                st.success("✨ MATCH FOUND!")
                                st.rerun()
                            else:
                                # Set up mismatch display
                                expedition['show_mismatch'] = True
                                expedition['mismatch_cards'] = [expedition['first_card'], i]
                                st.rerun()
                else:
                    # Show placeholder during mismatch
                    st.markdown("<div style='text-align: center; font-size: 3rem; background: #ccc; padding: 10px; border-radius: 10px; margin: 2px;'>❓</div>", unsafe_allow_html=True)
    
    if expedition['matches'] == 6:  # All pairs matched
        reward = max(10, 60 - expedition['attempts'] * 3)  # Better score for fewer attempts
        expedition['resources_gathered'] += reward
        expedition['mining_sessions'] += 1
        st.balloons()
        st.success(f"🎉 PERFECT MEMORY! Found {reward} oz of gold!")
        # Clear memory game state
        for key in ['memory_cards', 'revealed', 'matches', 'attempts', 'first_card', 'show_mismatch']:
            if key in expedition:
                del expedition[key]
        st.rerun()

def render_number_guess_game(expedition, game_config):
    """Number guessing mini-game."""
    if 'target_number' not in expedition:
        expedition['target_number'] = random.randint(1, 100)
        expedition['guesses'] = 0
        expedition['max_guesses'] = 7
    
    st.markdown(f"### 🔢 **FIND THE GOLDEN VEIN DEPTH (1-100)!**")
    st.markdown(f"**Attempts remaining: {expedition['max_guesses'] - expedition['guesses']}**")
    
    guess = st.number_input("Enter your guess:", min_value=1, max_value=100, key=f"guess_{expedition['guesses']}")
    
    if st.button("🎯 DRILL HERE!", type="primary"):
        expedition['guesses'] += 1
        
        if guess == expedition['target_number']:
            reward = 80 - (expedition['guesses'] - 1) * 10  # Better reward for fewer guesses
            expedition['resources_gathered'] += reward
            expedition['mining_sessions'] += 1
            st.balloons()
            st.success(f"🎆 PERFECT STRIKE! Found the vein at depth {guess}! Reward: {reward} oz!")
            # Clear game state
            for key in ['target_number', 'guesses', 'max_guesses']:
                if key in expedition:
                    del expedition[key]
            st.rerun()
        elif expedition['guesses'] >= expedition['max_guesses']:
            reward = 10  # Consolation prize
            expedition['resources_gathered'] += reward
            expedition['mining_sessions'] += 1
            st.error(f"💥 Out of attempts! The vein was at depth {expedition['target_number']}. Consolation: {reward} oz")
            # Clear game state
            for key in ['target_number', 'guesses', 'max_guesses']:
                if key in expedition:
                    del expedition[key]
            st.rerun()
        elif guess < expedition['target_number']:
            st.info("📈 DIG DEEPER! The vein is at a greater depth.")
        else:
            st.info("📉 TOO DEEP! The vein is shallower.")

def render_reaction_time_game(expedition, game_config):
    """Reaction time mini-game."""
    import random
    import time
    
    if 'reaction_start' not in expedition:
        expedition['reaction_phase'] = 'waiting'
        expedition['reaction_delay'] = random.uniform(2, 5)
        expedition['reaction_start_time'] = time.time()
    
    if expedition['reaction_phase'] == 'waiting':
        st.markdown("### ⚡ **WAIT FOR THE GOLD FLASH!**")
        st.markdown("🔴 **GET READY... STRIKE WHEN YOU SEE THE GOLD!**")
        
        if time.time() - expedition['reaction_start_time'] > expedition['reaction_delay']:
            expedition['reaction_phase'] = 'strike'
            expedition['strike_time'] = time.time()
            st.rerun()
        
        if st.button("⚡ STRIKE NOW!"):
            st.error("❌ TOO EARLY! You missed the gold vein!")
            expedition['resources_gathered'] += 5  # Small consolation
            expedition['mining_sessions'] += 1
            st.rerun()
    
    elif expedition['reaction_phase'] == 'strike':
        st.markdown("### 🌟 **GOLD FLASH! STRIKE NOW!**")
        
        if st.button("⚡ STRIKE NOW!", type="primary"):
            reaction_time = time.time() - expedition['strike_time']
            if reaction_time < 1.0:
                reward = int(60 - reaction_time * 30)  # Faster = better reward
                st.balloons()
                st.success(f"⚡ LIGHTNING FAST! Reaction time: {reaction_time:.2f}s - Reward: {reward} oz!")
            else:
                reward = 15
                st.info(f"⏰ Good try! Reaction time: {reaction_time:.2f}s - Reward: {reward} oz")
            
            expedition['resources_gathered'] += reward
            expedition['mining_sessions'] += 1
            st.rerun()
        
        # Auto-timeout after 3 seconds
        if time.time() - expedition['strike_time'] > 3:
            st.error("⏰ TOO SLOW! The gold vein disappeared!")
            expedition['resources_gathered'] += 5
            expedition['mining_sessions'] += 1
            st.rerun()

def render_puzzle_solve_game(expedition, game_config):
    """Puzzle solving mini-game."""
    if 'puzzle' not in expedition:
        import random
        puzzles = [
            {"question": "I am yellow, precious, and sought by all. What am I?", "answer": "gold", "reward": 40},
            {"question": "What has a head, a tail, but no body and is worth its weight?", "answer": "coin", "reward": 35},
            {"question": "I sparkle and shine, cut with precision, a girl's best friend. What am I?", "answer": "diamond", "reward": 50},
            {"question": "Deep in the earth I hide, in veins I reside, miners seek me far and wide. What am I?", "answer": "ore", "reward": 30}
        ]
        expedition['puzzle'] = random.choice(puzzles)
        expedition['puzzle_attempts'] = 0
    
    st.markdown("### 🧩 **SOLVE THE ANCIENT RIDDLE!**")
    st.markdown(f"**Riddle:** {expedition['puzzle']['question']}")
    
    answer = st.text_input("Your answer:", key=f"puzzle_{expedition['puzzle_attempts']}")
    
    if st.button("🔍 SUBMIT ANSWER!", type="primary"):
        expedition['puzzle_attempts'] += 1
        
        if answer.lower().strip() == expedition['puzzle']['answer']:
            reward = expedition['puzzle']['reward']
            expedition['resources_gathered'] += reward
            expedition['mining_sessions'] += 1
            st.balloons()
            st.success(f"🧠 BRILLIANT! The ancient chamber opens! Reward: {reward} oz!")
            st.rerun()
        elif expedition['puzzle_attempts'] >= 3:
            reward = 10
            expedition['resources_gathered'] += reward
            expedition['mining_sessions'] += 1
            st.error(f"🤔 The answer was '{expedition['puzzle']['answer']}'. Consolation: {reward} oz")
            st.rerun()
        else:
            st.error(f"❌ Incorrect! {3 - expedition['puzzle_attempts']} attempts remaining.")

def render_dice_roll_game(expedition, game_config):
    """Dice rolling mini-game."""
    st.markdown("### 🎲 **ROLL THE PROSPECTOR'S DICE!**")
    st.markdown("*Roll doubles for bonus! Higher numbers = more gold!*")
    
    if st.button("🎲 ROLL THE DICE!", type="primary", use_container_width=True):
        import random
        import time
        
        # Animated dice roll
        dice_placeholder = st.empty()
        for i in range(6):
            roll1, roll2 = random.randint(1, 6), random.randint(1, 6)
            dice_placeholder.markdown(f"""
            <div style="text-align: center; font-size: 4rem; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
                       padding: 20px; border-radius: 15px; margin: 10px 0;">
                🎲 {roll1} | {roll2} 🎲
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.2)
        
        # Final roll
        final_roll1, final_roll2 = random.randint(1, 6), random.randint(1, 6)
        total = final_roll1 + final_roll2
        
        # Calculate reward
        reward = total * 3
        if final_roll1 == final_roll2:  # Doubles bonus
            reward *= 2
            st.balloons()
            st.success(f"🎆 DOUBLES! {final_roll1}-{final_roll2} = DOUBLE REWARD!")
        
        dice_placeholder.markdown(f"""
        <div style="text-align: center; font-size: 5rem; background: linear-gradient(45deg, #FFD700, #FF6B6B); 
                   padding: 30px; border-radius: 20px; margin: 20px 0; 
                   box-shadow: 0 0 30px rgba(255, 215, 0, 0.8);">
            🎲 {final_roll1} | {final_roll2} 🎲
        </div>
        """, unsafe_allow_html=True)
        
        expedition['resources_gathered'] += reward
        expedition['mining_sessions'] += 1
        st.success(f"🎲 Rolled {total}! Found {reward} oz of gold!")
        st.rerun()

def render_events_phase(expedition):
    """Handle dramatic final events."""
    st.markdown("### 🎲 **ROUND 3: WILD CARD CHALLENGE!**")
    st.markdown("*🎙️ Host: 'Time for our signature Wild Card round! Anything can happen!'*")
    
    if 'final_event' not in expedition:
        import random
        current_gold = expedition['resources_gathered']
        
        # Events scale with how much gold you have
        if current_gold > 50:
            events = [
                {
                    'title': '💰 GOLD BARON CHALLENGE!',
                    'description': f'Word of your {current_gold:.1f} oz haul has spread! A mysterious gold baron offers you a high-stakes wager!',
                    'choices': [
                        {'text': 'Double or nothing coin flip!', 'result': 'INCREDIBLE! You doubled your fortune!', 'gold': current_gold, 'morale': 50},
                        {'text': 'Invest in his secret mine', 'result': 'Smart investment pays off big!', 'gold': 25, 'morale': 20},
                        {'text': 'Politely decline and keep your gold', 'result': 'Wisdom over greed - you keep everything!', 'morale': 10}
                    ]
                }
            ]
        else:
            events = [
                {
                    'title': '🌊 FLASH FLOOD TREASURE HUNT!',
                    'description': 'A flash flood reveals an ancient riverbed full of gold nuggets! But the water is rising fast!',
                    'choices': [
                        {'text': 'Dive in and grab everything you can!', 'result': 'BONANZA! You found a fortune in the flood!', 'gold': 20, 'supplies': -20, 'morale': 25},
                        {'text': 'Form a human chain with your team', 'result': 'Teamwork triumph! Everyone gets rich!', 'gold': 15, 'supplies': -10, 'morale': 30},
                        {'text': 'Wait for the water to recede', 'result': 'Patience pays! You find the best nuggets!', 'gold': 12, 'morale': 15}
                    ]
                },
                {
                    'title': '👻 GHOST MINER\'S BLESSING!',
                    'description': 'The ghost of an old prospector appears! "Help me find my lost treasure, and I\'ll share it with you!"',
                    'choices': [
                        {'text': 'Follow the ghost into the deep tunnels', 'result': 'LEGENDARY! You found the ghost\'s treasure hoard!', 'gold': 30, 'supplies': -15, 'morale': 40},
                        {'text': 'Ask the ghost for mining wisdom', 'result': 'Ancient secrets revealed! Your skills improve!', 'gold': 10, 'morale': 25},
                        {'text': 'Help the ghost find peace', 'result': 'Good karma! The ghost blesses your future!', 'gold': 8, 'morale': 35}
                    ]
                }
            ]
        
        expedition['final_event'] = random.choice(events)
    
    event = expedition['final_event']
    
    st.markdown(f"### 🎪 **{event['title']}**")
    st.markdown(event['description'])
    st.markdown("*🎭 Audience: The crowd is going WILD!*")
    
    # Show current modifiers that will affect rewards
    supplies = expedition['supplies_remaining']
    morale = expedition['team_morale']
    col1, col2 = st.columns(2)
    with col1:
        if supplies > 80:
            st.success(f"🟢 Excellent Supplies ({supplies}%) = +30% gold bonus!")
        elif supplies > 60:
            st.info(f"🟡 Good Supplies ({supplies}%) = +15% gold bonus")
        elif supplies < 30:
            st.error(f"🔴 Poor Supplies ({supplies}%) = -30% gold penalty")
        else:
            st.warning(f"🟠 Low Supplies ({supplies}%) = -15% gold penalty")
    with col2:
        if morale > 80:
            st.success(f"😄 High Morale ({morale}%) = +25% gold bonus!")
        elif morale > 60:
            st.info(f"😐 Good Morale ({morale}%) = +10% gold bonus")
        elif morale < 40:
            st.error(f"😰 Low Morale ({morale}%) = -25% gold penalty")
        else:
            st.warning(f"😕 Poor Morale ({morale}%) = -10% gold penalty")
    
    st.info("💡 **Hover over each choice below** to see exact calculations with your current bonuses/penalties!")
    
    if 'final_choice' not in expedition:
        choice_options = []
        for i, choice in enumerate(event['choices']):
            gold_reward = choice.get('gold', 0)
            current_gold = expedition['resources_gathered']
            
            # Create detailed tooltips showing exact calculations
            supplies = expedition['supplies_remaining']
            morale = expedition['team_morale']
            
            # Calculate supply and morale modifiers
            supply_mod = 1.3 if supplies > 80 else 1.15 if supplies > 60 else 0.7 if supplies < 30 else 0.85 if supplies < 50 else 1.0
            morale_mod = 1.25 if morale > 80 else 1.1 if morale > 60 else 0.75 if morale < 40 else 0.9 if morale < 60 else 1.0
            total_mod = supply_mod * morale_mod
            
            if 'Double or nothing' in choice['text']:
                win_amount = current_gold
                lose_amount = current_gold // 2
                tooltip = f"""🎲 COIN FLIP GAMBLE:
• 50% WIN: +{win_amount:.1f} oz → Total: {current_gold + win_amount:.1f} oz
• 50% LOSE: -{lose_amount:.1f} oz → Keep: {current_gold - lose_amount:.1f} oz
• Morale: +50% if you win
• Expected value: {(win_amount - lose_amount) / 2:.1f} oz
⚠️ HIGH RISK, HIGH REWARD!"""
                drama_level = "🔥 LEGENDARY GAMBLE"
            elif 'Invest in his secret mine' in choice['text']:
                final_gold = gold_reward * total_mod
                tooltip = f"""💰 SAFE INVESTMENT:
• Base reward: {gold_reward} oz
• Supply bonus: {(supply_mod-1)*100:+.0f}% ({supplies}% supplies)
• Morale bonus: {(morale_mod-1)*100:+.0f}% ({morale}% morale)
• Final reward: {final_gold:.1f} oz
• Morale boost: +{choice.get('morale', 0)}%
✅ GUARANTEED RETURN"""
                drama_level = "⭐ SAFE INVESTMENT"
            elif 'Politely decline' in choice['text']:
                tooltip = f"""🛡️ CONSERVATIVE CHOICE:
• Keep all current gold: {current_gold:.1f} oz
• No additional risk
• Small morale boost: +{choice.get('morale', 0)}%
• Total final gold: {current_gold:.1f} oz
✅ ZERO RISK STRATEGY"""
                drama_level = "✅ SAFE CHOICE"
            else:
                # Generic tooltip with modifier calculations
                base_gold = gold_reward
                final_gold = base_gold * total_mod
                
                tooltip = f"""⚡ ADVENTURE CHOICE:
• Base reward: {base_gold} oz
• Supply modifier: {(supply_mod-1)*100:+.0f}% ({supplies}% supplies)
• Morale modifier: {(morale_mod-1)*100:+.0f}% ({morale}% morale)
• Final reward: {final_gold:.1f} oz
• Morale change: {choice.get('morale', 0):+}%
• Supply cost: {choice.get('supplies', 0):+}%"""
                
                if final_gold > 25:
                    drama_level = "🔥 HIGH REWARD"
                elif final_gold > 15:
                    drama_level = "⭐ BONUS"
                elif final_gold > 0:
                    drama_level = "💰 REWARD"
                else:
                    drama_level = "✅ SAFE"
            
            choice_text = f"{chr(65+i)}) {choice['text']} {drama_level}"
            choice_options.append((choice_text, tooltip))
        
        # Add CSS for tooltips
        st.markdown("""
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 350px;
            background-color: #1a1a1a;
            color: #00ff00;
            text-align: left;
            border-radius: 10px;
            padding: 15px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            margin-left: -175px;
            opacity: 0;
            transition: opacity 0.3s;
            border: 2px solid #DAA520;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-line;
            box-shadow: 0 0 15px rgba(218, 165, 32, 0.7);
            line-height: 1.4;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        .tooltip .tooltiptext::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #DAA520 transparent transparent transparent;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display choices with detailed tooltips
        st.markdown("**Make your choice:**")
        
        # Create detailed choice display with hover tooltips
        for i, (choice_text, tooltip) in enumerate(choice_options):
            st.markdown(f"""
            <div class="tooltip" style="margin: 15px 0; padding: 10px; background: rgba(218,165,32,0.1); border-radius: 8px; border-left: 4px solid #DAA520;">
                <span style="cursor: help; color: #DAA520; font-weight: bold; font-size: 18px;">
                    {choice_text} 💡
                </span>
                <span class="tooltiptext">{tooltip}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Single radio for selection with clear labels
        selected_index = st.radio(
            "Choose your strategy:", 
            range(len(choice_options)), 
            format_func=lambda x: f"{chr(65+x)}) {event['choices'][x]['text']}",
            key="final_choice_selection"
        )
        
        if st.button("🎬 MAKE THE FINAL CALL!", type="primary"):
            selected_choice = event['choices'][selected_index]
            expedition['final_choice'] = selected_choice
            
            # Special handling for double-or-nothing
            if 'Double or nothing' in selected_choice['text']:
                import random
                if random.choice([True, False]):
                    # Win!
                    expedition['resources_gathered'] += selected_choice['gold']
                    st.balloons()
                    st.success(f"🎆 **INCREDIBLE WIN!** You doubled your gold!")
                else:
                    # Lose half
                    lost_gold = expedition['resources_gathered'] // 2
                    expedition['resources_gathered'] -= lost_gold
                    selected_choice['result'] = f"Tough luck! You lost {lost_gold:.1f} oz, but you still have the rest!"
                    st.error(f"😭 **OUCH!** The coin flip didn't go your way!")
            else:
                apply_choice_consequences(expedition, selected_choice)
            
            expedition['phase'] = 'travel_back'
            
            st.success(f"🎉 **FINAL CHOICE MADE!** {selected_choice['text']}")
            st.markdown(f"**🎭 Outcome**: {selected_choice['result']}")
            st.rerun()
    else:
        choice = expedition['final_choice']
        st.success(f"✅ **Final Decision**: {choice['text']}")
        st.markdown(f"**🎭 Outcome**: {choice['result']}")
        
        if st.button("🏁 BEGIN VICTORY LAP!", type="primary"):
            expedition['phase'] = 'travel_back'
            st.rerun()

def render_finale_phase(expedition):
    """Handle the triumphant return."""
    st.markdown("### 🏁 **ROUND 4: VICTORY LAP!**")
    
    total_gold = expedition['resources_gathered']
    success_level = "LEGENDARY" if total_gold > 40 else "SPECTACULAR" if total_gold > 25 else "EXCELLENT" if total_gold > 15 else "RESPECTABLE"
    
    st.markdown(f"### 🏆 **{success_level} PERFORMANCE!**")
    st.markdown(f"You return to Gold Creek with {total_gold:.1f} oz of gold!")
    
    if st.button("🏆 CLAIM YOUR PRIZE!", type="primary"):
        expedition['completed'] = True
        final_gold = expedition['resources_gathered']
        st.session_state.gold = st.session_state.get('gold', 0) + final_gold
        st.session_state.turn += 1
        
        # Add to visited sites
        if 'visited_sites' not in st.session_state:
            st.session_state.visited_sites = set()
        st.session_state.visited_sites.add(expedition['site'])
        
        # Auto-save after completing expedition
        try:
            from goldcraft import auto_save_game
            if auto_save_game():
                st.success(f"🎊 **EXPEDITION COMPLETE!** You've won {final_gold:.1f} oz gold! (Auto-saved Turn {st.session_state.turn})")
            else:
                st.success(f"🎊 **EXPEDITION COMPLETE!** You've won {final_gold:.1f} oz gold!")
        except:
            st.success(f"🎊 **EXPEDITION COMPLETE!** You've won {final_gold:.1f} oz gold!")
        
        st.balloons()
        st.rerun()

def render_expedition_results(expedition):
    """Show final expedition results."""
    st.markdown(f"### 📊 Expedition to {expedition['site']} - Complete!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Gold Gathered", f"{expedition['resources_gathered']:.1f} oz")
        st.metric("Total Cost", f"{expedition['cost']} oz")
    
    with col2:
        profit = expedition['resources_gathered'] - expedition['cost']
        st.metric("Net Profit", f"{profit:.1f} oz", delta=f"{profit:.1f}")
        st.metric("Final Morale", f"{expedition['team_morale']}%")

def apply_choice_consequences(expedition, choice):
    """Apply the consequences of player choices with supply/morale impact."""
    if 'gold' in choice:
        base_gold = choice['gold']
        
        # Apply supply bonus/penalty
        supply_modifier = 1.0
        if expedition['supplies_remaining'] > 80:
            supply_modifier = 1.3  # 30% bonus with excellent supplies
        elif expedition['supplies_remaining'] > 60:
            supply_modifier = 1.15  # 15% bonus with good supplies
        elif expedition['supplies_remaining'] < 30:
            supply_modifier = 0.7  # 30% penalty with poor supplies
        elif expedition['supplies_remaining'] < 50:
            supply_modifier = 0.85  # 15% penalty with low supplies
        
        # Apply morale bonus/penalty
        morale_modifier = 1.0
        if expedition['team_morale'] > 80:
            morale_modifier = 1.25  # 25% bonus with high morale
        elif expedition['team_morale'] > 60:
            morale_modifier = 1.1   # 10% bonus with good morale
        elif expedition['team_morale'] < 40:
            morale_modifier = 0.75  # 25% penalty with low morale
        elif expedition['team_morale'] < 60:
            morale_modifier = 0.9   # 10% penalty with poor morale
        
        # Calculate final gold with modifiers
        final_gold = base_gold * supply_modifier * morale_modifier
        expedition['resources_gathered'] += final_gold
        
        # Show impact to player
        if supply_modifier != 1.0 or morale_modifier != 1.0:
            total_modifier = supply_modifier * morale_modifier
            if total_modifier > 1.1:
                st.success(f"🎉 **TEAM SYNERGY BONUS!** Your excellent supplies ({expedition['supplies_remaining']}%) and high team spirit ({expedition['team_morale']}%) boosted your gold find by {(total_modifier-1)*100:.0f}%! ({base_gold:.1f} → {final_gold:.1f} oz)")
            elif total_modifier < 0.9:
                st.warning(f"⚠️ **TEAM STRUGGLES:** Low supplies ({expedition['supplies_remaining']}%) and poor morale ({expedition['team_morale']}%) reduced your gold find by {(1-total_modifier)*100:.0f}%. ({base_gold:.1f} → {final_gold:.1f} oz)")
    
    if 'morale' in choice:
        expedition['team_morale'] = max(0, min(100, expedition['team_morale'] + choice['morale']))
    
    if 'supplies' in choice:
        expedition['supplies_remaining'] = max(0, min(100, expedition['supplies_remaining'] + choice['supplies']))
    
    # Log the event
    if 'events' not in expedition:
        expedition['events'] = []
    
    expedition['events'].append(f"{choice['text']}: {choice['result']}")
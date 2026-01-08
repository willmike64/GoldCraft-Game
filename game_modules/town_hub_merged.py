import streamlit as st
from game_modules.firebase_service import get_firebase_service

# Get Firebase service for logging
firebase_service = get_firebase_service()

# Import save function from main module
def save_current_game(save_name=None):
    """Save the current game state."""
    try:
        email = st.session_state.get('user_email')
        if not email:
            return False
            
        if not save_name:
            import datetime
            save_name = f"autosave_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare game state
        game_state = {
            'current_view': st.session_state.get('current_view', 'menu'),
            'current_strata': st.session_state.get('current_strata', 'Surface'),
            'depth_layer': st.session_state.get('depth_layer', 'Surface'),
            'gold': st.session_state.get('gold', 50),
            'reputation': st.session_state.get('reputation', {}),
            'visited_sites': list(st.session_state.get('visited_sites', set())),
            'turn': st.session_state.get('turn', 1),
            'equipment': st.session_state.get('equipment', {}),
            'supplies': st.session_state.get('supplies', {}),
            'faction_negotiations': st.session_state.get('faction_negotiations', {})
        }
        
        return firebase_service.save_game(email, save_name, game_state)
    except Exception as e:
        st.error(f"Error saving game: {e}")
        return False

EQUIPMENT = {
    "Basic Pickaxe": {"cost": 0, "mining_bonus": 0, "durability": 100, "description": "Standard mining tool", "faction": None, "rep_required": 0},
    "Steel Pickaxe": {"cost": 25, "mining_bonus": 0.15, "durability": 150, "description": "Stronger and more efficient", "faction": None, "rep_required": 0},
    "Diamond-Tipped Pick": {"cost": 75, "mining_bonus": 0.35, "durability": 200, "description": "Premium mining equipment", "faction": None, "rep_required": 0},
    "Hydraulic Drill": {"cost": 150, "mining_bonus": 0.60, "durability": 250, "description": "Industrial-grade extraction", "faction": None, "rep_required": 0},
    
    # Old Miners Guild exclusive equipment
    "Grandfather's Pick": {"cost": 100, "mining_bonus": 0.45, "durability": 300, "description": "Blessed by generations of miners", "faction": "Old Miners Guild", "rep_required": 5},
    "Ancient Sluice Box": {"cost": 80, "capacity_bonus": 0.60, "description": "Time-tested gold separation", "faction": "Old Miners Guild", "rep_required": 3},
    "Master's Apron": {"cost": 40, "safety_bonus": 0.30, "description": "Worn by guild masters for decades", "faction": "Old Miners Guild", "rep_required": 4},
    
    # Industrial Syndicate exclusive equipment
    "Steam-Powered Drill": {"cost": 200, "mining_bonus": 0.80, "durability": 400, "description": "Cutting-edge industrial technology", "faction": "Industrial Syndicate", "rep_required": 6},
    "Mechanical Conveyor": {"cost": 120, "capacity_bonus": 0.75, "description": "Automated ore transport system", "faction": "Industrial Syndicate", "rep_required": 4},
    "Safety Harness System": {"cost": 60, "safety_bonus": 0.35, "description": "Industrial-grade safety equipment", "faction": "Industrial Syndicate", "rep_required": 3},
    
    # Frontier Independents exclusive equipment
    "Prospector's Special": {"cost": 90, "mining_bonus": 0.50, "durability": 180, "description": "Custom-built for the wild frontier", "faction": "Frontier Independents", "rep_required": 4},
    "Bandit's Cache": {"cost": 70, "capacity_bonus": 0.40, "description": "Hidden compartments for dangerous territory", "faction": "Frontier Independents", "rep_required": 3},
    "Gunslinger's Vest": {"cost": 50, "safety_bonus": 0.20, "description": "Protection from more than just cave-ins", "faction": "Frontier Independents", "rep_required": 2},
    "Sourdough Bread": {"cost": 10, "effect": "morale", "value": 5, "description": "Hearty bread for long journeys", "faction": "Frontier Independents", "rep_required": 1},
    
    # Standard equipment
    "Canvas Satchel": {"cost": 0, "capacity_bonus": 0, "description": "Basic gold storage", "faction": None, "rep_required": 0},
    "Leather Pouch": {"cost": 15, "capacity_bonus": 0.20, "description": "Holds 20% more gold", "faction": None, "rep_required": 0},
    "Reinforced Chest": {"cost": 50, "capacity_bonus": 0.50, "description": "Secure storage for large hauls", "faction": None, "rep_required": 0},
    
    "Work Clothes": {"cost": 0, "safety_bonus": 0, "description": "Basic protection", "faction": None, "rep_required": 0},
    "Leather Gear": {"cost": 20, "safety_bonus": 0.10, "description": "Reduces injury risk by 10%", "faction": None, "rep_required": 0},
    "Mining Suit": {"cost": 60, "safety_bonus": 0.25, "description": "Professional protection gear", "faction": None, "rep_required": 0},
}

SUPPLIES = {
    "Food Rations": {"cost": 5, "effect": "morale", "value": 10, "description": "Keeps team fed and happy"},
    "Medical Kit": {"cost": 15, "effect": "safety", "value": 15, "description": "Emergency medical supplies"},
    "Dynamite": {"cost": 25, "effect": "mining", "value": 0.20, "description": "Explosive mining boost"},
    "Lanterns": {"cost": 8, "effect": "efficiency", "value": 0.10, "description": "Better visibility underground"},
    "Rope & Pulleys": {"cost": 12, "effect": "capacity", "value": 0.15, "description": "Extract more ore per trip"},
    "Guard Hire": {"cost": 30, "effect": "security", "value": 20, "description": "Armed protection for expeditions"},
}

FACTION_SUPPLIES = {
    "Old Miners Guild": {
        "Traditional Rations": {"cost": 4, "effect": "morale", "value": 15, "description": "Hearty meals that boost team spirit", "rep_required": 2},
        "Herbal Medicine": {"cost": 12, "effect": "safety", "value": 20, "description": "Natural remedies from guild knowledge", "rep_required": 3},
        "Blessed Candles": {"cost": 6, "effect": "efficiency", "value": 0.15, "description": "Guild-blessed lighting for good fortune", "rep_required": 1},
    },
    "Industrial Syndicate": {
        "Military Rations": {"cost": 6, "effect": "morale", "value": 12, "description": "Efficient nutrition for maximum productivity", "rep_required": 1},
        "Advanced Medical Kit": {"cost": 20, "effect": "safety", "value": 25, "description": "State-of-the-art medical supplies", "rep_required": 4},
        "Industrial Explosives": {"cost": 35, "effect": "mining", "value": 0.30, "description": "High-grade mining explosives", "rep_required": 5},
        "Electric Lamps": {"cost": 15, "effect": "efficiency", "value": 0.20, "description": "Bright electric illumination", "rep_required": 2},
    },
    "Frontier Independents": {
        "Trail Mix": {"cost": 3, "effect": "morale", "value": 8, "description": "Cheap but effective frontier food", "rep_required": 0},
        "Moonshine Medicine": {"cost": 8, "effect": "safety", "value": 12, "description": "Questionable but effective frontier remedy", "rep_required": 1},
        "Black Powder": {"cost": 18, "effect": "mining", "value": 0.25, "description": "Volatile but powerful explosive", "rep_required": 3},
        "Mercenary Guards": {"cost": 25, "effect": "security", "value": 25, "description": "Experienced frontier fighters", "rep_required": 4},
    }
}

FACTIONS = {
    "Old Miners Guild": {
        "description": "Tradition-bound, slow-moving, but deeply influential.",
    },
    "Industrial Syndicate": {
        "description": "Capital-rich, efficient, and ruthless.",
    },
    "Frontier Independents": {
        "description": "High risk, high reward, little protection.",
    },
}


def _inject_town_hub_styles():
    """Inject lightweight CSS to match the Town Hub 'new' look."""
    st.markdown(
        """
        <style>
            .content-box{
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 18px;
                padding: 22px 22px 10px 22px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.18);
                margin-bottom: 14px;
            }
            .town-subtitle{
                margin-top:-8px;
                opacity:0.85;
                font-style: italic;
            }
            .town-card{
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 16px;
                padding: 14px 14px 10px 14px;
                background: rgba(255,255,255,0.03);
                margin-bottom: 10px;
            }
            .town-card h3{
                margin: 0 0 6px 0;
            }
            .town-card p{
                margin: 0 0 10px 0;
                opacity: 0.9;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_town_hub():
    _inject_town_hub_styles()

    # Initialize session state with proper defaults
    if "reputation" not in st.session_state:
        st.session_state.reputation = {}
    if "equipment" not in st.session_state:
        st.session_state.equipment = {"Basic Pickaxe": True, "Canvas Satchel": True, "Work Clothes": True}
    if "supplies" not in st.session_state:
        st.session_state.supplies = {}
    if "faction_negotiations" not in st.session_state:
        st.session_state.faction_negotiations = {}
    if "turn" not in st.session_state:
        st.session_state.turn = 1

    # Outer container for the "new" look
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# 🏘️ **GOLD CREEK TOWN**")
    st.markdown('<div class="town-subtitle">The bustling heart of the mining frontier</div>', unsafe_allow_html=True)

    # Quick-access row (visual cards) — buttons jump the user to sections below
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="town-card"><h3>🏪 General Store</h3><p>Gear up with tools, supplies, and essentials.</p></div>', unsafe_allow_html=True)
        if st.button("🛒 Enter Store", use_container_width=True):
            st.session_state["town_hub_nav"] = "📦 Supplies"

    with col2:
        st.markdown('<div class="town-card"><h3>🍺 Saloon</h3><p>Rumors, deals, and the occasional tall tale.</p></div>', unsafe_allow_html=True)
        if st.button("🍻 Enter Saloon", use_container_width=True):
            st.session_state["town_hub_nav"] = "🤝 Factions"

    with col3:
        st.markdown('<div class="town-card"><h3>🏦 Bank</h3><p>Secure reserves, track inventory value, plan ahead.</p></div>', unsafe_allow_html=True)
        if st.button("💰 Enter Bank", use_container_width=True):
            st.session_state["town_hub_nav"] = "🏦 Bank"

    # Auto-save when making purchases (keeps existing behavior)
    if st.session_state.get('user_email'):
        save_current_game()

    st.divider()

    # Section navigation (lets the quick buttons above actually switch views)
    nav = st.radio(
        label="",
        options=["🤝 Factions", "🔧 Equipment", "📦 Supplies", "🏦 Bank", "📊 Inventory"],
        horizontal=True,
        key="town_hub_nav",
    )

    if nav == "🤝 Factions":
        render_factions()
    elif nav == "🔧 Equipment":
        render_equipment_shop()
    elif nav == "📦 Supplies":
        render_supplies_shop()
    elif nav == "🏦 Bank":
        from .bank import render_bank
        render_bank()
    else:
        render_inventory()

    st.divider()

    # Town news (from town_hub_new.py vibe)
    st.markdown("### 📰 Town News")
    st.info("🗞️ Latest: New mining claims discovered in the Sierra foothills!")

    if st.button("⬅️ Return to Map"):
        st.session_state.current_view = "map"

    st.markdown('</div>', unsafe_allow_html=True)

def render_factions(
):
    """Render faction interaction interface."""
    st.markdown("### 🤝 Faction Relations")
    
    faction = st.selectbox(
        "Choose a faction to engage",
        list(FACTIONS.keys())
    )

    st.markdown(f"**{faction}**")
    st.markdown(FACTIONS[faction]["description"])

    rep = st.session_state.reputation.get(faction, 0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Reputation", rep)
    with col2:
        # Show reputation tier
        if rep >= 6:
            tier = "🏆 Elite Partner"
        elif rep >= 4:
            tier = "⭐ Trusted Ally"
        elif rep >= 2:
            tier = "🤝 Known Associate"
        else:
            tier = "👤 Stranger"
        st.metric("Status", tier)

    col_a, col_b = st.columns(2)

    with col_a:
        # Check if player has negotiated recently
        last_negotiation = st.session_state.faction_negotiations.get(faction, 0)
        current_turn = st.session_state.get('turn', 1)
        can_negotiate = current_turn > last_negotiation
        
        negotiate_cost = 5
        if can_negotiate:
            if st.button(f"📜 Negotiate Access ({negotiate_cost} oz)"):
                if st.session_state.gold >= negotiate_cost:
                    st.session_state.gold -= negotiate_cost
                    st.session_state.reputation[faction] = rep + 1
                    st.session_state.faction_negotiations[faction] = current_turn
                    
                    # Log faction negotiation for big data
                    if st.session_state.get('user_email'):
                        firebase_service.log_game_action(st.session_state.user_email, 'faction_negotiation', {
                            'faction': faction,
                            'cost': negotiate_cost,
                            'new_reputation': rep + 1,
                            'turn': current_turn,
                            'remaining_gold': st.session_state.gold
                        })
                    
                    st.success("Negotiation improved relations.")
                    st.rerun()
                else:
                    st.error("Insufficient gold!")
        else:
            st.info(f"Already negotiated this turn")

    with col_b:
        if st.button("💰 Offer Capital (10 oz)"):
            if st.session_state.gold >= 10:
                st.session_state.gold -= 10
                st.session_state.reputation[faction] = rep + 2
                st.success("Capital greased the wheels.")
                st.rerun()
            else:
                st.error("Insufficient gold!")
    
    # Show faction-exclusive equipment preview
    st.markdown(f"### 🎁 {faction} Exclusive Equipment")
    faction_equipment = {k: v for k, v in EQUIPMENT.items() if v.get('faction') == faction}
    
    if faction_equipment:
        for name, stats in faction_equipment.items():
            rep_needed = stats['rep_required']
            can_access = rep >= rep_needed
            
            if can_access:
                st.success(f"✅ **{name}** - {stats['cost']} oz (Available)")
            else:
                st.info(f"🔒 **{name}** - Requires {rep_needed} reputation")
            st.caption(stats['description'])
    else:
        st.info("No exclusive equipment available from this faction.")

def render_equipment_shop():
    """Render equipment upgrade interface with faction restrictions."""
    st.markdown("### 🔧 Equipment Upgrades")
    st.caption(f"💰 Available Gold: {st.session_state.gold:.1f} oz")
    
    # Faction filter
    faction_filter = st.selectbox(
        "Shop by Faction",
        ["All Equipment", "General Store"] + list(FACTIONS.keys())
    )
    
    # Filter equipment based on selection
    if faction_filter == "All Equipment":
        filtered_equipment = EQUIPMENT
    elif faction_filter == "General Store":
        filtered_equipment = {k: v for k, v in EQUIPMENT.items() if v.get('faction') is None}
    else:
        filtered_equipment = {k: v for k, v in EQUIPMENT.items() if v.get('faction') == faction_filter or v.get('faction') is None}
    
    # Group equipment by type
    tools = {k: v for k, v in filtered_equipment.items() if "Pick" in k or "Drill" in k or "Special" in k}
    storage = {k: v for k, v in filtered_equipment.items() if "Satchel" in k or "Pouch" in k or "Chest" in k or "Box" in k or "Cache" in k or "Conveyor" in k}
    protection = {k: v for k, v in filtered_equipment.items() if "Clothes" in k or "Gear" in k or "Suit" in k or "Apron" in k or "Vest" in k or "Harness" in k}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### ⛏️ Mining Tools")
        render_equipment_category(tools)
    
    with col2:
        st.markdown("#### 🎒 Storage")
        render_equipment_category(storage)
    
    with col3:
        st.markdown("#### 🛡️ Protection")
        render_equipment_category(protection)

def render_equipment_category(equipment_dict):
    """Render a category of equipment with faction restrictions."""
    for name, stats in equipment_dict.items():
        owned = st.session_state.equipment.get(name, False)
        faction = stats.get('faction')
        rep_required = stats.get('rep_required', 0)
        
        # Check if player can access this equipment
        can_access = True
        if faction:
            player_rep = st.session_state.reputation.get(faction, 0)
            can_access = player_rep >= rep_required
        
        with st.container():
            if owned:
                st.success(f"✅ **{name}** (Owned)")
            elif not can_access:
                st.error(f"🔒 **{name}** - Requires {rep_required} rep with {faction}")
            else:
                faction_tag = f" [{faction}]" if faction else ""
                st.markdown(f"**{name}**{faction_tag} - {stats['cost']} oz")
            
            st.caption(stats['description'])
            
            # Show bonuses
            if 'mining_bonus' in stats and stats['mining_bonus'] > 0:
                st.caption(f"⛏️ +{stats['mining_bonus']*100:.0f}% mining yield")
            if 'capacity_bonus' in stats and stats['capacity_bonus'] > 0:
                st.caption(f"🎒 +{stats['capacity_bonus']*100:.0f}% carrying capacity")
            if 'safety_bonus' in stats and stats['safety_bonus'] > 0:
                st.caption(f"🛡️ +{stats['safety_bonus']*100:.0f}% safety")
            
            if not owned and stats['cost'] > 0 and can_access:
                if st.button(f"Buy {name}", key=f"buy_{name}"):
                    if st.session_state.gold >= stats['cost']:
                        st.session_state.gold -= stats['cost']
                        st.session_state.equipment[name] = True
                        
                        # Log equipment purchase for big data
                        if st.session_state.get('user_email'):
                            firebase_service.log_game_action(st.session_state.user_email, 'equipment_purchased', {
                                'item_name': name,
                                'cost': stats['cost'],
                                'faction': faction,
                                'mining_bonus': stats.get('mining_bonus', 0),
                                'capacity_bonus': stats.get('capacity_bonus', 0),
                                'safety_bonus': stats.get('safety_bonus', 0),
                                'remaining_gold': st.session_state.gold,
                                'turn': st.session_state.get('turn', 1)
                            })
                        
                        st.success(f"Purchased {name}!")
                        st.rerun()
                    else:
                        st.error("Insufficient gold!")
            
            st.divider()

def render_supplies_shop():
    """Render supplies purchasing interface with faction-specific options."""
    st.markdown("### 📦 Expedition Supplies")
    st.caption(f"💰 Available Gold: {st.session_state.gold:.1f} oz")
    
    # Faction selection for supplies
    faction_choice = st.selectbox(
        "Supply Source",
        ["General Store"] + list(FACTIONS.keys())
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🛒 Available Supplies")
        
        if faction_choice == "General Store":
            # Show standard supplies
            for name, stats in SUPPLIES.items():
                render_supply_item(name, stats)
        else:
            # Show faction-specific supplies
            faction_supplies = FACTION_SUPPLIES.get(faction_choice, {})
            player_rep = st.session_state.reputation.get(faction_choice, 0)
            
            for name, stats in faction_supplies.items():
                can_access = player_rep >= stats.get('rep_required', 0)
                render_supply_item(name, stats, faction_choice, can_access)
    
    with col2:
        render_supply_recommendations()

def render_supply_item(name, stats, faction=None, can_access=True):
    """Render individual supply item."""
    with st.container():
        if not can_access:
            rep_needed = stats.get('rep_required', 0)
            st.error(f"🔒 **{name}** - Requires {rep_needed} rep with {faction}")
        else:
            faction_tag = f" [{faction}]" if faction else ""
            st.markdown(f"**{name}**{faction_tag} - {stats['cost']} oz")
        
        st.caption(stats['description'])
        
        # Show effect
        effect_icons = {
            'morale': '😊',
            'safety': '🛡️', 
            'mining': '⛏️',
            'efficiency': '⚡',
            'capacity': '🎒',
            'security': '🔒'
        }
        icon = effect_icons.get(stats['effect'], '📈')
        if stats['effect'] in ['morale', 'safety', 'security']:
            st.caption(f"{icon} +{stats['value']} {stats['effect']}")
        else:
            st.caption(f"{icon} +{stats['value']*100:.0f}% {stats['effect']}")
        
        if can_access:
            quantity = st.number_input(f"Quantity", min_value=0, max_value=10, value=0, key=f"qty_{name}")
            
            if quantity > 0:
                total_cost = stats['cost'] * quantity
                if st.button(f"Buy {quantity}x {name} ({total_cost} oz)", key=f"buy_supply_{name}"):
                    if st.session_state.gold >= total_cost:
                        st.session_state.gold -= total_cost
                        current = st.session_state.supplies.get(name, 0)
                        st.session_state.supplies[name] = current + quantity
                        st.success(f"Purchased {quantity}x {name}!")
                        st.rerun()
                    else:
                        st.error("Insufficient gold!")
        
        st.divider()

def render_supply_recommendations():
    """Render supply recommendations."""
    st.markdown("#### 📋 Supply Recommendations")
    
    # Recommend supplies based on player's situation
    gold = st.session_state.gold
    
    if gold < 50:
        st.info("💡 **Budget Build**: Food Rations + Lanterns for basic expeditions")
    elif gold < 100:
        st.info("💡 **Balanced Build**: Medical Kit + Rope & Pulleys for safer, more profitable runs")
    else:
        st.info("💡 **Premium Build**: Guard Hire + Dynamite for high-risk, high-reward expeditions")
    
    st.markdown("#### 🎯 Faction Benefits")
    st.markdown("""
    **Old Miners Guild**: Traditional, reliable equipment with durability bonuses
    
    **Industrial Syndicate**: High-tech gear with maximum efficiency
    
    **Frontier Independents**: Versatile equipment for dangerous territories
    """)

def render_inventory():
    """Render current inventory and stats."""
    st.markdown("### 📊 Current Inventory")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 Owned Equipment")
        
        total_mining_bonus = 0
        total_capacity_bonus = 0
        total_safety_bonus = 0
        
        for name, owned in st.session_state.equipment.items():
            if owned:
                stats = EQUIPMENT[name]
                faction_tag = f" [{stats.get('faction')}]" if stats.get('faction') else ""
                st.success(f"✅ {name}{faction_tag}")
                
                # Accumulate bonuses
                total_mining_bonus += stats.get('mining_bonus', 0)
                total_capacity_bonus += stats.get('capacity_bonus', 0)
                total_safety_bonus += stats.get('safety_bonus', 0)
        
        st.markdown("#### 📈 Total Equipment Bonuses")
        if total_mining_bonus > 0:
            st.metric("Mining Yield Bonus", f"+{total_mining_bonus*100:.0f}%")
        if total_capacity_bonus > 0:
            st.metric("Capacity Bonus", f"+{total_capacity_bonus*100:.0f}%")
        if total_safety_bonus > 0:
            st.metric("Safety Bonus", f"+{total_safety_bonus*100:.0f}%")
    
    with col2:
        st.markdown("#### 📦 Supply Stockpile")
        
        if st.session_state.supplies:
            for name, quantity in st.session_state.supplies.items():
                if quantity > 0:
                    st.info(f"📦 {name}: {quantity}")
        else:
            st.caption("No supplies in stock")
        
        # Calculate total supply value
        total_value = 0
        for name, qty in st.session_state.supplies.items():
            if name in SUPPLIES:
                total_value += SUPPLIES[name]['cost'] * qty
            else:
                # Check faction supplies
                for faction_supplies in FACTION_SUPPLIES.values():
                    if name in faction_supplies:
                        total_value += faction_supplies[name]['cost'] * qty
                        break
        
        if total_value > 0:
            st.metric("Total Supply Value", f"{total_value} oz")
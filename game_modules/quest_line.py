QUEST_LINE = [
    {
        "id": "first_pick",
        "level_required": 1,
        "title": "First Pick, First Promise",
        "description": "Choose your character and vow to strike true in Gold Creek.",
        "xp_reward": 15,
    },
    {
        "id": "supply_check",
        "level_required": 2,
        "title": "Supplies on the Belt",
        "description": "Confirm your starter equipment and ready your satchel.",
        "xp_reward": 20,
    },
    {
        "id": "campfire_tale",
        "level_required": 3,
        "title": "Campfire Tale",
        "description": "Hear the rumor of a rich vein and prepare your first outing.",
        "xp_reward": 25,
    },
    {
        "id": "town_introduction",
        "level_required": 4,
        "title": "A Face in Town",
        "description": "Introduce yourself in Gold Creek and earn your place.",
        "xp_reward": 30,
    },
    {
        "id": "first_payday",
        "level_required": 5,
        "title": "First Payday",
        "description": "Earn your first real haul and prove your grit.",
        "xp_reward": 35,
    },
    {
        "id": "faction_pledge",
        "level_required": 6,
        "title": "Faction Pledge",
        "description": "Stand with your faction and learn their traditions.",
        "xp_reward": 40,
    },
    {
        "id": "map_marks",
        "level_required": 7,
        "title": "Marks on the Map",
        "description": "Plot your first expedition route.",
        "xp_reward": 45,
    },
    {
        "id": "second_shift",
        "level_required": 8,
        "title": "Second Shift",
        "description": "Work an extra shift to prove your endurance.",
        "xp_reward": 50,
    },
    {
        "id": "gear_tuneup",
        "level_required": 9,
        "title": "Gear Tune-Up",
        "description": "Sharpen tools and keep your kit in top shape.",
        "xp_reward": 55,
    },
    {
        "id": "safe_harbor",
        "level_required": 10,
        "title": "Safe Harbor",
        "description": "Secure a reliable routine before venturing deeper.",
        "xp_reward": 60,
    },
    {
        "id": "trade_connections",
        "level_required": 11,
        "title": "Trade Connections",
        "description": "Meet traders who can outfit your next run.",
        "xp_reward": 65,
    },
    {
        "id": "trail_watch",
        "level_required": 12,
        "title": "Trail Watch",
        "description": "Keep an eye out for danger on the mining trails.",
        "xp_reward": 70,
    },
    {
        "id": "bonus_find",
        "level_required": 13,
        "title": "Bonus Find",
        "description": "Spot a hidden nugget and bank the reward.",
        "xp_reward": 75,
    },
    {
        "id": "crew_respect",
        "level_required": 14,
        "title": "Crew Respect",
        "description": "Earn the trust of veteran prospectors.",
        "xp_reward": 80,
    },
    {
        "id": "deepening_roads",
        "level_required": 15,
        "title": "Deepening Roads",
        "description": "Prepare to reach the deeper strata.",
        "xp_reward": 85,
    },
    {
        "id": "risk_and_reward",
        "level_required": 16,
        "title": "Risk & Reward",
        "description": "Balance safety and profit as the stakes rise.",
        "xp_reward": 90,
    },
    {
        "id": "toolmaster",
        "level_required": 17,
        "title": "Toolmaster",
        "description": "Master the tools that define your craft.",
        "xp_reward": 95,
    },
    {
        "id": "steady_hands",
        "level_required": 18,
        "title": "Steady Hands",
        "description": "Keep calm under pressure and steady the crew.",
        "xp_reward": 100,
    },
    {
        "id": "prospector_legacy",
        "level_required": 19,
        "title": "Prospector Legacy",
        "description": "Leave a mark on Gold Creek's ledger.",
        "xp_reward": 105,
    },
    {
        "id": "twentieth_level_oath",
        "level_required": 20,
        "title": "Twentieth-Level Oath",
        "description": "Swear to seek legendary veins beyond the known map.",
        "xp_reward": 120,
    },
]


def get_quest_line():
    return QUEST_LINE


def get_next_quest(completed_ids):
    for quest in QUEST_LINE:
        if quest["id"] not in completed_ids:
            return quest
    return None


def get_quest_by_id(quest_id):
    for quest in QUEST_LINE:
        if quest["id"] == quest_id:
            return quest
    return None

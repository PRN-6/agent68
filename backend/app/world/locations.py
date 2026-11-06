from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class Location(BaseModel):
    id: str
    name: str
    zone: str  # guild, tavern, civic, workshop, arcane, training, forest, dungeon, residential
    x: float
    y: float
    width: float = 12.0
    height: float = 10.0
    walk_x: float = 20.0
    walk_y: float = 20.0
    capacity: int = 20
    description: str
    objects: List[str] = Field(default_factory=list)
    color: str = "#4A5568"
    icon: str = "building"

# Fantasy MMORPG World Locations (Sunhaven Town + Whispering Forest + The Shadow Crypts)
TOWN_LOCATIONS: Dict[str, Location] = {
    # 1. Guild & Adventurer Hub
    "guild_hall": Location(
        id="guild_hall", name="Sunhaven Adventurer's Guild", zone="guild",
        x=34.0, y=10.0, width=20.0, height=16.0, walk_x=44.0, walk_y=20.0, capacity=35,
        description="The grand hall of the Adventurer's Guild with quest bounty boards, guildmaster desk, banquet tables, and weapon racks.",
        objects=["quest_board", "guildmaster_desk", "banquet_tables", "weapon_racks", "guild_banner"],
        color="#3B82F6", icon="shield"
    ),
    "tavern": Location(
        id="tavern", name="The Dragon's Flagon Tavern & Inn", zone="tavern",
        x=10.0, y=10.0, width=20.0, height=18.0, walk_x=20.0, walk_y=22.0, capacity=35,
        description="Lively tavern with oak bar counter, ale kegs, warm stone fireplace, dining tables, and upstairs inn lodgings.",
        objects=["bar_counter", "ale_kegs", "hearth_fireplace", "dining_tables", "tankards", "inn_beds"],
        color="#F59E0B", icon="beer"
    ),

    # 2. Commerce & Crafting
    "town_square": Location(
        id="town_square", name="Sunhaven Fountain Plaza", zone="civic",
        x=32.0, y=36.0, width=22.0, height=20.0, walk_x=41.0, walk_y=40.0, capacity=40,
        description="Grand cobblestone courtyard with a central stone fountain, merchant stalls selling potions, armor, and rare relics.",
        objects=["stone_fountain", "produce_stall", "armory_stall", "potion_stall", "relic_stall", "lantern_posts"],
        color="#10B981", icon="sparkles"
    ),
    "blacksmith": Location(
        id="blacksmith", name="Ironforge Blacksmith & Armory", zone="workshop",
        x=10.0, y=38.0, width=16.0, height=16.0, walk_x=18.0, walk_y=48.0, capacity=20,
        description="Stone forge with blazing smelting furnace, anvil, weapon displays, and repair tools for adventuring gear.",
        objects=["forge_furnace", "anvil", "weapon_racks", "armor_stands", "hammer_tools"],
        color="#EF4444", icon="hammer"
    ),
    "apothecary": Location(
        id="apothecary", name="Arcane Sanctum & Potion Lab", zone="arcane",
        x=58.0, y=38.0, width=16.0, height=16.0, walk_x=66.0, walk_y=48.0, capacity=20,
        description="Mystical sanctum with a glowing runic circle, bubbling cauldron, potion shelves, and ancient spell grimoires.",
        objects=["runic_circle", "alchemy_cauldron", "potion_shelves", "crystal_orb", "spell_tomes"],
        color="#8B5CF6", icon="wand"
    ),

    # 3. Training & Wilds
    "training_grounds": Location(
        id="training_grounds", name="Hero's Training Arena", zone="training",
        x=10.0, y=64.0, width=18.0, height=20.0, walk_x=19.0, walk_y=74.0, capacity=25,
        description="Fenced sand and dirt combat arena equipped with sparring practice dummies, archery bullseye targets, and weapon racks.",
        objects=["training_dummies", "archery_targets", "wooden_fencing", "weapon_racks"],
        color="#D97706", icon="swords"
    ),
    "stone_bridge": Location(
        id="stone_bridge", name="The Grand Stone Bridge", zone="civic",
        x=78.0, y=47.0, width=10.0, height=6.0, walk_x=83.0, walk_y=50.0, capacity=20,
        description="Sturdy fortified stone bridge spanning across the Great River, connecting Sunhaven to the dangerous wilderness.",
        objects=["stone_parapet", "bridge_lanterns", "cobblestone_road"],
        color="#64748B", icon="bridge"
    ),
    "whispering_woods": Location(
        id="whispering_woods", name="The Whispering Forest & Shrine", zone="forest",
        x=96.0, y=46.0, width=12.0, height=12.0, walk_x=100.0, walk_y=50.0, capacity=25,
        description="Deep mystical woods featuring a glowing stone campfire ring and ancient druidic standing runic monoliths.",
        objects=["stone_campfire", "runic_monoliths", "log_seats", "pine_trees"],
        color="#059669", icon="trees"
    ),

    # 4. The Shadow Crypts / Dungeon
    "dungeon_entrance": Location(
        id="dungeon_entrance", name="The Shadow Crypts - Skull Gate", zone="dungeon",
        x=112.0, y=46.0, width=8.0, height=8.0, walk_x=115.0, walk_y=50.0, capacity=25,
        description="The ominous subterranean entrance carved into obsidian rock, flanked by burning purple brazier torches.",
        objects=["skull_archway", "purple_braziers", "obsidian_gates"],
        color="#7C3AED", icon="skull"
    ),
    "dungeon_crypt": Location(
        id="dungeon_crypt", name="Crypt of the Undead (Floor 1)", zone="dungeon",
        x=120.0, y=12.0, width=16.0, height=20.0, walk_x=128.0, walk_y=23.0, capacity=20,
        description="Dark flagstone crypt lined with stone sarcophagi, cobwebs, and wandering undead skeletons.",
        objects=["stone_sarcophagi", "bone_piles", "soul_torches", "cobwebs"],
        color="#6D28D9", icon="skull"
    ),
    "dungeon_catacombs": Location(
        id="dungeon_catacombs", name="Catacombs & Treasure Vault (Floor 2)", zone="dungeon",
        x=120.0, y=40.0, width=16.0, height=20.0, walk_x=128.0, walk_y=51.0, capacity=20,
        description="Ancient labyrinth filled with massive pillars, traps, and gilded treasure chests overflowing with gold and gems.",
        objects=["carved_pillars", "gilded_chests", "gold_coins", "iron_cages"],
        color="#B45309", icon="coins"
    ),
    "dungeon_boss_chamber": Location(
        id="dungeon_boss_chamber", name="Abyssal Sanctum (Boss Floor)", zone="dungeon",
        x=120.0, y=68.0, width=16.0, height=20.0, walk_x=128.0, walk_y=79.0, capacity=20,
        description="Massive bloodstone chamber with a giant glowing crimson summon pentagram and the Horned Dragon Altar.",
        objects=["crimson_pentagram", "dragon_skull_altar", "flaming_skull_sconces", "boss_throne"],
        color="#DC2626", icon="flame"
    ),

    # 5. Adventurer Residential Cottages
    "cottage_nw": Location(
        id="cottage_nw", name="Silvercrest Cottage", zone="residential",
        x=36.0, y=64.0, width=12.0, height=10.0, walk_x=42.0, walk_y=70.0, capacity=4,
        description="Cozy stone-and-timber cottage with wooden furniture, hearth, and bunk beds for adventurers.",
        objects=["bunk_beds", "fireplace", "dining_table", "bookshelf"],
        color="#0284C7", icon="home"
    ),
    "cottage_ne": Location(
        id="cottage_ne", name="Arcane Spire Lodge", zone="residential",
        x=56.0, y=64.0, width=12.0, height=10.0, walk_x=62.0, walk_y=70.0, capacity=4,
        description="Comfortable lodge for mages and scholars with study desk, scroll racks, and tea hearth.",
        objects=["study_desk", "scroll_racks", "single_beds", "wardrobe"],
        color="#8B5CF6", icon="home"
    ),
    "cottage_sw": Location(
        id="cottage_sw", name="Oakwood Quarters", zone="residential",
        x=36.0, y=78.0, width=12.0, height=10.0, walk_x=42.0, walk_y=84.0, capacity=4,
        description="Hearty wooden cottage housing veteran rangers and trackers.",
        objects=["beds", "weapon_rack", "round_table", "armchair"],
        color="#15803D", icon="home"
    ),
    "cottage_se": Location(
        id="cottage_se", name="Vanguard Lodgings", zone="residential",
        x=56.0, y=78.0, width=12.0, height=10.0, walk_x=62.0, walk_y=84.0, capacity=4,
        description="Fortified residence for knights and warriors with shields mounted above the hearth.",
        objects=["plate_armor_stand", "beds", "shield_wall", "chest"],
        color="#4338CA", icon="home"
    ),
}

# Full Alias Mapping for backward compatibility with Smallville IDs
LOCATION_ALIASES = {
    # Civic / Commerce / Guild
    "cafe": "guild_hall",
    "pub": "tavern",
    "market": "town_square",
    "supply_store": "blacksmith",
    "college": "apothecary",
    "dorm": "guild_hall",
    "park": "training_grounds",
    "artist_space": "cottage_ne",
    "bakery": "tavern",
    "general_store": "town_square",
    "workshop": "blacksmith",
    "library": "apothecary",
    "clinic": "apothecary",
    "community_center": "guild_hall",
    "farm": "training_grounds",
    "town_hall": "guild_hall",

    # Dungeon Aliases
    "dungeon": "dungeon_entrance",
    "crypt": "dungeon_crypt",
    "catacombs": "dungeon_catacombs",
    "boss_room": "dungeon_boss_chamber",
    "boss": "dungeon_boss_chamber",

    # Residential Aliases
    "home_arthur": "cottage_se",
    "home_ryan": "cottage_nw",
    "home_isabella": "cottage_ne",
    "home_giorgio": "cottage_sw",
    "home_carlos": "cottage_se",
    "home_adam": "cottage_nw",
    "home_yuriko": "cottage_sw",
    "home_moore": "cottage_se",
    "home_tamara_carmen": "cottage_ne",
    "home_moreno": "cottage_nw",
    "home_lin": "cottage_sw",
    "home_1": "cottage_se",
    "home_2": "cottage_nw",
    "home_3": "cottage_sw",
    "home_4": "cottage_ne",
    "home_5": "cottage_se",
    "home_6": "cottage_sw",
    "home_7": "cottage_se",
    "home_8": "cottage_sw",
    "home_9": "cottage_ne",
    "home_10": "cottage_sw",
    "home_11": "cottage_nw",
    "home_12": "cottage_ne",
}

def get_location(location_id: str) -> Optional[Location]:
    target = LOCATION_ALIASES.get(location_id, location_id)
    return TOWN_LOCATIONS.get(target)

def get_all_locations() -> List[Location]:
    return list(TOWN_LOCATIONS.values())

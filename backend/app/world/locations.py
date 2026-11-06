from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class Location(BaseModel):
    id: str
    name: str
    zone: str  # residential, commercial, civic, hospitality, park, agriculture
    x: float
    y: float
    width: float = 12.0
    height: float = 10.0
    capacity: int = 20
    description: str
    objects: List[str] = Field(default_factory=list)
    color: str = "#4A5568"
    icon: str = "building"

# Smallville / The Ville Authentic Locations Registry
TOWN_LOCATIONS: Dict[str, Location] = {
    # 1. Hospitality & Dining
    "cafe": Location(
        id="cafe", name="Hobbs Cafe", zone="hospitality",
        x=72.0, y=17.0, width=14.0, height=10.0, capacity=25,
        description="The town's cozy coffeehouse with polished wooden counters, fresh pastries, and cafe tables.",
        objects=["espresso_machine", "pastry_case", "dining_table", "wooden_chair", "piano"],
        color="#F472B6", icon="coffee"
    ),
    "pub": Location(
        id="pub", name="The Rose and Crown Pub", zone="hospitality",
        x=52.0, y=18.0, width=12.0, height=9.0, capacity=30,
        description="Lively neighborhood tavern with warm hearth, bar counter, and draught taps.",
        objects=["bar_counter", "beer_taps", "fireplace", "dartboard", "bistro_tables"],
        color="#CA8A04", icon="beer"
    ),

    # 2. Commercial & Supply
    "market": Location(
        id="market", name="The Willows Market & Pharmacy", zone="commercial",
        x=74.0, y=42.0, width=21.0, height=12.0, capacity=35,
        description="Bustling marketplace with grocery shelves, pharmaceutical apothecary, and checkout counter.",
        objects=["pharmacy_counter", "produce_shelves", "register", "refrigerators"],
        color="#EA580C", icon="store"
    ),
    "supply_store": Location(
        id="supply_store", name="Harvey Oak Supply Store & Craft", zone="commercial",
        x=56.0, y=42.0, width=16.0, height=12.0, capacity=20,
        description="Hardware, carpentry tools, timber, and iron crafting equipment.",
        objects=["workbench", "hardware_shelves", "timber_rack", "forge_tools"],
        color="#78716C", icon="hammer"
    ),

    # 3. Nature & Civic Parks
    "park": Location(
        id="park", name="Johnson Park & Garden", zone="park",
        x=20.0, y=41.0, width=16.0, height=11.0, capacity=40,
        description="Green lawn with flowering shrubs, wooden fence, gravel trail, and park benches.",
        objects=["park_bench", "fountain", "flowering_bushes", "wooden_bridge"],
        color="#22C55E", icon="trees"
    ),

    # 4. Civic & Education
    "college": Location(
        id="college", name="Oak Hill College Classrooms", zone="civic",
        x=107.0, y=19.0, width=19.0, height=16.0, capacity=35,
        description="Lecture hall with wooden desks, podium, and historical reference books.",
        objects=["chalkboard", "student_desks", "podium", "library_stacks"],
        color="#2563EB", icon="landmark"
    ),
    "dorm": Location(
        id="dorm", name="Dormitory for Oak Hill College", zone="civic",
        x=105.0, y=32.0, width=28.0, height=28.0, capacity=40,
        description="Multi-room student residency with study nooks, common kitchen, and shared dorm rooms.",
        objects=["study_desks", "single_beds", "common_sofa", "coffee_maker"],
        color="#3B82F6", icon="users"
    ),
    "artist_space": Location(
        id="artist_space", name="Artist's Co-Living Space & Studio", zone="civic",
        x=14.0, y=17.0, width=30.0, height=18.0, capacity=25,
        description="Creative studio loft with painting easels, musical instruments, and sculptures.",
        objects=["easels", "canvas_racks", "drafting_tables", "acoustic_instruments"],
        color="#EC4899", icon="palette"
    ),

    # 5. Residential Houses & Apartments
    "home_arthur": Location(
        id="home_arthur", name="Arthur Burton's Apartment", zone="residential",
        x=52.0, y=13.0, width=12.0, height=7.0, capacity=3,
        description="Neat apartment with writing desk, armchair, and bookshelf.",
        objects=["bed", "writing_desk", "bookshelf", "kitchenette"],
        color="#7C3AED", icon="home"
    ),
    "home_ryan": Location(
        id="home_ryan", name="Ryan Park's Apartment", zone="residential",
        x=64.0, y=13.0, width=7.0, height=14.0, capacity=2,
        description="Cozy studio apartment with modern setup.",
        objects=["bed", "computer_desk", "wardrobe"],
        color="#0284C7", icon="home"
    ),
    "home_isabella": Location(
        id="home_isabella", name="Isabella Rodriguez's Apartment", zone="residential",
        x=71.0, y=13.0, width=14.0, height=6.0, capacity=2,
        description="Sunlit studio with plant planters and culinary spice jars.",
        objects=["bed", "kitchen_counter", "sofa"],
        color="#E11D48", icon="home"
    ),
    "home_giorgio": Location(
        id="home_giorgio", name="Giorgio Rossi's Apartment", zone="residential",
        x=85.0, y=12.0, width=7.0, height=14.0, capacity=2,
        description="Classic bachelor pad with espresso machine and framed art.",
        objects=["bed", "armchair", "sound_system"],
        color="#F59E0B", icon="home"
    ),
    "home_carlos": Location(
        id="home_carlos", name="Carlos Gomez's Apartment", zone="residential",
        x=92.0, y=12.0, width=7.0, height=14.0, capacity=2,
        description="Tidy apartment with sports gear and guitar in the corner.",
        objects=["bed", "closet", "desk"],
        color="#10B981", icon="home"
    ),
    "home_adam": Location(
        id="home_adam", name="Adam Smith's House", zone="residential",
        x=19.0, y=58.0, width=7.0, height=13.0, capacity=3,
        description="Traditional house with wooden siding and front garden porch.",
        objects=["double_bed", "dining_table", "bookshelves"],
        color="#64748B", icon="home"
    ),
    "home_yuriko": Location(
        id="home_yuriko", name="Yuriko Yamamoto's House", zone="residential",
        x=27.0, y=58.0, width=7.0, height=13.0, capacity=3,
        description="Peaceful house with tatami accents, tea table, and bonsai.",
        objects=["futon_bed", "tea_set", "zen_screen"],
        color="#8B5CF6", icon="home"
    ),
    "home_moore": Location(
        id="home_moore", name="Moore Family's House", zone="residential",
        x=35.0, y=58.0, width=7.0, height=13.0, capacity=4,
        description="Family home with garden tools, children's books, and large kitchen table.",
        objects=["family_beds", "dining_suite", "refrigerator"],
        color="#D97706", icon="home"
    ),
    "home_tamara_carmen": Location(
        id="home_tamara_carmen", name="Tamara & Carmen's House", zone="residential",
        x=50.0, y=64.0, width=14.0, height=19.0, capacity=4,
        description="Spacious shared house with open living room and garden patio.",
        objects=["living_room_couches", "kitchen_island", "patio_chairs"],
        color="#EC4899", icon="home"
    ),
    "home_moreno": Location(
        id="home_moreno", name="Moreno Family's House", zone="residential",
        x=68.0, y=64.0, width=14.0, height=19.0, capacity=4,
        description="Warm brick home filled with family portraits and baking aromas.",
        objects=["dining_table", "fireplace", "study_nook"],
        color="#F97316", icon="home"
    ),
    "home_lin": Location(
        id="home_lin", name="Lin Family's House", zone="residential",
        x=86.0, y=64.0, width=14.0, height=19.0, capacity=4,
        description="Welcoming house with flourishing houseplants and musical instruments.",
        objects=["upright_piano", "garden_tools", "study_desks"],
        color="#14B8A6", icon="home"
    ),
}

# Alias mapping for backward compatibility with earlier fixtures
LOCATION_ALIASES = {
    "bakery": "cafe",
    "town_square": "cafe",
    "tavern": "pub",
    "marketplace": "market",
    "general_store": "supply_store",
    "workshop": "supply_store",
    "library": "college",
    "clinic": "market",
    "community_center": "dorm",
    "farm": "park",
    "town_hall": "college",
    "home_1": "home_arthur",
    "home_2": "home_moreno",
    "home_3": "home_adam",
    "home_4": "home_isabella",
    "home_5": "home_carlos",
    "home_6": "home_yuriko",
    "home_7": "home_moore",
    "home_8": "home_lin",
    "home_9": "home_tamara_carmen",
    "home_10": "home_giorgio",
    "home_11": "home_ryan",
    "home_12": "artist_space",
}

def get_location(location_id: str) -> Optional[Location]:
    target = LOCATION_ALIASES.get(location_id, location_id)
    return TOWN_LOCATIONS.get(target)

def get_all_locations() -> List[Location]:
    return list(TOWN_LOCATIONS.values())

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class Location(BaseModel):
    id: str
    name: str
    zone: str  # residential, commercial, civic, hospitality, park, agriculture
    x: float
    y: float
    width: float = 6.0
    height: float = 5.0
    capacity: int = 20
    description: str
    objects: List[str] = Field(default_factory=list)
    color: str = "#4A5568"
    icon: str = "building"

# Town Locations Registry
TOWN_LOCATIONS: Dict[str, Location] = {
    # Residential Homes (1-12)
    "home_1": Location(
        id="home_1", name="Vance Manor", zone="residential",
        x=4.0, y=4.0, capacity=4, description="Grand brick house belonging to Arthur Vance and sons Victor & Ethan.",
        objects=["study_desk", "bed", "bookshelf", "fireplace", "dining_table"],
        color="#7C3AED", icon="home"
    ),
    "home_2": Location(
        id="home_2", name="Bennett Cottage", zone="residential",
        x=12.0, y=4.0, capacity=2, description="Cozy cottage of Clara Bennett with sweet lavender in window boxes.",
        objects=["kitchen_stove", "bed", "recipe_rack", "herb_planter"],
        color="#EC4899", icon="home"
    ),
    "home_3": Location(
        id="home_3", name="Thorne Residence", zone="residential",
        x=20.0, y=4.0, capacity=2, description="Neat, quiet home of Dr. Marcus Thorne, smelling of dried chamomile.",
        objects=["medical_cabinet", "bed", "reading_lamp", "tea_station"],
        color="#0284C7", icon="home"
    ),
    "home_4": Location(
        id="home_4", name="Rostova Studio", zone="residential",
        x=4.0, y=10.0, capacity=2, description="Charming attic apartment of Elena Rostova, filled with maps and note pins.",
        objects=["typewriter", "bed", "bulletin_board", "coffee_maker"],
        color="#F59E0B", icon="home"
    ),
    "home_5": Location(
        id="home_5", name="Gray & Brooks Shared Flat", zone="residential",
        x=12.0, y=10.0, capacity=3, description="Simple, bustling home shared by Lucas Gray and Noah Brooks.",
        objects=["woodworking_models", "fishing_rods", "bunk_bed", "guitar"],
        color="#10B981", icon="home"
    ),
    "home_6": Location(
        id="home_6", name="Ward Sanctuary", zone="residential",
        x=20.0, y=10.0, capacity=2, description="Warm, welcoming home of Beatrice Ward filled with family quilts and tea.",
        objects=["rocking_chair", "tea_service", "bed", "family_photos"],
        color="#8B5CF6", icon="home"
    ),
    "home_7": Location(
        id="home_7", name="Miller Lodging", zone="residential",
        x=4.0, y=16.0, capacity=2, description="Sturdy timber house of David Miller adjacent to his forge.",
        objects=["heavy_workbench", "bed", "iron_stove"],
        color="#64748B", icon="home"
    ),
    "home_8": Location(
        id="home_8", name="Lin Greenhouse House", zone="residential",
        x=12.0, y=16.0, capacity=2, description="Lush home of Sophie Lin surrounded by exotic flowering orchids.",
        objects=["botanical_press", "bed", "watering_can", "terrarium"],
        color="#10B981", icon="home"
    ),
    "home_9": Location(
        id="home_9", name="Jenkins & Martin House", zone="residential",
        x=20.0, y=16.0, capacity=3, description="Artistic home shared by Sarah Jenkins and young Chloe Martin.",
        objects=["easel", "bookshelves", "bed", "oil_paints"],
        color="#F43F5E", icon="home"
    ),
    "home_10": Location(
        id="home_10", name="Wright Clock Loft", zone="residential",
        x=4.0, y=22.0, capacity=2, description="Ticking home of Oliver Wright, filled with pendulum clocks.",
        objects=["gears_desk", "bed", "magnifying_lens", "grandfather_clock"],
        color="#D97706", icon="home"
    ),
    "home_11": Location(
        id="home_11", name="Patel & Rivera Quarters", zone="residential",
        x=12.0, y=22.0, capacity=3, description="Pleasant town home of Maya Patel and teacher Nora Rivera.",
        objects=["lesson_planner", "herb_mortar", "bed", "dining_nook"],
        color="#06B6D4", icon="home"
    ),
    "home_12": Location(
        id="home_12", name="Innovator Lodge", zone="residential",
        x=20.0, y=22.0, capacity=4, description="Modern shared quarters for Zoe Zhao, Felix Kim, and Julian Cole.",
        objects=["workstation", "delivery_crates", "acoustic_bass", "bed"],
        color="#3B82F6", icon="home"
    ),

    # Civic & Services (North-East)
    "town_hall": Location(
        id="town_hall", name="Town Hall & Council Chamber", zone="civic",
        x=42.0, y=4.0, width=8.0, height=6.0, capacity=30,
        description="The heart of local governance, mayor's desk, and civic record archives.",
        objects=["mayors_desk", "podium", "public_bulletin", "council_benches", "records_archive"],
        color="#2563EB", icon="landmark"
    ),
    "clinic": Location(
        id="clinic", name="St. Jude Clinic & Apothecary", zone="civic",
        x=52.0, y=4.0, width=7.0, height=5.0, capacity=15,
        description="Clean medical examination center and herbal dispensary run by Dr. Thorne & Maya Patel.",
        objects=["exam_bed", "medicine_jars", "stethoscope", "waiting_chairs", "wash_basin"],
        color="#EF4444", icon="cross"
    ),
    "library": Location(
        id="library", name="Town Library & Archives", zone="civic",
        x=42.0, y=12.0, width=8.0, height=5.0, capacity=20,
        description="Peaceful sanctum of knowledge curated by Sarah Jenkins with high oak shelves.",
        objects=["reading_tables", "card_catalog", "archive_stacks", "armchairs"],
        color="#059669", icon="book-open"
    ),
    "community_center": Location(
        id="community_center", name="Community Center Hall", zone="civic",
        x=52.0, y=12.0, width=7.0, height=5.0, capacity=35,
        description="Versatile multi-purpose hall for town meetings, celebrations, and workshops.",
        objects=["stage", "folding_chairs", "notice_board", "kitchenette", "piano"],
        color="#8B5CF6", icon="users"
    ),

    # Commercial & Marketplace (Center)
    "town_square": Location(
        id="town_square", name="Town Square & Fountain", zone="commercial",
        x=32.0, y=18.0, width=8.0, height=6.0, capacity=40,
        description="Cobblestone gathering plaza surrounding the great central fountain.",
        objects=["central_fountain", "stone_benches", "pigeon_perch", "streetlamp"],
        color="#38BDF8", icon="sparkles"
    ),
    "marketplace": Location(
        id="marketplace", name="Marketplace Stalls", zone="commercial",
        x=24.0, y=18.0, width=7.0, height=6.0, capacity=25,
        description="Bustling outdoor market with produce, wares, and vibrant bartering.",
        objects=["vegetable_crates", "canopy_stall", "scales", "display_baskets"],
        color="#F59E0B", icon="store"
    ),
    "general_store": Location(
        id="general_store", name="Reed's General Goods", zone="commercial",
        x=42.0, y=18.0, width=7.0, height=5.0, capacity=15,
        description="Dry goods, tools, household sundries, managed by Samuel Reed.",
        objects=["checkout_counter", "shelving_aisles", "canned_goods", "register"],
        color="#EA580C", icon="shopping-bag"
    ),
    "workshop": Location(
        id="workshop", name="Master Craft Workshop & Forge", zone="commercial",
        x=50.0, y=18.0, width=8.0, height=6.0, capacity=15,
        description="Smell of cedar shavings and glowing forge fire. Henry Fletcher and David Miller work here.",
        objects=["anvil", "forge", "carpentry_bench", "lathe", "tool_racks"],
        color="#78716C", icon="hammer"
    ),

    # Hospitality & Dining (South-West)
    "bakery": Location(
        id="bakery", name="Bella's Bakery & Café", zone="hospitality",
        x=8.0, y=30.0, width=7.0, height=5.0, capacity=20,
        description="Sweet aromas of fresh sourdough, croissants, and espresso. Clara Bennett's pride.",
        objects=["bread_ovens", "pastry_display", "espresso_machine", "café_tables"],
        color="#F472B6", icon="coffee"
    ),
    "tavern": Location(
        id="tavern", name="The Golden Spire Tavern", zone="hospitality",
        x=16.0, y=30.0, width=8.0, height=6.0, capacity=35,
        description="Lively neighborhood tavern with polished oak bar, fireplace, and Julian's stage.",
        objects=["bar_counter", "beer_taps", "fireplace", "dartboard", "tavern_tables"],
        color="#CA8A04", icon="beer"
    ),
    "bistro": Location(
        id="bistro", name="Riverside Bistro", zone="hospitality",
        x=25.0, y=30.0, width=7.0, height=5.0, capacity=22,
        description="Fine dining restaurant run by passionate Chef Isabella Rossi.",
        objects=["chef_range", "wine_rack", "dining_linen", "order_counter"],
        color="#E11D48", icon="utensils"
    ),

    # Parklands & Nature (South-East)
    "park": Location(
        id="park", name="Oakridge Park & Duck Pond", zone="park",
        x=34.0, y=28.0, width=10.0, height=8.0, capacity=40,
        description="Serene green park with duck pond, willow trees, and walking trails.",
        objects=["duck_pond", "wooden_bridge", "picnic_tables", "flowering_bushes", "bench"],
        color="#22C55E", icon="trees"
    ),
    "farm": Location(
        id="farm", name="Greenfield Farmstead", zone="agriculture",
        x=46.0, y=28.0, width=12.0, height=8.0, capacity=15,
        description="Rolling vegetable patches, apple orchards, and grain storage tended by Hannah Abbott.",
        objects=["apple_trees", "vegetable_beds", "tractor", "storage_barn", "water_well"],
        color="#84CC16", icon="tractor"
    ),
}

def get_location(location_id: str) -> Optional[Location]:
    return TOWN_LOCATIONS.get(location_id)

def get_all_locations() -> List[Location]:
    return list(TOWN_LOCATIONS.values())


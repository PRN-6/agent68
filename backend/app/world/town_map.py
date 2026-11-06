from typing import Dict, Any, List
from app.world.locations import TOWN_LOCATIONS, get_all_locations

class TownMap:
    def __init__(self):
        self.width: int = 140
        self.height: int = 100
        self.locations = TOWN_LOCATIONS
        
        self.roads: List[Dict[str, Any]] = [
            # Main East-West High Street to Bridge & Dungeon
            {"x1": 10, "y1": 49, "x2": 115, "y2": 49, "width": 3},
            # North-South Avenue connecting Guild & Tavern to Plaza & Cottages
            {"x1": 43, "y1": 20, "x2": 43, "y2": 85, "width": 3},
            # West Avenue connecting Tavern, Blacksmith, and Arena
            {"x1": 20, "y1": 22, "x2": 20, "y2": 75, "width": 2},
        ]

    def get_map_metadata(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "roads": self.roads,
            "locations": [loc.model_dump() for loc in get_all_locations()],
            "districts": [
                {"name": "Adventurer's Guild & Tavern", "bounds": {"x": 8, "y": 8, "w": 50, "h": 24}, "color": "rgba(99, 102, 241, 0.12)"},
                {"name": "Sunhaven Plaza & Arcane Sanctum", "bounds": {"x": 8, "y": 34, "w": 68, "h": 26}, "color": "rgba(245, 158, 11, 0.12)"},
                {"name": "Hero Arena & Cottages", "bounds": {"x": 8, "y": 62, "w": 68, "h": 32}, "color": "rgba(34, 197, 94, 0.12)"},
                {"name": "The River & Whispering Forest", "bounds": {"x": 78, "y": 4, "w": 32, "h": 92}, "color": "rgba(56, 189, 248, 0.12)"},
                {"name": "The Shadow Crypts / Dungeon", "bounds": {"x": 112, "y": 4, "w": 26, "h": 92}, "color": "rgba(168, 85, 247, 0.15)"},
            ]
        }

town_map = TownMap()

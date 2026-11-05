from typing import Dict, Any, List
from app.world.locations import TOWN_LOCATIONS, get_all_locations

class TownMap:
    def __init__(self):
        self.width: int = 60
        self.height: int = 40
        self.locations = TOWN_LOCATIONS
        
        # Major roads segments for frontend drawing
        self.roads: List[Dict[str, Any]] = [
            # Horizontal main avenues
            {"x1": 4, "y1": 8, "x2": 56, "y2": 8, "width": 2},
            {"x1": 4, "y1": 14, "x2": 56, "y2": 14, "width": 2},
            {"x1": 4, "y1": 20, "x2": 56, "y2": 20, "width": 3},  # Central Market Blvd
            {"x1": 4, "y1": 26, "x2": 56, "y2": 26, "width": 2},
            
            # Vertical avenues
            {"x1": 16, "y1": 4, "x2": 16, "y2": 36, "width": 2},  # West Lane
            {"x1": 30, "y1": 4, "x2": 30, "y2": 36, "width": 3},  # High Street
            {"x1": 40, "y1": 4, "x2": 40, "y2": 36, "width": 2},  # Civic Way
            {"x1": 50, "y1": 4, "x2": 50, "y2": 36, "width": 2},  # East Walk
        ]

    def get_map_metadata(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "roads": self.roads,
            "locations": [loc.dict() for loc in get_all_locations()],
            "districts": [
                {"name": "Residential Quarter", "bounds": {"x": 2, "y": 2, "w": 24, "h": 25}, "color": "rgba(99, 102, 241, 0.08)"},
                {"name": "Civic & Medical Center", "bounds": {"x": 38, "y": 2, "w": 20, "h": 14}, "color": "rgba(59, 130, 246, 0.08)"},
                {"name": "Central Plaza & Market", "bounds": {"x": 22, "y": 16, "w": 34, "h": 10}, "color": "rgba(245, 158, 11, 0.08)"},
                {"name": "Dining & Hospitality", "bounds": {"x": 4, "y": 28, "w": 26, "h": 10}, "color": "rgba(236, 72, 153, 0.08)"},
                {"name": "Parklands & Orchards", "bounds": {"x": 32, "y": 26, "w": 26, "h": 12}, "color": "rgba(34, 197, 94, 0.08)"},
            ]
        }

town_map = TownMap()


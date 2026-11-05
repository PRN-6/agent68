import math
from typing import List, Tuple, Dict, Optional

# Waypoints representing key road intersections and building entrances
WAYPOINTS: Dict[str, Tuple[float, float]] = {
    # Road network nodes
    "wp_north_west": (16.0, 8.0),
    "wp_north_mid": (30.0, 8.0),
    "wp_north_east": (40.0, 8.0),
    "wp_north_far_east": (50.0, 8.0),
    
    "wp_mid_west": (16.0, 14.0),
    "wp_plaza_north": (30.0, 14.0),
    "wp_mid_east": (40.0, 14.0),
    "wp_mid_far_east": (50.0, 14.0),
    
    "wp_plaza_west": (22.0, 20.0),
    "wp_plaza_center": (30.0, 20.0),
    "wp_plaza_east": (38.0, 20.0),
    
    "wp_south_west": (16.0, 26.0),
    "wp_south_mid": (30.0, 26.0),
    "wp_south_east": (40.0, 26.0),
    "wp_south_far_east": (50.0, 26.0),
    
    # Building Entrance Waypoints
    "ent_home_1": (7.0, 8.0),
    "ent_home_2": (15.0, 8.0),
    "ent_home_3": (23.0, 8.0),
    "ent_home_4": (7.0, 14.0),
    "ent_home_5": (15.0, 14.0),
    "ent_home_6": (23.0, 14.0),
    "ent_home_7": (7.0, 20.0),
    "ent_home_8": (15.0, 20.0),
    "ent_home_9": (23.0, 20.0),
    "ent_home_10": (7.0, 26.0),
    "ent_home_11": (15.0, 26.0),
    "ent_home_12": (23.0, 26.0),
    
    "ent_town_hall": (42.0, 8.0),
    "ent_clinic": (52.0, 8.0),
    "ent_library": (42.0, 14.0),
    "ent_community_center": (52.0, 14.0),
    
    "ent_town_square": (32.0, 20.0),
    "ent_marketplace": (24.0, 20.0),
    "ent_general_store": (42.0, 20.0),
    "ent_workshop": (50.0, 20.0),
    
    "ent_bakery": (11.0, 28.0),
    "ent_tavern": (19.0, 28.0),
    "ent_bistro": (27.0, 28.0),
    
    "ent_park": (36.0, 28.0),
    "ent_farm": (48.0, 28.0),
}

# Graph Adjacency List for Waypoints
WAYPOINT_GRAPH: Dict[str, List[str]] = {
    "wp_north_west": ["wp_north_mid", "wp_mid_west", "ent_home_1", "ent_home_2"],
    "wp_north_mid": ["wp_north_west", "wp_north_east", "wp_plaza_north", "ent_home_3"],
    "wp_north_east": ["wp_north_mid", "wp_north_far_east", "wp_mid_east", "ent_town_hall"],
    "wp_north_far_east": ["wp_north_east", "wp_mid_far_east", "ent_clinic"],
    
    "wp_mid_west": ["wp_north_west", "wp_plaza_west", "wp_south_west", "ent_home_4", "ent_home_5", "ent_home_6"],
    "wp_plaza_north": ["wp_north_mid", "wp_plaza_center", "wp_plaza_west", "wp_plaza_east"],
    "wp_mid_east": ["wp_north_east", "wp_plaza_east", "wp_south_east", "ent_library"],
    "wp_mid_far_east": ["wp_north_far_east", "wp_south_far_east", "ent_community_center"],
    
    "wp_plaza_west": ["wp_mid_west", "wp_plaza_center", "ent_marketplace", "ent_home_7", "ent_home_8", "ent_home_9"],
    "wp_plaza_center": ["wp_plaza_north", "wp_plaza_west", "wp_plaza_east", "wp_south_mid", "ent_town_square"],
    "wp_plaza_east": ["wp_plaza_center", "wp_mid_east", "ent_general_store", "ent_workshop"],
    
    "wp_south_west": ["wp_mid_west", "wp_south_mid", "ent_bakery", "ent_tavern", "ent_home_10", "ent_home_11", "ent_home_12"],
    "wp_south_mid": ["wp_plaza_center", "wp_south_west", "wp_south_east", "ent_bistro", "ent_park"],
    "wp_south_east": ["wp_mid_east", "wp_south_mid", "wp_south_far_east", "ent_park"],
    "wp_south_far_east": ["wp_mid_far_east", "wp_south_east", "ent_farm"],
    
    # Entrances to nodes
    "ent_home_1": ["wp_north_west"],
    "ent_home_2": ["wp_north_west"],
    "ent_home_3": ["wp_north_mid"],
    "ent_home_4": ["wp_mid_west"],
    "ent_home_5": ["wp_mid_west"],
    "ent_home_6": ["wp_mid_west"],
    "ent_home_7": ["wp_plaza_west"],
    "ent_home_8": ["wp_plaza_west"],
    "ent_home_9": ["wp_plaza_west"],
    "ent_home_10": ["wp_south_west"],
    "ent_home_11": ["wp_south_west"],
    "ent_home_12": ["wp_south_west"],
    
    "ent_town_hall": ["wp_north_east"],
    "ent_clinic": ["wp_north_far_east"],
    "ent_library": ["wp_mid_east"],
    "ent_community_center": ["wp_mid_far_east"],
    
    "ent_town_square": ["wp_plaza_center"],
    "ent_marketplace": ["wp_plaza_west"],
    "ent_general_store": ["wp_plaza_east"],
    "ent_workshop": ["wp_plaza_east"],
    
    "ent_bakery": ["wp_south_west"],
    "ent_tavern": ["wp_south_west"],
    "ent_bistro": ["wp_south_mid"],
    "ent_park": ["wp_south_mid", "wp_south_east"],
    "ent_farm": ["wp_south_far_east"],
}

def euclidean_dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def find_nearest_waypoint(coord: Tuple[float, float]) -> str:
    best_wp = "wp_plaza_center"
    best_dist = float("inf")
    for wp, pt in WAYPOINTS.items():
        dist = euclidean_dist(coord, pt)
        if dist < best_dist:
            best_dist = dist
            best_wp = wp
    return best_wp

def find_path(start_coord: Tuple[float, float], end_coord: Tuple[float, float]) -> List[Tuple[float, float]]:
    """Dijkstra/A* to find smooth path coordinates between any two points."""
    start_wp = find_nearest_waypoint(start_coord)
    end_wp = find_nearest_waypoint(end_coord)
    
    if start_wp == end_wp:
        return [start_coord, end_coord]
        
    # Dijkstra
    dist: Dict[str, float] = {wp: float("inf") for wp in WAYPOINTS}
    parent: Dict[str, Optional[str]] = {wp: None for wp in WAYPOINTS}
    dist[start_wp] = 0.0
    
    unvisited = set(WAYPOINTS.keys())
    
    while unvisited:
        # Node with smallest distance
        current = min(unvisited, key=lambda wp: dist[wp])
        if dist[current] == float("inf"):
            break
        if current == end_wp:
            break
        unvisited.remove(current)
        
        for neighbor in WAYPOINT_GRAPH.get(current, []):
            if neighbor not in unvisited:
                continue
            d = dist[current] + euclidean_dist(WAYPOINTS[current], WAYPOINTS[neighbor])
            if d < dist[neighbor]:
                dist[neighbor] = d
                parent[neighbor] = current
                
    # Reconstruct path
    wp_path = []
    curr = end_wp
    while curr is not None:
        wp_path.append(curr)
        curr = parent[curr]
    wp_path.reverse()
    
    # Convert waypoints to coordinates
    coords = [start_coord]
    for wp in wp_path:
        coords.append(WAYPOINTS[wp])
    coords.append(end_coord)
    
    # Simplify duplicate sequential coords
    clean_coords = [coords[0]]
    for pt in coords[1:]:
        if euclidean_dist(clean_coords[-1], pt) > 0.05:
            clean_coords.append(pt)
            
    return clean_coords

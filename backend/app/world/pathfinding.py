import os
import json
import heapq
from collections import deque
from typing import List, Tuple, Dict, Optional

# Load Smallville 140x100 collision grid
COLLISION_GRID_PATH = os.path.join(os.path.dirname(__file__), "collision_grid.json")

GRID: List[List[int]] = []
H = 100
W = 140

if os.path.exists(COLLISION_GRID_PATH):
    try:
        with open(COLLISION_GRID_PATH, "r", encoding="utf-8") as f:
            GRID = json.load(f)
            H = len(GRID)
            W = len(GRID[0])
    except Exception as e:
        print(f"Error loading collision_grid.json: {e}")

# Fallback empty grid if file was not loaded
if not GRID:
    GRID = [[0 for _ in range(W)] for _ in range(H)]

# Path cache for rapid reuse
_PATH_CACHE: Dict[Tuple[int, int, int, int], List[Tuple[float, float]]] = {}
_MAX_CACHE_SIZE = 1000

def is_walkable(x: int, y: int) -> bool:
    if 0 <= x < W and 0 <= y < H:
        return GRID[y][x] == 0
    return False

def find_nearest_walkable(x: float, y: float) -> Tuple[int, int]:
    """Finds the nearest walkable tile if coordinate is on an obstacle or out of bounds."""
    ix = max(0, min(W - 1, int(round(x))))
    iy = max(0, min(H - 1, int(round(y))))

    if is_walkable(ix, iy):
        return (ix, iy)

    queue = deque([(ix, iy)])
    visited = {(ix, iy)}

    while queue:
        cx, cy = queue.popleft()
        if is_walkable(cx, cy):
            return (cx, cy)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    return (ix, iy)

def find_path(start_coord: Tuple[float, float], end_coord: Tuple[float, float]) -> List[Tuple[float, float]]:
    """A* Pathfinding over Smallville 140x100 collision grid.
    Guarantees NPCs never walk through walls, fences, counters, or buildings.
    """
    sx, sy = find_nearest_walkable(start_coord[0], start_coord[1])
    gx, gy = find_nearest_walkable(end_coord[0], end_coord[1])

    if sx == gx and sy == gy:
        return [(float(gx), float(gy))]

    cache_key = (sx, sy, gx, gy)
    if cache_key in _PATH_CACHE:
        return list(_PATH_CACHE[cache_key])

    def heuristic(x: int, y: int) -> int:
        return abs(x - gx) + abs(y - gy)

    # Priority queue: (f_score, g_score, (x, y))
    frontier = [(heuristic(sx, sy), 0, (sx, sy))]
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {(sx, sy): None}
    cost_so_far: Dict[Tuple[int, int], int] = {(sx, sy): 0}

    found = False
    while frontier:
        _, current_cost, current = heapq.heappop(frontier)

        if current == (gx, gy):
            found = True
            break

        cx, cy = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if is_walkable(nx, ny):
                new_cost = current_cost + 1
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + heuristic(nx, ny)
                    heapq.heappush(frontier, (priority, new_cost, (nx, ny)))
                    came_from[(nx, ny)] = current

    if not found:
        # Fallback to direct snapped points
        return [(float(sx), float(sy)), (float(gx), float(gy))]

    # Reconstruct path
    curr = (gx, gy)
    path: List[Tuple[float, float]] = []
    while curr is not None:
        path.append((float(curr[0]), float(curr[1])))
        curr = came_from[curr]
    path.reverse()

    # Save to cache
    if len(_PATH_CACHE) > _MAX_CACHE_SIZE:
        _PATH_CACHE.clear()
    _PATH_CACHE[cache_key] = path

    return path

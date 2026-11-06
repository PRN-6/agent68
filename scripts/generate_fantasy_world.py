import os
import json
import math
import random
from PIL import Image, ImageDraw, ImageFilter

MAP_W = 140
MAP_H = 100
TILE_SIZE = 32
WIDTH_PX = MAP_W * TILE_SIZE
HEIGHT_PX = MAP_H * TILE_SIZE

print(f"Generating Fantasy MMORPG World Map: {MAP_W}x{MAP_H} tiles ({WIDTH_PX}x{HEIGHT_PX} px)...")

# Initialize base canvas and foreground canvas
base_img = Image.new("RGBA", (WIDTH_PX, HEIGHT_PX), (34, 139, 34, 255))
fore_img = Image.new("RGBA", (WIDTH_PX, HEIGHT_PX), (0, 0, 0, 0))

draw_base = ImageDraw.Draw(base_img)
draw_fore = ImageDraw.Draw(fore_img)

# Collision Grid: 0 = walkable, 1 = solid obstacle
collision_grid = [[0 for _ in range(MAP_W)] for _ in range(MAP_H)]

def set_solid_rect(x1, y1, x2, y2):
    for y in range(max(0, y1), min(MAP_H, y2 + 1)):
        for x in range(max(0, x1), min(MAP_W, x2 + 1)):
            collision_grid[y][x] = 1

def set_walkable_rect(x1, y1, x2, y2):
    for y in range(max(0, y1), min(MAP_H, y2 + 1)):
        for x in range(max(0, x1), min(MAP_W, x2 + 1)):
            collision_grid[y][x] = 0

# -------------------------------------------------------------
# 1. GROUND TERRAIN GENERATION
# -------------------------------------------------------------
print("1. Painting ground terrain & biomes...")

# Town & Wilds Grass: Soft emerald green with gentle noise
for y in range(MAP_H):
    for x in range(MAP_W):
        if x < 110:
            # Grass with procedural variation
            v = int((math.sin(x * 0.4) + math.cos(y * 0.4) + math.sin((x+y)*0.2)) * 6)
            g = 145 + v
            r = 75 + v // 2
            b = 60 + v // 3
            draw_base.rectangle([x*32, y*32, (x+1)*32-1, (y+1)*32-1], fill=(r, g, b, 255))
        else:
            # Dungeon Dark Obsidian & Slate Ground
            v = int((math.sin(x * 0.6) + math.cos(y * 0.6)) * 8)
            r = 30 + v
            g = 25 + v
            b = 40 + v
            draw_base.rectangle([x*32, y*32, (x+1)*32-1, (y+1)*32-1], fill=(r, g, b, 255))

# Dungeon Outer Mountain / Obsidian Enclosure
for y in range(MAP_H):
    for x in range(110, MAP_W):
        # Dungeon borders are solid rock except gate and interior chambers
        collision_grid[y][x] = 1

# Scatter wildflower flecks on the grass
random.seed(42)
for _ in range(400):
    fx = random.randint(2, 75)
    fy = random.randint(2, 95)
    fcol = random.choice([(255, 230, 100), (244, 114, 182), (255, 255, 255), (147, 197, 253)])
    draw_base.ellipse([fx*32 + 12, fy*32 + 12, fx*32 + 18, fy*32 + 18], fill=fcol)

# -------------------------------------------------------------
# 2. THE GREAT RIVER & THE GRAND STONE BRIDGE
# -------------------------------------------------------------
print("2. Carving Great River and building Grand Stone Bridge...")

# River flows around X = 80 to 86
river_x_center = 82
for y in range(MAP_H):
    offset = int(math.sin(y * 0.1) * 3)
    rx1 = river_x_center + offset - 3
    rx2 = river_x_center + offset + 3
    for x in range(rx1, rx2 + 1):
        # River water gradient
        dist_to_center = abs(x - (river_x_center + offset))
        if dist_to_center <= 1:
            w_col = (25, 95, 175, 255) # Deep water
        elif dist_to_center <= 2:
            w_col = (45, 125, 205, 255) # Mid water
        else:
            w_col = (90, 165, 225, 255) # Shore foam
        
        draw_base.rectangle([x*32, y*32, (x+1)*32-1, (y+1)*32-1], fill=w_col)
        # Add subtle wave ripples
        if (x + y) % 3 == 0:
            draw_base.line([x*32 + 4, y*32 + 16, x*32 + 24, y*32 + 16], fill=(180, 225, 255, 180), width=1)
        
        # Mark water as solid
        collision_grid[y][x] = 1

# The Grand Stone Bridge (X = 77..88, Y = 47..53)
bridge_x1, bridge_y1 = 77, 47
bridge_x2, bridge_y2 = 88, 53

# Bridge Cobblestone Deck
for by in range(bridge_y1, bridge_y2 + 1):
    for bx in range(bridge_x1, bridge_x2 + 1):
        # Stone paving
        is_rail = (by == bridge_y1 or by == bridge_y2)
        if is_rail:
            # Stone balustrade / guardrail
            draw_base.rectangle([bx*32, by*32, (bx+1)*32-1, (by+1)*32-1], fill=(100, 110, 125, 255), outline=(60, 65, 75), width=2)
            # Pillars / lanterns on railing
            if bx % 3 == 0:
                draw_base.rectangle([bx*32+8, by*32+4, bx*32+24, by*32+28], fill=(140, 150, 165, 255))
                draw_base.ellipse([bx*32+10, by*32+8, bx*32+22, by*32+20], fill=(255, 215, 0, 255)) # Lantern
            collision_grid[by][bx] = 1 # railing solid
        else:
            # Walkable bridge road
            p_fill = (150, 145, 135) if (bx + by) % 2 == 0 else (165, 160, 150)
            draw_base.rectangle([bx*32, by*32, (bx+1)*32-1, (by+1)*32-1], fill=p_fill, outline=(115, 110, 100))
            collision_grid[by][bx] = 0 # Walkable bridge roadway!

# -------------------------------------------------------------
# 3. ROADS & PATHWAYS
# -------------------------------------------------------------
print("3. Laying cobblestone high streets & trails...")

def draw_cobblestone_road(x1, y1, x2, y2):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if collision_grid[y][x] != 1 or x >= 78: # Don't overwrite river railings
                c1 = (175, 170, 158, 255) if (x + y) % 2 == 0 else (188, 182, 170, 255)
                draw_base.rectangle([x*32, y*32, (x+1)*32-1, (y+1)*32-1], fill=c1, outline=(140, 135, 125))
                # Add cobblestone speckle details
                draw_base.line([x*32 + 6, y*32 + 8, x*32 + 14, y*32 + 8], fill=(130, 125, 115, 200))
                draw_base.line([x*32 + 18, y*32 + 20, x*32 + 26, y*32 + 20], fill=(130, 125, 115, 200))
                collision_grid[y][x] = 0

def draw_dirt_trail(x1, y1, x2, y2):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            d1 = (160, 130, 95, 255) if (x + y) % 2 == 0 else (175, 142, 105, 255)
            draw_base.rectangle([x*32, y*32, (x+1)*32-1, (y+1)*32-1], fill=d1, outline=(135, 105, 75))
            collision_grid[y][x] = 0

# East-West Main High Street: Town to Bridge
draw_cobblestone_road(10, 48, 77, 51)

# North-South Avenue: Adventurer's Guild & Tavern down to Plaza & Cottages
draw_cobblestone_road(42, 26, 45, 86)

# Connecting road to Tavern (X=20, Y=28 to Y=48)
draw_cobblestone_road(20, 28, 22, 48)

# Connecting road to Blacksmith (X=26, Y=46)
draw_cobblestone_road(24, 46, 32, 49)

# Connecting road to Arcane Sanctum (X=58, Y=46)
draw_cobblestone_road(54, 48, 58, 49)

# Connecting road to Hero's Training Arena (X=19, Y=64 to Y=74)
draw_cobblestone_road(19, 52, 22, 64)

# East of Bridge: Dirt Trail through Whispering Forest to Dungeon Gate
draw_dirt_trail(88, 48, 114, 51)

# -------------------------------------------------------------
# 4. SUNHAVEN TOWN BUILDINGS
# -------------------------------------------------------------
print("4. Constructing Sunhaven Buildings...")

def build_house(x1, y1, x2, y2, door_x, door_y, name, wall_col, floor_col, roof_col=None):
    # Floor
    for y in range(y1 + 1, y2):
        for x in range(x1 + 1, x2):
            draw_base.rectangle([x*32, y*32, (x+1)*32-1, (y+1)*32-1], fill=floor_col, outline=(floor_col[0]-25, floor_col[1]-25, floor_col[2]-25))
            collision_grid[y][x] = 0
            
    # Walls (North, South, East, West)
    for x in range(x1, x2 + 1):
        # North wall (double height for depth)
        draw_base.rectangle([x*32, y1*32, (x+1)*32-1, (y1+1)*32-1], fill=wall_col, outline=(30, 30, 35), width=2)
        collision_grid[y1][x] = 1
        # South wall
        if x != door_x:
            draw_base.rectangle([x*32, y2*32, (x+1)*32-1, (y2+1)*32-1], fill=wall_col, outline=(30, 30, 35), width=2)
            collision_grid[y2][x] = 1
            
    for y in range(y1, y2 + 1):
        # West wall
        draw_base.rectangle([x1*32, y*32, (x1+1)*32-1, (y+1)*32-1], fill=wall_col, outline=(30, 30, 35), width=2)
        collision_grid[y][x1] = 1
        # East wall
        draw_base.rectangle([x2*32, y*32, (x2+1)*32-1, (y+1)*32-1], fill=wall_col, outline=(30, 30, 35), width=2)
        collision_grid[y][x2] = 1

    # Open Door
    draw_base.rectangle([door_x*32, door_y*32, (door_x+1)*32-1, (door_y+1)*32-1], fill=floor_col)
    draw_base.rectangle([door_x*32+4, door_y*32, (door_x+1)*32-5, (door_y+1)*32-1], fill=(120, 85, 50))
    collision_grid[door_y][door_x] = 0

# --- Building A: The Grand Adventurer's Guild ---
build_house(
    x1=34, y1=10, x2=54, y2=26,
    door_x=44, door_y=26,
    name="Adventurer's Guild",
    wall_col=(85, 95, 110),
    floor_col=(210, 195, 170)
)
# Guild Banners & Quest Board
draw_base.rectangle([36*32, 11*32, 42*32, 12*32], fill=(160, 115, 65), outline=(90, 60, 30), width=2) # Quest Notice Board
draw_base.text([37*32, 11*32+6], "QUEST BOUNTIES", fill=(255, 255, 230))
# Guildmaster Desk
draw_base.rectangle([43*32, 12*32, 46*32, 13*32], fill=(110, 75, 40), outline=(60, 40, 20), width=2)
# Guild Long Banquet Tables
for tx in [37, 47]:
    draw_base.rectangle([tx*32, 16*32, (tx+3)*32, 22*32], fill=(130, 90, 50), outline=(70, 45, 25), width=2)
    # Chairs
    for ty in [16, 18, 20]:
        draw_base.rectangle([(tx-1)*32+10, ty*32+4, (tx-1)*32+26, ty*32+28], fill=(90, 60, 30))
        draw_base.rectangle([(tx+3)*32+6, ty*32+4, (tx+3)*32+22, ty*32+28], fill=(90, 60, 30))
# Weapon Racks on walls
draw_base.rectangle([52*32, 14*32, 53*32+16, 20*32], fill=(80, 50, 30), outline=(50, 30, 15))
draw_base.text([52*32+2, 15*32], "WEAPONS", fill=(220, 220, 220))

# --- Building B: The Dragon's Flagon Tavern & Inn ---
build_house(
    x1=10, y1=10, x2=30, y2=28,
    door_x=20, door_y=28,
    name="Dragon's Flagon Tavern",
    wall_col=(115, 80, 55),
    floor_col=(195, 160, 120)
)
# Tavern Bar Counter & Kegs
draw_base.rectangle([12*32, 13*32, 26*32, 14*32+16], fill=(120, 75, 40), outline=(65, 40, 20), width=2)
for kx in range(13, 26, 2):
    draw_base.ellipse([kx*32+4, 11*32+8, kx*32+28, 12*32+28], fill=(150, 95, 45), outline=(80, 45, 20)) # Kegs
# Roaring Stone Fireplace / Hearth
draw_base.rectangle([11*32, 18*32, 12*32+16, 22*32], fill=(90, 95, 100), outline=(50, 50, 55), width=2)
draw_base.rectangle([11*32+6, 19*32, 12*32+10, 21*32], fill=(230, 80, 20)) # Roaring fire
draw_base.ellipse([11*32+10, 19*32+8, 12*32+6, 20*32+24], fill=(255, 220, 50))
# Tavern Dining Tables
for (tx, ty) in [(15, 18), (23, 18), (15, 23), (23, 23)]:
    draw_base.rectangle([tx*32, ty*32, (tx+2)*32, (ty+2)*32], fill=(130, 85, 45), outline=(75, 45, 20), width=2)
    # Stools
    draw_base.ellipse([(tx-1)*32+8, ty*32+8, (tx-1)*32+24, ty*32+24], fill=(100, 65, 30))
    draw_base.ellipse([(tx+2)*32+8, ty*32+8, (tx+2)*32+24, ty*32+24], fill=(100, 65, 30))

# --- Building C: Ironforge Blacksmith & Armory ---
build_house(
    x1=10, y1=38, x2=26, y2=54,
    door_x=26, door_y=46,
    name="Ironforge Blacksmith",
    wall_col=(95, 90, 85),
    floor_col=(140, 135, 130)
)
# Fiery Forge Furnace
draw_base.rectangle([12*32, 40*32, 15*32, 43*32], fill=(70, 70, 75), outline=(40, 40, 45), width=2)
draw_base.ellipse([12*32+12, 40*32+12, 14*32+20, 42*32+20], fill=(255, 100, 20)) # Glowing coals
draw_base.ellipse([13*32, 41*32, 14*32+4, 42*32+4], fill=(255, 240, 120))
# Large Anvil on Stump
draw_base.ellipse([18*32, 42*32, 19*32+16, 43*32+16], fill=(110, 75, 40)) # Tree stump
draw_base.rectangle([18*32+6, 42*32+6, 19*32+10, 43*32+6], fill=(50, 55, 65)) # Anvil
# Armor Display & Weapon Crates
draw_base.rectangle([12*32, 47*32, 14*32, 52*32], fill=(90, 65, 45), outline=(50, 35, 20))
draw_base.rectangle([17*32, 49*32, 22*32, 51*32], fill=(115, 80, 50), outline=(65, 45, 25))

# --- Building D: Arcane Sanctum & Potion Apothecary ---
build_house(
    x1=58, y1=38, x2=74, y2=54,
    door_x=58, door_y=46,
    name="Arcane Sanctum",
    wall_col=(80, 70, 95),
    floor_col=(175, 165, 195)
)
# Glowing Runic Summoning Circle on Sanctum Floor
sc_x, sc_y = 66 * 32, 46 * 32
draw_base.ellipse([sc_x - 48, sc_y - 48, sc_x + 48, sc_y + 48], outline=(168, 85, 247), width=3)
draw_base.ellipse([sc_x - 32, sc_y - 32, sc_x + 32, sc_y + 32], outline=(192, 132, 252), width=2)
# Alchemy Shelves with glowing potion flasks
draw_base.rectangle([60*32, 40*32, 72*32, 41*32+16], fill=(75, 55, 90), outline=(45, 30, 60), width=2)
for px in range(61, 72):
    p_col = random.choice([(56, 189, 248), (236, 72, 153), (34, 197, 94), (234, 179, 8)])
    draw_base.ellipse([px*32+8, 40*32+10, px*32+22, 41*32+8], fill=p_col)
# Bubbling Cauldron on Pedestal
draw_base.ellipse([64*32, 49*32, 67*32, 52*32], fill=(40, 45, 55), outline=(20, 20, 25), width=2)
draw_base.ellipse([64*32+8, 49*32+8, 67*32-8, 52*32-8], fill=(147, 51, 234)) # Purple brew

# --- Sector E: Sunhaven Town Square & Central Fountain ---
print("Building Town Square Plaza & Grand Fountain...")
# Grand Stone Plaza
for py in range(36, 56):
    for px in range(32, 54):
        p_col = (185, 180, 170) if (px + py) % 2 == 0 else (198, 193, 182)
        draw_base.rectangle([px*32, py*32, (px+1)*32-1, (py+1)*32-1], fill=p_col, outline=(150, 145, 135))
        collision_grid[py][px] = 0

# Central Grand Stone Fountain (Center at X=43, Y=46)
fx1, fy1, fx2, fy2 = 41*32, 44*32, 45*32, 48*32
draw_base.ellipse([fx1-8, fy1-8, fx2+8, fy2+8], fill=(130, 135, 145), outline=(70, 75, 85), width=3)
draw_base.ellipse([fx1, fy1, fx2, fy2], fill=(56, 189, 248), outline=(14, 165, 233), width=2)
# Spouting water central pillar
draw_base.ellipse([fx1+40, fy1+40, fx2-40, fy2-40], fill=(224, 242, 254), outline=(255, 255, 255), width=2)
# Solid fountain basin
for fby in range(44, 49):
    for fbx in range(41, 46):
        collision_grid[fby][fbx] = 1

# Market Stalls in Square (North & South of Fountain)
# Food/Produce Stall
draw_base.rectangle([34*32, 38*32, 38*32, 41*32], fill=(239, 68, 68), outline=(185, 28, 28), width=2)
draw_base.text([34*32+6, 39*32], "PRODUCE", fill=(255, 255, 255))
set_solid_rect(34, 38, 38, 41)
# Weapon Merchant Stall
draw_base.rectangle([48*32, 38*32, 52*32, 41*32], fill=(59, 130, 246), outline=(29, 78, 216), width=2)
draw_base.text([48*32+6, 39*32], "ARMORY", fill=(255, 255, 255))
set_solid_rect(48, 38, 52, 41)
# Potion & Magic Curio Stall
draw_base.rectangle([34*32, 49*32, 38*32, 52*32], fill=(168, 85, 247), outline=(126, 34, 206), width=2)
draw_base.text([34*32+6, 50*32], "POTIONS", fill=(255, 255, 255))
set_solid_rect(34, 49, 38, 52)
# Rare Relic Stall
draw_base.rectangle([48*32, 49*32, 52*32, 52*32], fill=(34, 197, 94), outline=(21, 128, 61), width=2)
draw_base.text([48*32+8, 50*32], "RELICS", fill=(255, 255, 255))
set_solid_rect(48, 49, 52, 52)

# --- Sector F: Hero's Training Arena ---
print("Constructing Hero's Training Arena...")
for ay in range(64, 84):
    for ax in range(10, 28):
        # Sand/dirt ring
        draw_base.rectangle([ax*32, ay*32, (ax+1)*32-1, (ay+1)*32-1], fill=(215, 185, 135), outline=(185, 155, 105))
        collision_grid[ay][ax] = 0

# Split-rail fence around Arena with entrance at (20, 64)
for ax in range(10, 28):
    if ax != 19 and ax != 20:
        draw_base.line([ax*32, 64*32+4, (ax+1)*32, 64*32+4], fill=(120, 80, 45), width=4)
        draw_base.line([ax*32, 84*32-4, (ax+1)*32, 84*32-4], fill=(120, 80, 45), width=4)
        collision_grid[64][ax] = 1
        collision_grid[84][ax] = 1
for ay in range(64, 85):
    draw_base.line([10*32+4, ay*32, 10*32+4, (ay+1)*32], fill=(120, 80, 45), width=4)
    draw_base.line([28*32-4, ay*32, 28*32-4, (ay+1)*32], fill=(120, 80, 45), width=4)
    collision_grid[ay][10] = 1
    collision_grid[ay][28] = 1

# Training Dummies (hay posts with wooden crossbars)
for (dx, dy) in [(14, 70), (14, 76), (24, 70), (24, 76)]:
    draw_base.rectangle([dx*32+10, dy*32+6, dx*32+22, dy*32+26], fill=(190, 160, 100), outline=(120, 90, 45), width=2)
    draw_base.ellipse([dx*32+8, dy*32+2, dx*32+24, dy*32+14], fill=(150, 120, 70))
    collision_grid[dy][dx] = 1

# Archery Targets (red, white, yellow bullseye)
for (tx, ty) in [(18, 66), (21, 66)]:
    draw_base.ellipse([tx*32+4, ty*32+4, tx*32+28, ty*32+28], fill=(239, 68, 68))
    draw_base.ellipse([tx*32+8, ty*32+8, tx*32+24, ty*32+24], fill=(255, 255, 255))
    draw_base.ellipse([tx*32+12, ty*32+12, tx*32+20, ty*32+20], fill=(234, 179, 8))
    collision_grid[ty][tx] = 1

# --- Sector G: 4 Adventurer Cottages ---
print("Constructing 4 Adventurer Cottages...")
# Cottage NW
build_house(36, 64, 48, 74, door_x=42, door_y=74, name="Cottage NW", wall_col=(105, 85, 75), floor_col=(200, 170, 130))
# Cottage NE
build_house(56, 64, 68, 74, door_x=62, door_y=74, name="Cottage NE", wall_col=(105, 85, 75), floor_col=(200, 170, 130))
# Cottage SW
build_house(36, 78, 48, 88, door_x=42, door_y=78, name="Cottage SW", wall_col=(95, 85, 80), floor_col=(190, 160, 125))
# Cottage SE
build_house(56, 78, 68, 88, door_x=62, door_y=78, name="Cottage SE", wall_col=(95, 85, 80), floor_col=(190, 160, 125))

# -------------------------------------------------------------
# 5. WHISPERING FOREST (Wilderness)
# -------------------------------------------------------------
print("5. Planting Whispering Forest...")
# Scatter pine trees and oak trees in Wilderness (X=88..109)
def draw_tree(tx, ty):
    # Tree trunk (base layer, solid)
    draw_base.rectangle([tx*32+10, ty*32+16, tx*32+22, ty*32+30], fill=(100, 65, 35))
    collision_grid[ty][tx] = 1
    # Foliage Canopy (drawn on foreground so agents walk beneath canopy)
    cx, cy = tx * 32 + 16, ty * 32 + 8
    draw_fore.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(34, 120, 50, 240), outline=(20, 80, 30), width=2)
    draw_fore.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(45, 145, 60, 240))

# Forest Campfire & Ancient Shrine (X=96..104, Y=46..54)
draw_dirt_trail(96, 46, 104, 54)
# Campfire pit at (101, 51)
draw_base.ellipse([101*32+6, 51*32+6, 101*32+26, 51*32+26], fill=(80, 50, 30), outline=(40, 40, 40), width=2)
draw_base.ellipse([101*32+10, 51*32+10, 101*32+22, 51*32+22], fill=(245, 100, 20))
draw_base.ellipse([101*32+13, 51*32+13, 101*32+19, 51*32+19], fill=(255, 230, 80))
collision_grid[51][101] = 1 # Solid campfire pit

# Walkable clearing around campfire
set_walkable_rect(98, 48, 100, 52)

# Standing Runic Monoliths
for (mx, my) in [(97, 47), (103, 47), (97, 53), (103, 53)]:
    draw_base.rectangle([mx*32+8, my*32+4, mx*32+24, my*32+28], fill=(120, 125, 135), outline=(70, 75, 85), width=2)
    draw_base.line([mx*32+16, my*32+8, mx*32+16, my*32+24], fill=(56, 189, 248), width=2) # Blue glowing rune
    collision_grid[my][mx] = 1

# Scatter trees around forest (avoiding trails and shrine)
random.seed(99)
for _ in range(120):
    tx = random.randint(89, 109)
    ty = random.randint(4, 94)
    # Don't block trail
    if not (46 <= ty <= 54 and 88 <= tx <= 114):
        draw_tree(tx, ty)

# -------------------------------------------------------------
# 6. THE SHADOW CRYPTS / SUNKEN DUNGEON
# -------------------------------------------------------------
print("6. Excavating The Shadow Crypts & Dungeon Chambers...")

def build_dungeon_room(rx1, ry1, rx2, ry2, floor_color=(35, 30, 48)):
    # Floor (walkable)
    for y in range(ry1, ry2 + 1):
        for x in range(rx1, rx2 + 1):
            f_col = (floor_color[0] + (x+y)%4*3, floor_color[1] + (x+y)%4*3, floor_color[2] + (x+y)%4*3)
            draw_base.rectangle([x*32, y*32, (x+1)*32-1, (y+1)*32-1], fill=f_col, outline=(20, 16, 28))
            # Cracks in dungeon floor
            if (x * 7 + y * 13) % 17 == 0:
                draw_base.line([x*32+4, y*32+8, x*32+22, y*32+24], fill=(15, 12, 22), width=1)
            collision_grid[y][x] = 0
            
    # Solid stone walls around room
    for x in range(rx1 - 1, rx2 + 2):
        draw_base.rectangle([x*32, (ry1-1)*32, (x+1)*32-1, ry1*32-1], fill=(22, 18, 30), outline=(10, 8, 15), width=2)
        collision_grid[ry1-1][x] = 1
        draw_base.rectangle([x*32, (ry2+1)*32, (x+1)*32-1, (ry2+2)*32-1], fill=(22, 18, 30), outline=(10, 8, 15), width=2)
        collision_grid[ry2+1][x] = 1
        
    for y in range(ry1 - 1, ry2 + 2):
        draw_base.rectangle([(rx1-1)*32, y*32, rx1*32-1, (y+1)*32-1], fill=(22, 18, 30), outline=(10, 8, 15), width=2)
        collision_grid[y][rx1-1] = 1
        draw_base.rectangle([(rx2+1)*32, y*32, (rx2+2)*32-1, (y+1)*32-1], fill=(22, 18, 30), outline=(10, 8, 15), width=2)
        collision_grid[y][rx2+1] = 1

# Room 1: Crypt of the Undead (X=120..136, Y=12..32)
build_dungeon_room(120, 12, 136, 32, floor_color=(38, 32, 50))
# Ancient Stone Sarcophagi
for (sx, sy) in [(123, 16), (131, 16), (123, 26), (131, 26)]:
    draw_base.rectangle([sx*32+2, sy*32+4, (sx+2)*32-2, (sy+2)*32-4], fill=(65, 60, 75), outline=(35, 30, 45), width=2)
    # Carved cross/skull on sarcophagus lid
    draw_base.line([(sx+1)*32, sy*32+12, (sx+1)*32, (sy+2)*32-12], fill=(130, 120, 145), width=2)
    draw_base.line([sx*32+10, sy*32+24, (sx+2)*32-10, sy*32+24], fill=(130, 120, 145), width=2)
    set_solid_rect(sx, sy, sx+1, sy+1)

# Room 2: Catacombs & Treasure Vault (X=120..136, Y=40..60)
build_dungeon_room(120, 40, 136, 60, floor_color=(42, 35, 52))
# Pillars in Catacombs
for (px, py) in [(123, 44), (133, 44), (123, 56), (133, 56)]:
    draw_base.rectangle([px*32+4, py*32+4, px*32+28, py*32+28], fill=(75, 70, 85), outline=(40, 35, 50), width=2)
    collision_grid[py][px] = 1

# Gilded Treasure Chests overflowing with Gold!
for (cx, cy) in [(127, 43), (129, 43), (128, 57)]:
    # Chest body (gold-trimmed mahogany)
    draw_base.rectangle([cx*32+4, cy*32+8, cx*32+28, cy*32+26], fill=(180, 83, 9), outline=(245, 158, 11), width=2)
    draw_base.ellipse([cx*32+12, cy*32+12, cx*32+20, cy*32+20], fill=(253, 224, 71)) # Padlock
    # Gold coins scatter around chest
    for _ in range(6):
        gx = random.randint(cx*32, (cx+1)*32)
        gy = random.randint((cy+1)*32-4, (cy+1)*32+6)
        draw_base.ellipse([gx, gy, gx+4, gy+4], fill=(250, 204, 21))
    collision_grid[cy][cx] = 1

# Room 3: The Abyssal Boss Chamber (X=120..136, Y=68..88)
build_dungeon_room(120, 68, 136, 88, floor_color=(45, 20, 30))
# Giant Glowing Crimson Boss Summon Circle / Pentagram
bx_center, by_center = 128 * 32, 78 * 32
draw_base.ellipse([bx_center-70, by_center-70, bx_center+70, by_center+70], outline=(220, 38, 38), width=3)
draw_base.ellipse([bx_center-50, by_center-50, bx_center+50, by_center+50], outline=(239, 68, 68), width=2)
# Pentagram star points
points = []
for i in range(5):
    angle = i * (2 * math.pi / 5) - math.pi / 2
    points.append((bx_center + math.cos(angle)*48, by_center + math.sin(angle)*48))
for i in range(5):
    p1 = points[i]
    p2 = points[(i + 2) % 5]
    draw_base.line([p1[0], p1[1], p2[0], p2[1]], fill=(248, 113, 113), width=2)

# Demonic Boss Altar & Dragon Skull Throne
draw_base.rectangle([126*32, 70*32, 130*32, 73*32], fill=(30, 10, 15), outline=(185, 28, 28), width=3)
draw_base.text([126*32+8, 71*32+4], "ABYSSAL ALTAR", fill=(252, 165, 165))
set_solid_rect(126, 70, 130, 73)
# Flaming skull sconces
for (fx, fy) in [(124, 71), (132, 71), (124, 85), (132, 85)]:
    draw_base.ellipse([fx*32+8, fy*32+8, fx*32+24, fy*32+24], fill=(239, 68, 68))
    draw_base.ellipse([fx*32+12, fy*32+12, fx*32+20, fy*32+20], fill=(254, 240, 138))
    collision_grid[fy][fx] = 1

# Dungeon Skull Gate / Entrance Arch (X=112..118, Y=47..53)
print("Building Dungeon Skull Gate Archway...")
for gy in range(48, 53):
    for gx in range(112, 119):
        draw_base.rectangle([gx*32, gy*32, (gx+1)*32-1, (gy+1)*32-1], fill=(50, 42, 60), outline=(25, 20, 35))
        collision_grid[gy][gx] = 0

# Massive Skull Arch Keystones
draw_base.rectangle([114*32, 46*32, 116*32, 48*32], fill=(80, 70, 95), outline=(40, 35, 50), width=3)
draw_base.text([114*32+2, 46*32+6], "DUNGEON", fill=(220, 220, 240))
# Blazing purple flame braziers flanking the gate
for by in [47, 53]:
    draw_base.ellipse([114*32+6, by*32+6, 114*32+26, by*32+26], fill=(147, 51, 234), outline=(88, 28, 135), width=2)
    draw_base.ellipse([114*32+10, by*32+10, 114*32+22, by*32+22], fill=(236, 72, 153))

# Connecting Dungeon Corridors:
# Gate to Catacombs Corridor (X=118..120, Y=49..51)
set_walkable_rect(118, 49, 120, 51)
# North Corridor to Crypt of the Undead (X=126..129, Y=32..40)
for cy in range(32, 41):
    for cx in range(126, 130):
        draw_base.rectangle([cx*32, cy*32, (cx+1)*32-1, (cy+1)*32-1], fill=(36, 30, 46), outline=(18, 15, 24))
        collision_grid[cy][cx] = 0
# South Corridor to Boss Chamber (X=126..129, Y=60..68)
for cy in range(60, 69):
    for cx in range(126, 130):
        draw_base.rectangle([cx*32, cy*32, (cx+1)*32-1, (cy+1)*32-1], fill=(36, 30, 46), outline=(18, 15, 24))
        collision_grid[cy][cx] = 0

# -------------------------------------------------------------
# 7. SAVE ASSETS & GENERATE COLLISION GRID
# -------------------------------------------------------------
print("7. Exporting MMORPG world maps and collision grid...")

os.makedirs("frontend/public/assets/the_ville", exist_ok=True)
os.makedirs("backend/app/world", exist_ok=True)

out_base = "frontend/public/assets/the_ville/the_ville_base.png"
base_img.save(out_base, "PNG")
print(f"Saved: {out_base} ({base_img.size})")

out_fore = "frontend/public/assets/the_ville/the_ville_foreground.png"
fore_img.save(out_fore, "PNG")
print(f"Saved: {out_fore} ({fore_img.size})")

# Also copy to kenney_urban_base so both themes show the glorious world
base_img.save("frontend/public/assets/the_ville/kenney_urban_base.png", "PNG")
fore_img.save("frontend/public/assets/the_ville/kenney_urban_foreground.png", "PNG")

# Half-resolution preview for ultra fast web loading
base_half = base_img.resize((WIDTH_PX // 2, HEIGHT_PX // 2), Image.Resampling.LANCZOS)
base_half.save("frontend/public/assets/the_ville/the_ville_base_half.png", "PNG")

# Save collision grid
out_grid = "backend/app/world/collision_grid.json"
with open(out_grid, "w", encoding="utf-8") as f:
    json.dump(collision_grid, f)
print(f"Saved: {out_grid} (140x100 matrix)")

# Verify key MMORPG locations in collision grid
test_points = {
    "Guild Hall Walk": (44, 20),
    "Tavern Walk": (20, 22),
    "Town Square Fountain Walk": (41, 40),
    "Blacksmith Walk": (18, 48),
    "Arcane Sanctum Walk": (66, 48),
    "Hero Arena Walk": (19, 74),
    "Stone Bridge Walk": (83, 50),
    "Whispering Shrine Walk": (100, 50),
    "Dungeon Skull Gate": (115, 50),
    "Dungeon Crypt Walk": (128, 23),
    "Dungeon Catacombs Walk": (128, 51),
    "Dungeon Boss Chamber Walk": (128, 79),
}

all_walkable = True
for name, (px, py) in test_points.items():
    val = collision_grid[py][px]
    status = "WALKABLE (0)" if val == 0 else "SOLID OBSTACLE (1) - ERROR!"
    print(f"  {name} at ({px}, {py}): {status}")
    if val != 0:
        all_walkable = False

if all_walkable:
    print("SUCCESS: All MMORPG key locations are verified 100% walkable!")
else:
    print("WARNING: Some key locations were blocked!")

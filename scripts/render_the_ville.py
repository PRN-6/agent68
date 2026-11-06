import os
import json
from PIL import Image

def render_map():
    tileset_dir = "frontend/public/assets/the_ville/tilesets"
    json_path = os.path.join(tileset_dir, "the_ville_jan7.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        map_data = json.load(f)

    map_w = map_data["width"]
    map_h = map_data["height"]
    tile_w = map_data["tilewidth"]
    tile_h = map_data["tileheight"]

    print(f"Map size: {map_w}x{map_h} tiles ({map_w * tile_w}x{map_h * tile_h} pixels)")

    # Load tileset images
    tilesets = sorted(map_data["tilesets"], key=lambda ts: ts["firstgid"])
    loaded_tilesets = []
    
    for ts in tilesets:
        # Determine filename
        filename = os.path.basename(ts["image"])
        img_path = os.path.join(tileset_dir, filename)
        if not os.path.exists(img_path):
            print(f"Warning: Tileset file missing: {img_path}")
            continue
        img = Image.open(img_path).convert("RGBA")
        loaded_tilesets.append({
            "firstgid": ts["firstgid"],
            "name": ts["name"],
            "image": img,
            "cols": img.width // tile_w,
            "rows": img.height // tile_h,
            "tile_w": tile_w,
            "tile_h": tile_h
        })

    def get_tile_image(raw_gid):
        if raw_gid == 0:
            return None
        # Extract flip flags
        flipped_h = bool(raw_gid & 0x80000000)
        flipped_v = bool(raw_gid & 0x40000000)
        flipped_d = bool(raw_gid & 0x20000000)
        gid = raw_gid & 0x1FFFFFFF

        # Find tileset
        chosen_ts = None
        for i in range(len(loaded_tilesets)):
            if loaded_tilesets[i]["firstgid"] <= gid:
                if i == len(loaded_tilesets) - 1 or loaded_tilesets[i+1]["firstgid"] > gid:
                    chosen_ts = loaded_tilesets[i]
                    break

        if not chosen_ts:
            return None

        local_id = gid - chosen_ts["firstgid"]
        col = local_id % chosen_ts["cols"]
        row = local_id // chosen_ts["cols"]

        x1 = col * tile_w
        y1 = row * tile_h
        x2 = x1 + tile_w
        y2 = y1 + tile_h

        if x2 > chosen_ts["image"].width or y2 > chosen_ts["image"].height:
            return None

        tile_crop = chosen_ts["image"].crop((x1, y1, x2, y2))
        
        # Apply flips if any
        if flipped_d:
            tile_crop = tile_crop.transpose(Image.Transpose.TRANSPOSE)
        if flipped_h:
            tile_crop = tile_crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if flipped_v:
            tile_crop = tile_crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        return tile_crop

    # Base visual layers to render into the ground/building layer
    base_layers = [
        "Bottom Ground",
        "Exterior Ground",
        "Exterior Decoration L1",
        "Exterior Decoration L2",
        "Interior Ground",
        "Wall",
        "Interior Furniture L1",
        "Interior Furniture L2 "
    ]

    foreground_layers = [
        "Foreground L1",
        "Foreground L2"
    ]

    print("Compositing base world layer...")
    base_canvas = Image.new("RGBA", (map_w * tile_w, map_h * tile_h), (15, 23, 42, 255))

    for layer in map_data["layers"]:
        if layer["name"] in base_layers and "data" in layer:
            print(f"  Rendering layer: {layer['name']}")
            data = layer["data"]
            for idx, raw_gid in enumerate(data):
                if raw_gid != 0:
                    x = (idx % map_w) * tile_w
                    y = (idx // map_w) * tile_h
                    tile_img = get_tile_image(raw_gid)
                    if tile_img:
                        base_canvas.paste(tile_img, (x, y), tile_img)

    out_base = "frontend/public/assets/the_ville/the_ville_base.png"
    print(f"Saving {out_base}...")
    base_canvas.save(out_base, "PNG")

    print("Compositing foreground overlay layer...")
    fore_canvas = Image.new("RGBA", (map_w * tile_w, map_h * tile_h), (0, 0, 0, 0))
    for layer in map_data["layers"]:
        if layer["name"] in foreground_layers and "data" in layer:
            print(f"  Rendering layer: {layer['name']}")
            data = layer["data"]
            for idx, raw_gid in enumerate(data):
                if raw_gid != 0:
                    x = (idx % map_w) * tile_w
                    y = (idx // map_w) * tile_h
                    tile_img = get_tile_image(raw_gid)
                    if tile_img:
                        fore_canvas.paste(tile_img, (x, y), tile_img)

    out_fore = "frontend/public/assets/the_ville/the_ville_foreground.png"
    print(f"Saving {out_fore}...")
    fore_canvas.save(out_fore, "PNG")

    # Also save a scaled down 50% version for ultra-fast mobile/web rendering
    print("Generating half-resolution preview...")
    base_half = base_canvas.resize((map_w * tile_w // 2, map_h * tile_h // 2), Image.Resampling.LANCZOS)
    base_half.save("frontend/public/assets/the_ville/the_ville_base_half.png", "PNG")

    print("Rendering complete!")

if __name__ == "__main__":
    render_map()

import os
import urllib.request
import json
import time

BASE_REPO = "https://raw.githubusercontent.com/joonspk-research/generative_agents/main/environment/frontend_server/static_dirs/assets"

CHARACTERS = [
    "Abigail_Chen", "Adam_Smith", "Arthur_Burton", "Ayesha_Khan", "Carlos_Gomez",
    "Carmen_Ortiz", "Eddy_Lin", "Francisco_Lopez", "Giorgio_Rossi", "Hailey_Johnson",
    "Isabella_Rodriguez", "Jane_Moreno", "Jennifer_Moore", "John_Lin", "Klaus_Mueller",
    "Latoya_Williams", "Maria_Lopez", "Mei_Lin", "Rajiv_Patel", "Ryan_Park",
    "Sam_Moore", "Tamara_Taylor", "Tom_Moreno", "Wolfgang_Schulz", "Yuriko_Yamamoto"
]

TILESETS = [
    ("CuteRPG_Field_B.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Field_B.png"),
    ("CuteRPG_Field_C.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Field_C.png"),
    ("CuteRPG_Harbor_C.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Harbor_C.png"),
    ("CuteRPG_Village_B.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Village_B.png"),
    ("CuteRPG_Forest_B.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Forest_B.png"),
    ("CuteRPG_Desert_C.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Desert_C.png"),
    ("CuteRPG_Mountains_B.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Mountains_B.png"),
    ("CuteRPG_Desert_B.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Desert_B.png"),
    ("CuteRPG_Forest_C.png", f"{BASE_REPO}/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Forest_C.png"),
    ("Room_Builder_32x32.png", f"{BASE_REPO}/the_ville/visuals/map_assets/v1/Room_Builder_32x32.png"),
    ("interiors_pt1.png", f"{BASE_REPO}/the_ville/visuals/map_assets/v1/interiors_pt1.png"),
    ("interiors_pt2.png", f"{BASE_REPO}/the_ville/visuals/map_assets/v1/interiors_pt2.png"),
    ("interiors_pt3.png", f"{BASE_REPO}/the_ville/visuals/map_assets/v1/interiors_pt3.png"),
    ("interiors_pt4.png", f"{BASE_REPO}/the_ville/visuals/map_assets/v1/interiors_pt4.png"),
    ("interiors_pt5.png", f"{BASE_REPO}/the_ville/visuals/map_assets/v1/interiors_pt5.png"),
    ("blocks_1.png", f"{BASE_REPO}/the_ville/visuals/map_assets/blocks/blocks_1.png"),
]

def download_file(url: str, dest_path: str):
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as res:
            data = res.read()
            with open(dest_path, "wb") as f:
                f.write(data)
        print(f"Downloaded: {os.path.basename(dest_path)} ({len(data)} bytes)")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def main():
    dest_chars = "frontend/public/assets/characters"
    dest_profiles = "frontend/public/assets/characters/profile"
    dest_tilesets = "frontend/public/assets/the_ville/tilesets"
    dest_speech = "frontend/public/assets/speech_bubble"

    os.makedirs(dest_chars, exist_ok=True)
    os.makedirs(dest_profiles, exist_ok=True)
    os.makedirs(dest_tilesets, exist_ok=True)
    os.makedirs(dest_speech, exist_ok=True)

    print("--- 1. Downloading Characters & Sprites ---")
    download_file(f"{BASE_REPO}/characters/atlas.json", f"{dest_chars}/atlas.json")
    for name in CHARACTERS:
        download_file(f"{BASE_REPO}/characters/{name}.png", f"{dest_chars}/{name}.png")
        download_file(f"{BASE_REPO}/characters/profile/{name}.png", f"{dest_profiles}/{name}.png")

    print("\n--- 2. Downloading Speech Bubbles ---")
    for b in ["v1.png", "v2.png", "v3.png"]:
        download_file(f"{BASE_REPO}/speech_bubble/{b}", f"{dest_speech}/{b}")

    print("\n--- 3. Downloading Map Tiled JSON ---")
    download_file(f"{BASE_REPO}/the_ville/visuals/the_ville_jan7.json", f"{dest_tilesets}/the_ville_jan7.json")

    print("\n--- 4. Downloading Tilesets ---")
    for filename, url in TILESETS:
        download_file(url, f"{dest_tilesets}/{filename}")

    print("\nAll Stanford assets downloaded successfully!")

if __name__ == "__main__":
    main()


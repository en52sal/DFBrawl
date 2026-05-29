
import json
from pathlib import Path
from PIL import Image, ImageSequence

NAMESPACE = "animations"

SCRIPT_DIR = Path(__file__).parent

GIFS_DIR = SCRIPT_DIR / "gifs"
SHEETS_DIR = SCRIPT_DIR / "sheets"
PACK_ROOT = SCRIPT_DIR.parent.parent

TEXTURES_DIR = PACK_ROOT / "assets" / NAMESPACE / "textures" / "item"
MODELS_DIR = PACK_ROOT / "assets" / NAMESPACE / "models" / "item"
ITEMS_DIR = PACK_ROOT / "assets" / NAMESPACE / "items"


#


def frame_model(tex_path):
    return {
        "parent": "item/generated",
        "textures": {
            "0": tex_path
        },
        "elements": [
            {
                "from": [0, 8, 0],
                "to": [16, 8, 16],
                "rotation": {"angle": 0, "axis": "y", "origin": [0, 8, 0]},
                "faces": {
                    "north": {"uv": [0, 2, 16, 2], "texture": "#0"},
                    "east": {"uv": [0, 2, 16, 2], "texture": "#0"},
                    "south": {"uv": [0, 2, 16, 2], "texture": "#0"},
                    "west": {"uv": [0, 2, 16, 2], "texture": "#0"},
                    "up": {"uv": [0, 0, 16, 16], "texture": "#0"},
                    "down": {"uv": [0, 16, 16, 0], "texture": "#0"}
                }
            }
        ]
    }


def build_items(animations):
    model = {
        "model": {
            "type": "minecraft:select",
            "property": "minecraft:custom_model_data",
            "index": 0,
            "cases": [],
            "fallback": {
                "type": "minecraft:model",
                "model": "minecraft:item/none"
            }
        }
    }

    for anim_id, frame_count in animations.items():
        anim = {
            "when": anim_id,
            "model": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:custom_model_data",
                "index": 0,
                "entries": [
                ]
            }
        }

        for i in range(frame_count):
            anim["model"]["entries"].append({
                "threshold": i,
                "model": {
                    "type": "minecraft:model",
                    "model": f"{NAMESPACE}:item/{anim_id}_{i:04d}",
                    "tints": [
                        {
                            "type": "minecraft:custom_model_data",
                            "index": 1,
                            "default": 4294967295
                        }
                    ]
                }
            })
        
        model["model"]["cases"].append(anim)
    
    return model
    

def extract_frames(gif_path):
    frames = []
    durations = []
    with Image.open(gif_path) as img:
        for frame in ImageSequence.Iterator(img):
            frames.append(frame.convert("RGBA"))
            durations.append(frame.info.get("duration", 50))
    return frames, durations


def main():
    for d in (TEXTURES_DIR, MODELS_DIR, ITEMS_DIR):
        d.mkdir(parents=True, exist_ok=True)
    
    gif_files = sorted(GIFS_DIR.glob("*.gif"))
    if not gif_files:
        print(f"No GIFs found in {GIFS_DIR}")
        return
    
    animations = {}

    for gif_path in gif_files:
        anim_id = gif_path.stem
        print(f"Processing '{anim_id}'")

        frames, durations = extract_frames(gif_path)
        print(f"  - {len(frames)} frames, {sum(durations)}ms")
        frame_count = len(frames)

        for i, (frame_img, _) in enumerate(zip(frames, durations)):
            tex_file = TEXTURES_DIR / f"{anim_id}_{i:04d}.png"
            frame_img.save(tex_file, "PNG")

            tex_path = f"{NAMESPACE}:item/{tex_file.stem}"
            model_file = MODELS_DIR / f"{anim_id}_{i:04d}.json"
            model_file.write_text(json.dumps(frame_model(tex_path), indent=2), encoding="utf-8")

        animations[anim_id] = frame_count
    
    items_file = ITEMS_DIR / "anim.json"
    items_file.write_text(json.dumps(build_items(animations), indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()

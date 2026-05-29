from pathlib import Path
import json


NAMESPACE = "minecraft"
SCRIPT_DIR = Path(__file__).parent
PACK_ROOT = SCRIPT_DIR.parent.parent

ITEMS_FOLDER = PACK_ROOT / "assets" / NAMESPACE / "items"
ITEM_FILE = ITEMS_FOLDER / "item.json"
ITEM_BOB_FILE = ITEMS_FOLDER / "item_bob.json"

print(PACK_ROOT)


def tints(index):
    return [{
        "type": "minecraft:custom_model_data",
        "index": index,
        "default": 4294967295
    }]


def confirm_model(model):
    for key, value in model.items():
        if type(value) == dict:
            confirm_model(value)
        elif key == "model":
            confirm_file(value)

def confirm_file(path):
    namespace, _path = path.split(":")
    file_path = PACK_ROOT / "assets" / namespace / "models" / f"{_path}.json"
    if not file_path.exists():
        print(f"[WARN] Model does not exist: {path}")
    
    return path


def create_item(item):
    id = item["id"]
    case = {
        "when": id
    }

    if "icon" in item and "model" in item["icon"]:
        model = item["icon"]["model"]
        if type(model) == dict:
            confirm_model(model)

            case["model"] = model
            return case
        
        if model == "relic":
            case["model"] = {
                "type": "minecraft:condition",
                "on_false": {
                    "type": "minecraft:model",
                    "model": confirm_file(f"minecraft:item/items/{id}"),
                    "tints": tints(1)
                },
                "on_true": {
                    "type": "minecraft:model",
                    "model": confirm_file(f"minecraft:item/items/gray/{id}"),
                    "tints": tints(1)
                },
                "property": "minecraft:custom_model_data",
                "index": 1
            }
            return case
        
        if model == "gun":
            def state(state, tint_index):
                return {
                    "when": state, "model": { "type": "minecraft:model", "model": confirm_file(f"minecraft:item/items/{id}/{state}"), "tints": tints(tint_index) }
                }
            case["model"] = {
                "type": "minecraft:select", "property": "minecraft:display_context", "cases": [{
                    "when": ["thirdperson_lefthand", "thirdperson_righthand", "firstperson_lefthand", "firstperson_righthand", "ground", "none", "fixed"], "model": {
                        "type": "minecraft:select", "property": "minecraft:custom_model_data", "index": 1, "cases": [
                            state("reload", 0), state("equip", 1), state("firing", 0)
                        ], "fallback": { "type": "minecraft:model", "model": confirm_file(f"minecraft:item/items/{id}/base"), "tints": tints(0) }
                    }
                }
                ], "fallback": {
                    "type": "minecraft:condition", "property": "minecraft:custom_model_data", "index": 1,
                    "on_false": { "type": "minecraft:model", "model": confirm_file(f"minecraft:item/items/{id}/base") },
                    "on_true": { "type": "minecraft:model", "model": confirm_file(f"minecraft:item/items/{id}/gray") }
                }
            }


    if not "model" in case:
        case["model"] = {
            "type": "minecraft:model",
            "model": "minecraft:item/none"
        }
    return case



#


def create_items(items):

    models = []

    models.append({
        "type": "minecraft:select",
        "property": "minecraft:custom_model_data",
        "index": 0,
        "cases": [create_item(item) for item in items],
        "fallback": {
            "type": "minecraft:model",
            "model": "minecraft:item/none"
        }
    })
    

    root = {
        "swap_animation_scale": 0,
        "hand_animation_on_swap": False,
        "oversized_in_gui": True,
        "model": {
            "type": "minecraft:composite",
            "models": models
        }
    }

    with open(ITEM_FILE, "w") as f:
        json.dump(root, f)

    root["swap_animation_scale"] = 1
    root["hand_animation_on_swap"] = True
    with open(ITEM_BOB_FILE, "w") as f:
        json.dump(root, f)


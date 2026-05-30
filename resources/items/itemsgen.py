from pathlib import Path
import json
import itemsgenutil


NAMESPACE = "minecraft"
SCRIPT_DIR = Path(__file__).parent
PACK_ROOT = SCRIPT_DIR.parent.parent

ITEMS_FOLDER = PACK_ROOT / "assets" / NAMESPACE / "items"
ITEM_FILE = ITEMS_FOLDER / "item.json"
ITEM_BOB_FILE = ITEMS_FOLDER / "item_bob.json"

U = itemsgenutil.ItemUtility(PACK_ROOT)

print(PACK_ROOT)


def create_item(item):
    id = item["id"]
    case = {
        "when": id
    }

    def state(state, tint_index):
        return U.when(state, U.model(f"minecraft:item/items/{id}/{state}", tint_index))

    if "icon" in item and "model" in item["icon"]:
        model = item["icon"]["model"]
        if type(model) == dict:
            U.confirm_model(model)

            case["model"] = model
            return case
        
        if model == "relic":
            case["model"] = U.condition(index=1,
                on_false=U.model(f"minecraft:item/items/{id}/base", 1),
                on_true=U.model(f"minecraft:item/items/{id}/gray", 1)
            )
            return case
        
        if model == "gun":
            case["model"] = U.select(index=1, cases=[
                state("reload", 0), state("equip", 0), state("firing", 0)
            ], fallback=U.model(f"minecraft:item/items/{id}/base", 0))

        if model == "melee":
            fallback = item["icon"].get("model_fallback", "base")
            states = item["icon"].get("model_states", None)
            
            if states is not None:
                case["model"] = U.select(index=1, cases=[state(s, i+1) for i, s in enumerate(states)], fallback=U.model(f"minecraft:item/items/{id}/{fallback}", 0))
            else:
                case["model"] = U.model(f"minecraft:item/items/{id}/{fallback}", 0)

    if not "model" in case:
        case["model"] = U.model(None)

    else:
        case["model"] = U.select(property="minecraft:display_context", cases=[
            U.when(["thirdperson_lefthand", "thirdperson_righthand", "firstperson_lefthand", "firstperson_righthand", "ground", "none", "fixed"], case["model"])
        ], fallback=U.condition(
            on_false=U.model(f"minecraft:item/items/{id}/base", 5),
            on_true=U.model(f"minecraft:item/items/{id}/gray", 5)
        ))

    return case


def create_addons(models):
    addons = []

    def add(group, threshold, model):
        addons.append(U.threshold(threshold, U.model(f"minecraft:item/numbersgui/{group}/{model}", 3)))
    
    # Numbers
    order = "1 2 3 4 5 6 7 8 9 stars weight ammo cart pound".split(" ")
    for i, group in enumerate("abcde"):
        addons = []
        add(group, 0.1, "0")

        for j, model in enumerate(order):
            add(group, j + 1, model)
        
        models.append(U.range_dispatch(index=i, entries=addons))

    # Bar
    bars = []
    bars.append(U.threshold(0.1, U.model("minecraft:item/bar/0", 4)))
    bars.extend([U.threshold(i, U.model(f"minecraft:item/bar/{i}", 4)) for i in range(1, 15)])
    models.append(U.range_dispatch(
        index=5,
        entries=bars
    ))

    # Corner
    models.append(U.select(index=2, cases=[
        U.when(t, U.model(f"minecraft:item/guielements/add_{t}", 2)) for t in
        "diamond square triangle".split(" ")
    ]))

def create_background():
    return U.condition(index=1,
        on_false=U.model("minecraft:item/guielements/background_gradient", 1)
    )

def create_items(items):

    models = []

    models.append(U.select(
        cases=[create_item(item) for item in items]
    ))

    create_addons(models)
    models.append(create_background())


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


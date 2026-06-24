from pathlib import Path
import json
import itemsgenutil


NAMESPACE = "minecraft"
SCRIPT_DIR = Path(__file__).parent
PACK_ROOT = SCRIPT_DIR.parent.parent

ITEMS_FOLDER = PACK_ROOT / "assets" / NAMESPACE / "items"
ITEM_FILE = ITEMS_FOLDER / "item.json"
ITEM_BOB_FILE = ITEMS_FOLDER / "item_bob.json"

DEFAULT_FALLBACK_CONTEXT = ["thirdperson_lefthand", "thirdperson_righthand", "firstperson_lefthand", "firstperson_righthand", "ground", "none", "fixed", "head"]

U = itemsgenutil.ItemUtility(PACK_ROOT)

print(PACK_ROOT)


def create_item(item):
    id = item["id"]

    def state(state):
        return U.when(state, U.model(f"minecraft:item/items/{id}/{state}", 0))

    icon = item.get("icon", {})
    if "model" in icon and type(icon["model"]) == dict:
            U.confirm_model(icon["model"])
            return U.when(id, icon["model"])
    

    gui_fallback = U.condition(index=0,
        on_false=U.model(f"minecraft:item/items/{id}/base", 5),
        on_true=U.model(f"minecraft:item/items/{id}/gray", 5)
    )
    non_gui_fallback_id = icon.get("non_gui_fallback", "base")
    non_gui_fallback = U.model(f"minecraft:item/items/{id}/{non_gui_fallback_id}", 0)

    states_model = None
    states = icon.get("states", [])
    if states:
        states_model = U.select(index=1, cases=[state(s) for s in states], fallback=non_gui_fallback)
        non_gui_fallback = states_model
    
    display_context_model = None
    display_context = icon.get("display_context", {})
    if display_context or states or non_gui_fallback_id != "base":
        filtered_fallback_contexts = [c for c in DEFAULT_FALLBACK_CONTEXT if c not in display_context]
        
        display_cases = [U.when(c, U.model(f"minecraft:item/items/{id}/{v}", 0)) for c, v in display_context.items()]

        if filtered_fallback_contexts:
            display_cases.append(U.when(filtered_fallback_contexts, non_gui_fallback))

        if display_cases:
            display_context_model = U.select_display_context(cases=display_cases, fallback=gui_fallback)

    if display_context_model:
        model = display_context_model
    elif states_model:
        model = states_model
    else:
        model = gui_fallback
        

    return U.when(id, model)


def create_addons(models):
    addons = []

    def add(group, threshold, model):
        addons.append(U.threshold(threshold, U.model(f"minecraft:item/numbersgui/{group}/{model}", 3)))
    
    # Numbers
    order = "1 2 3 4 5 6 7 8 9 stars weight ammo cart zap timer".split(" ")
    for i, group in enumerate("abcdefghij"):
        addons = []
        add(group, 0.1, "0")

        for j, model in enumerate(order):
            add(group, j + 1, model)
        
        models.append(U.range_dispatch(index=i+1, entries=addons))

    # Bar
    bars = []
    bars.append(U.threshold(0.1, U.model("minecraft:item/bar/0", 4)))
    bars.extend([U.threshold(i, U.model(f"minecraft:item/bar/{i}", 4)) for i in range(1, 15)])
    models.append(U.range_dispatch(
        index=0,
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


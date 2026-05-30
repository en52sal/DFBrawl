
import json, os

ITEMS = [
    ["bat", "Bat", "melee", 1, 0, 13, "cooldown", 0, 0, 0, 0, 240, 5, "hold", 16, 2.4, 1, "slash", [1, 0.5, 0]],
    ["broadsword", "Broadsword", "melee", 1, 0, 20.75, "meter", 100, 1, 0.5, 0, 20, 5, "hold", 17, 2.4, 1, "slash", [0.2, 0, 0]],
    ["hammer", "Hammer", "melee", 1, 0.2, 27, "cooldown", 0, 0, 0, 0, 240, 7, "hold", 24, 2, 1.35, "slash", [0.32, 0.1, 0]],
    ["spear", "Spear", "melee", 1, 0, 17.5, "cooldown", 0, 0, 0, 0, 220, 5, "hold", 17, 3.5, 0.5, "stab", [0.2, 0, 0]],
    ["greatsword", "Greatsword", "melee", 2, 0.2, 30, "cooldown", 0, 0, 0, 0, 280, 9, "tap", 29, 0.1, 1.5, "slash", [0.32, 0.1, 0]]
]

ARGS = "id name category weight move_speed_modifier dmg resource_type resource_max resource_per resource_tick resource_tick_first cd equip_speed behaviour swing_cooldown range radius attack_type kb"


# Create a file in ./weapons/melee for each item

for item in ITEMS:
    # create folder
    if not os.path.exists(f"./weapons/melee"):
        os.makedirs(f"./weapons/melee")

    item_dict = {arg: value for arg, value in zip(ARGS.split(), item)}
    with open(f"./weapons/melee/{item[0]}.json", "w") as f:
        json.dump(item_dict, f, indent=4)
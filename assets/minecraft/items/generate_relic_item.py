import os

relics = [
    "quick_reload",
    "speed",
    "springboard",
    "taco_time",
    "superball",
    "hearty",
    "bomb",
    "big_border",
    "entrapped",
    "flaregun",
    "snack"
]


template = '''{{"when": "{when}","model": {{"type": "minecraft:condition","on_false": {{"type": "minecraft:model","model": "minecraft:item/relics/{when}","tints": [{{"type": "minecraft:custom_model_data","index": 1,"default": 4294967295}}]}},"on_true": {{"type": "minecraft:model","model": "minecraft:item/relics/gray/{when}","tints": [{{"type": "minecraft:custom_model_data","index": 1,"default": 4294967295}}]}},"property": "minecraft:custom_model_data","index": 1}}}}'''

entries = []

for r in relics:
    entries.append(template.format(
        when=r,
    ))

output = ",\n".join(entries)

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "result.json")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(output)
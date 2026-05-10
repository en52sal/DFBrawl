import os

template = '''{{"when": "{when}","model": {{"type": "minecraft:condition","on_false": {{"type": "minecraft:model","model": "minecraft:item/relics/{when}","tints": [{{"type": "minecraft:custom_model_data","index": 1,"default": 4294967295}}]}},"on_true": {{"type": "minecraft:model","model": "minecraft:item/relics/gray/{when}","tints": [{{"type": "minecraft:custom_model_data","index": 1,"default": 4294967295}}]}},"property": "minecraft:custom_model_data","index": 1}}}}'''

script_dir = os.path.dirname(os.path.abspath(__file__))

# Go to textures/item/relics
relics_dir = os.path.abspath(
    os.path.join(
        script_dir,
        "..",                 # minecraft
        "textures",
        "item",
        "relics"
    )
)

# Get all png files (no subfolders)
relics = [
    os.path.splitext(file)[0]
    for file in os.listdir(relics_dir)
    if file.endswith(".png")
]

entries = []

for r in relics:
    entries.append(template.format(
        when=r,
    ))

output = ",\n".join(entries)

output_path = os.path.join(script_dir, "result.json")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(output)

print(f"Generated {len(relics)} entries.")
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
    "entrapped"
]

template = '''{{
    "when": "{when}",
    "model": {{
        "type": "minecraft:model",
        "model": "{path}",
        "tints": [{{"type": "minecraft:custom_model_data","index": 1,"default": 4294967295}}]
    }}
}}'''

entries = []

for r in relics:
    # normal
    entries.append(template.format(
        when=r,
        path=f"minecraft:item/relics/{r}"
    ))

    # gray
    entries.append(template.format(
        when=f"gray_{r}",
        path=f"minecraft:item/relics/gray/{r}"
    ))

# Join WITHOUT wrapping in []
output = ",\n".join(entries)

# Save next to script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "result.json")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(output)

print(f"Done! Wrote paste-ready relic cases to {output_path}")
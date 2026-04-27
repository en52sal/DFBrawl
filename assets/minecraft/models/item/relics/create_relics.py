import os

# === BASE DIRECTORY (where the script is located) ===
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up 3 levels: relics -> item -> models -> minecraft
base_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

# Target texture directory
texture_dir = os.path.join(base_dir, "textures", "item", "relics")

# Output directory (same as script location)
output_dir = script_dir

# Supported texture extensions
valid_extensions = (".png", ".jpg", ".jpeg")

# === PROCESS FILES ===
if not os.path.exists(texture_dir):
    print(f"Texture directory not found: {texture_dir}")
    exit()

for file in os.listdir(texture_dir):
    if file.lower().endswith(valid_extensions):
        name = os.path.splitext(file)[0]

        json_content = f'''{{
    "parent": "minecraft:item/generated",
    "textures": {{
        "layer0": "item/relics/{name}"
    }}
}}'''

        output_path = os.path.join(output_dir, f"{name}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_content)

        print(f"Created: {output_path}")

print("Done.")
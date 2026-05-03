import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up 3 levels
base_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

# Target texture directory
texture_dir = os.path.join(base_dir, "textures", "item", "relics")

# Output directory (same as script location)
output_dir = script_dir

# Supported texture extensions
valid_extensions = (".png", ".jpg", ".jpeg")


if not os.path.exists(texture_dir):
    print(f"Texture directory not found: {texture_dir}")
    exit()

# Walk through ALL folders and files
for root, dirs, files in os.walk(texture_dir):
    # Get relative path from relics folder
    rel_path = os.path.relpath(root, texture_dir)

    # Build matching output folder
    if rel_path == ".":
        current_output_dir = output_dir
        texture_prefix = "item/relics"
    else:
        current_output_dir = os.path.join(output_dir, rel_path)
        texture_prefix = f"item/relics/{rel_path.replace(os.sep, '/')}"

    os.makedirs(current_output_dir, exist_ok=True)

    for file in files:
        if file.lower().endswith(valid_extensions):
            name = os.path.splitext(file)[0]

            json_content = f'''{{
    "parent": "minecraft:item/generated",
    "textures": {{
        "layer0": "{texture_prefix}/{name}"
    }}
}}'''

            output_path = os.path.join(current_output_dir, f"{name}.json")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_content)

            print(f"Created: {output_path}")

print("Done.")
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up 3 levels
base_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

# Base relics texture directory
texture_dir = os.path.join(base_dir, "textures", "item", "relics")

# Output directory
output_dir = script_dir

# Supported texture extensions
valid_extensions = (".png", ".jpg", ".jpeg")

# ONLY these folders
target_folders = [
    ("", "item/relics"),
    ("gray", "item/relics/gray")
]

for folder_name, texture_prefix in target_folders:

    current_texture_dir = os.path.join(texture_dir, folder_name)

    if not os.path.exists(current_texture_dir):
        print(f"Missing folder: {current_texture_dir}")
        continue

    # Match output structure
    current_output_dir = os.path.join(output_dir, folder_name)
    os.makedirs(current_output_dir, exist_ok=True)

    for file in os.listdir(current_texture_dir):

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
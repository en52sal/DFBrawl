import os


# Folder names
folders = ["a", "b", "c", "d","e"]
letters = ["0","1","2","3","4","5","6","7","8","9","stars","weight","ammo","cart","pound"]

# Use the script's directory
base_output_dir = os.path.dirname(os.path.abspath(__file__))


for folder in folders:
    folder_path = os.path.join(base_output_dir, folder)  # <-- no "number_"
    os.makedirs(folder_path, exist_ok=True)

    for i in letters:
        filename = str(i)

        json_content = f'''{{
    "parent": "minecraft:item/numbersgui/number_{folder}",
    "textures": {{
        "layer0": "item/numbersgui/{filename}"
    }}
}}'''

        output_file = os.path.join(folder_path, f"{filename}.json")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_content)

        print(f"Created: {output_file}")

print("Done.")
from pathlib import Path
import json


def main() -> None:
    main_model_folder = Path(__file__).resolve().parent
    texture_folder = main_model_folder.parent.parent.parent / "textures" / "item" / main_model_folder.name

    if not texture_folder.exists():
        raise FileNotFoundError(f"Texture folder not found: {texture_folder}")

    model_files = sorted(main_model_folder.glob("*.json"))
    texture_files = sorted(texture_folder.glob("*.png"))

    for model_file in model_files:
        if model_file.stem.startswith("armory_"):
            continue

        target_folder = main_model_folder / model_file.stem
        target_folder.mkdir(parents=True, exist_ok=True)

        for texture_file in texture_files:
            texture_name = texture_file.stem
            parent_model_name = (
                f"armory_{model_file.stem}" if texture_name.startswith("armory_") else model_file.stem
            )
            output_file = target_folder / f"{texture_name}.json"
            content = {
                "parent": f"minecraft:item/numbersgui/{parent_model_name}",
                "textures": {
                    "layer0": f"item/numbersgui/{texture_name}"
                },
            }
            output_file.write_text(json.dumps(content, indent=4) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

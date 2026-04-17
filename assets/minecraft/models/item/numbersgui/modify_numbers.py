import os
import json

# Root = where script is located
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== USER INPUT VARIABLES =====
NEW_TRANSLATION = [-7, 0.5, 10]   # X, Y, Z
NEW_SCALE = [1.05, 1.05, 1.05]  # X, Y, Z
# ==============================2
    
def update_gui_display(data):
    """
    Updates display.gui translation and scale.
    Creates missing structure if needed.
    """

    if "display" not in data:
        data["display"] = {}

    if "gui" not in data["display"]:
        data["display"]["gui"] = {}

    gui = data["display"]["gui"]

    # Preserve rotation if it exists, otherwise default
    if "rotation" not in gui:
        gui["rotation"] = [0, 0, 0]

    gui["translation"] = NEW_TRANSLATION
    gui["scale"] = NEW_SCALE


def process_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return

        update_gui_display(data)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Updated: {path}")

    except Exception as e:
        print(f"Skipped {path}: {e}")


def walk(root):
    for dirpath, _, filenames in os.walk(root):
        for file in filenames:
            if file.endswith(".json"):
                full_path = os.path.join(dirpath, file)
                process_file(full_path)


if __name__ == "__main__":
    walk(ROOT_DIR)
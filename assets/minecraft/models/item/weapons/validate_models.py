import os
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_FILE_NAME = "base.json"

TARGET_PREFIX = "item/weapons/"
INSERT_TEXT = "gray/"


def insert_gray_into_path(path_value: str) -> str:
    if not isinstance(path_value, str):
        return path_value

    if path_value.startswith(TARGET_PREFIX):
        rest = path_value[len(TARGET_PREFIX):]

        if rest.startswith(INSERT_TEXT):
            return path_value

        return TARGET_PREFIX + INSERT_TEXT + rest

    return path_value


def process_faces(faces):
    """
    FORCE tintindex = 0 on all faces with texture,
    even if it already exists.
    """
    if not isinstance(faces, dict):
        return

    for face_name, face_data in faces.items():
        if isinstance(face_data, dict):
            if "texture" in face_data:
                face_data["tintindex"] = 0


def process_model(obj):
    if isinstance(obj, dict):

        # TEXTURES
        if "textures" in obj and isinstance(obj["textures"], dict):
            for k, v in obj["textures"].items():
                obj["textures"][k] = insert_gray_into_path(v)

        # FACES
        if "elements" in obj and isinstance(obj["elements"], list):
            for element in obj["elements"]:
                if "faces" in element:
                    process_faces(element["faces"])

        for v in obj.values():
            process_model(v)

    elif isinstance(obj, list):
        for item in obj:
            process_model(item)


def process_folder(folder):
    base_path = os.path.join(folder, BASE_FILE_NAME)

    if not os.path.exists(base_path):
        return

    try:
        with open(base_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        process_model(data)

        new_path = os.path.join(folder, "gray.json")

        with open(new_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Created: {new_path}")

    except Exception as e:
        print(f"Failed in {folder}: {e}")


def walk(root):
    for dirpath, _, _ in os.walk(root):
        process_folder(dirpath)


if __name__ == "__main__":
    walk(ROOT_DIR)
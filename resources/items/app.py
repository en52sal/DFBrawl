
import json
from pathlib import Path
import base64
import gzip
import websocket
import re
import itemsgen
import textparser

SCRIPT_DIR = Path(__file__).parent
MAX_LINE_LENGTH = 40
META_FILE = SCRIPT_DIR / "meta.json"

META = json.load(META_FILE.open())

def create_template(name):
    return {
        "blocks": [
            {
                "id": "block",
                "block": "func",
                "args": {
                    "items": [
                        {
                            "item": {
                                "id": "pn_el",
                                "data": {
                                    "name": "data",
                                    "type": "var",
                                    "plural": False,
                                    "optional": False
                                }
                            },
                            "slot": 0
                        },
                        {
                            "item": {
                                "id": "bl_tag",
                                "data": {
                                    "option": "False",
                                    "tag": "Is Hidden",
                                    "action": "dynamic",
                                    "block": "func"
                                }
                            },
                            "slot": 26
                        }
                    ]
                },
                "data": name
            }
        ]
    }

def template_set_var(action, varname, items):
    result = {
        "id": "block",
        "block": "set_var",
        "args": {
            "items": [
                {
                    "item": {
                        "id": "var",
                        "data": {
                            "name": varname,
                            "scope": "line"
                        }
                    },
                    "slot": 0
                }
            ]
        },
        "action": action
    }

    for i, item in enumerate(items):
        item["slot"] = i + 1
        result["args"]["items"].append(item)
    
    return result

def template_item_string(value):
    return {
        "item": {
            "id": "txt",
            "data": {
                "name": value
            }
        },
        "slot": -1
    }

def template_item_item(item):
    return {
        "item": {
            "id": "item",
            "data": {
                "item": item
            }
        },
        "slot": 1
    }

def get_description_lines(data, desc):
    desc = re.sub(r"\$(\w+)\$", lambda m: str(data.get(m.group(1), f"${m.group(1)}$")), desc)

    return textparser.parse_lore(f"<{META['colors']['desc']}>{desc}")

def create_item(data):
    name = data.get("name", "Unnamed Item")
    components =  {
        "custom_name": textparser.parse_name(f"<{META['colors']['name']}>{name}")
    }

    if "icon" in data:
        icon = data["icon"]

        components["item_model"] = "minecraft:item"
        components["custom_model_data"] = {
            "strings": [data["id"]]
        }

        # SHORTCUTS
        if "item_model" in icon:
            components["item_model"] = icon["item_model"]
        
        # LORE
        lore = []
        if "description" in icon:
            desc = icon["description"]
            lore.extend(get_description_lines(data, desc))
            lore.append({"text": ""})
        
        if "actions" in icon:
            for key, action in icon["actions"].items():
                line = {"bold": 0, "color": "white", "extra": [
                        {
                            "font": "minecraft:controls", "translate": "key", "with": [
                                {
                                    "extra": [
                                        {
                                            "keybind": f"key.{key}"
                                        }
                                    ], "text": ""
                                }
                            ]
                        },
                        " ",
                        {
                            "color": "gray", "extra": [
                                "- ",
                                {
                                    "color": "white", "text": action["title"]
                                }
                            ], "text": ""
                        }
                    ], "text": "", "italic": False
                }
                lore.append(line)

                if "desc" in action:
                    lore.extend(get_description_lines(data, action["desc"]))
                lore.append({"text": ""})
        
        if lore:
            lore.pop()
            components["lore"] = lore


        # OVERRIDE
        if "components" in icon:
            components.update(icon["components"])

    # print(json.dumps(components))
    return json.dumps({
        "components": components,
        "count": 1,
        "id": "minecraft:stone"
    })

def encode_string(str): 
    compressed = gzip.compress(str.encode())
    encoded = base64.b64encode(compressed).decode()
    return encoded


def main():
    folders = [f for f in SCRIPT_DIR.iterdir() if f.is_dir()]
    json_files = []
    for folder in folders:
        json_files.extend(list(folder.glob("*.json")))


    items = []

    for json_file in json_files:
        item = json.load(json_file.open())
        item["id"] = json_file.stem
        items.append(item)

    args = []
    template = create_template("ITEM:data")
    
    itemsgen.create_items(items)

    for item in items:
        value_item = create_item(item)
        if "icon" in item:
            del item["icon"]
        
        item_data = encode_string(json.dumps(item))
        value_str = template_item_string(item_data)

        args.append(value_str)
        args.append(template_item_item(value_item))
    
    
    first = True
    while args:
        # take 26 items at a time
        segment = args[:26]
        if first:
            template["blocks"].append(template_set_var("CreateList", "data", segment))
            first = False
        else:
            template["blocks"].append(template_set_var("AppendValue", "data", segment))
        
        args = args[26:]

    b64 = encode_string(json.dumps(template))
    payload = {
        "type": "template",
        "source": "The Great Importer",
        "data": b64
    }

    print(f"Sending {len(items)} items...")

    wsUrl = "ws://localhost:31321"
    ws = websocket.create_connection(wsUrl)
    ws.send(json.dumps(payload))
    ws.close()


if __name__ == "__main__":
    main()


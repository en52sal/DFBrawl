
import json
from pathlib import Path
import base64
import gzip
import websocket
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
    return textparser.parse_lore(f"<{META['colors']['desc']}>{desc}", data)


def parse_display_text(data, text, mode="name"):
    if mode == "lore":
        return textparser.parse_lore(text, data)
    return textparser.parse_name(text, data)


def normalize_text_component(data, value):
    if isinstance(value, list):
        return [normalize_text_component(data, item) for item in value]
    if not isinstance(value, dict):
        return value

    if "minimessage" in value:
        return textparser.parse_name(value["minimessage"], data)
    if "minimessage_lore" in value:
        return textparser.parse_lore(value["minimessage_lore"], data)
    if "dynamic_minimessage" in value:
        return textparser.compile_dynamic_name(value["dynamic_minimessage"], data)
    if "dynamic_minimessage_lore" in value:
        return textparser.compile_dynamic_lore(value["dynamic_minimessage_lore"], data)

    return {key: normalize_text_component(data, child) for key, child in value.items()}


def normalize_icon_components(data, components):
    normalized = {}
    for key, value in components.items():
        if key in {"custom_name", "item_name"} and isinstance(value, str):
            normalized[key] = parse_display_text(data, value)
        elif key == "lore" and isinstance(value, str):
            normalized[key] = parse_display_text(data, value, mode="lore")
        elif key == "lore" and isinstance(value, list):
            lore = []
            for line in value:
                if isinstance(line, str):
                    lore.extend(parse_display_text(data, line, mode="lore"))
                else:
                    lore.append(normalize_text_component(data, line))
            normalized[key] = lore
        else:
            normalized[key] = normalize_text_component(data, value)
    return normalized


def _append_dynamic_lore_entry(entries, data, source, section, key=None):
    if source is None:
        return
    if isinstance(source, str):
        entry = textparser.compile_dynamic_lore(source, data)
    elif isinstance(source, dict):
        raw = source.get("lore", source.get("text", source.get("minimessage", "")))
        entry = textparser.compile_dynamic_lore(raw, data)
        entry.update({k: v for k, v in source.items() if k not in {"lore", "text", "minimessage"}})
    elif isinstance(source, list):
        for item in source:
            _append_dynamic_lore_entry(entries, data, item, section, key)
        return
    else:
        return

    entry["section"] = section
    if key is not None:
        entry["key"] = key
    entries.append(entry)


def collect_dynamic_lore(data):
    icon = data.get("icon", {})
    entries = []

    _append_dynamic_lore_entry(entries, data, icon.get("dynamic_description"), "description")
    _append_dynamic_lore_entry(entries, data, icon.get("dynamic_lore"), "lore")

    for key, action in icon.get("actions", {}).items():
        if isinstance(action, dict):
            _append_dynamic_lore_entry(entries, data, action.get("dynamic_desc"), "action_desc", key)
            if "dynamic_title" in action:
                entries.append({
                    **textparser.compile_dynamic_name(action["dynamic_title"], data),
                    "section": "action_title",
                    "key": key,
                })

    _append_dynamic_lore_entry(entries, data, icon.get("dynamic_ability_boost"), "ability_boost")

    return entries

def create_item(data):
    name = data.get("name", "Unnamed Item")
    components =  {
        "custom_name": textparser.parse_name(f"<{META['colors']['name']}>{name}", data)
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
                        {"font": "minecraft:controls", "translate": "key", "with": [
                            {"extra": [{"keybind": f"key.{key}"}], "text": ""}
                        ]},
                        " ",
                        {"color": "gray", "extra": [
                            "- ",
                            textparser.parse_name("<white>" + action["title"], data)
                        ], "text": ""}
                    ], "text": "", "italic": False
                }
                if "prefix" in action:
                    line["extra"].insert(0, textparser.parse_name(action["prefix"], data))
                
                lore.append(line)

                if "desc" in action:
                    lore.extend(get_description_lines(data, action["desc"]))
            lore.append({"text": ""})

        if "ability_boost" in icon:
            lore.append(textparser.parse_name("$$boost$ <white>Ability Boost", data))
            lore.extend(get_description_lines(data, icon["ability_boost"]))
            lore.append({"text": ""})
        
        if lore:
            lore.pop()
            components["lore"] = lore


        # OVERRIDE
        if "components" in icon:
            components.update(normalize_icon_components(data, icon["components"]))

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

def apply_presets(item):
    presets = META.get("presets", {})
    if not presets:
        return
    
    for key, value in item.items():
        if type(value) != str:
            continue
        if value[0] != "$":
            continue
        if value[1:] in presets:
            item[key] = presets[value[1:]][key]
    
    if "icon" in item:
        apply_presets(item["icon"])

def main():
    folders = [f for f in SCRIPT_DIR.iterdir() if f.is_dir()]
    json_files = []
    for folder in folders:
        json_files.extend(list(folder.rglob("*.json")))


    items = []

    for json_file in json_files:
        item = json.load(json_file.open())
        item["id"] = json_file.stem
        items.append(item)

    args = []
    template = create_template("ITEM:data")
    
    for item in items:
        apply_presets(item)

    itemsgen.create_items(items)

    for item in items:

        value_item = create_item(item)
        dynamic_lore = collect_dynamic_lore(item)
        if dynamic_lore:
            item["dynamic_lore"] = dynamic_lore
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


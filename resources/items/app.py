
import json
from pathlib import Path
import base64
import gzip
import websocket
from df.main import Block, Item, Template
import itemsgen
import textparser

SCRIPT_DIR = Path(__file__).parent
MAX_LINE_LENGTH = 40
META_FILE = SCRIPT_DIR / "meta.json"
MAX_SET_VARS_PER_TEMPLATE = 4
SET_VAR_ITEM_LIMIT = 26

META = json.load(META_FILE.open())

def create_template(name):
    template = Template(name)
    template.add_parameter("data", "var")
    template.blocks[0].add_tag(Item("bl_tag", {
        "option": "False",
        "tag": "Is Hidden",
        "action": "dynamic",
        "block": "func"
    }))
    return template

def template_set_var(action, varname, items):
    block = Block("set_var", None, action)
    block.add_item(Item.Variable(varname))
    for item in items:
        block.add_item(item)
    return block

def template_item_string(value):
    return Item.String(value)

def template_item_item(item):
    return Item("item", {"item": item})


def template_call_func(name, varname="data"):
    return Block("call_func", name, None, [Item.Variable(varname)])


def chunked(values, size):
    for i in range(0, len(values), size):
        yield values[i:i + size]


def create_set_var_blocks(args):
    blocks = []
    first = True
    for segment in chunked(args, SET_VAR_ITEM_LIMIT):
        if first:
            blocks.append(template_set_var("CreateList", "data", segment))
            first = False
        else:
            blocks.append(template_set_var("AppendValue", "data", segment))
    return blocks


def create_templates_from_args(args, name="ITEM:data", max_set_vars=MAX_SET_VARS_PER_TEMPLATE):
    set_var_blocks = create_set_var_blocks(args)
    templates = []
    block_groups = list(chunked(set_var_blocks, max_set_vars))
    template_names = [
        name if i == 0 else f"{name}.{i + 1}"
        for i in range(len(block_groups))
    ]

    for i, blocks in enumerate(block_groups):
        template = create_template(template_names[i])
        for block in blocks:
            template.add_block(block)
        if i < len(block_groups) - 1:
            call_func = template_call_func(template_names[i + 1])
            template.add_block(call_func)
        templates.append(template)
    return templates


def send_templates(templates):
    wsUrl = "ws://localhost:31321"
    ws = websocket.create_connection(wsUrl)
    try:
        for template in templates:
            payload = {
                "type": "template",
                "source": "The Great Importer",
                "data": encode_string(template.to_json())
            }
            ws.send(json.dumps(payload))
    finally:
        ws.close()

def get_description_lines(data, desc):
    lines, _slots = get_description_lore(data, desc)
    return lines


def get_description_lore(data, desc, start_index=0, section="description", key=None):
    desc_color = META["colors"]["desc"]
    text = "\n".join(f"<{desc_color}>{line}" for line in desc.split("\n"))
    return textparser.parse_lore_with_dynamic_slots(
        text,
        data,
        start_index=start_index,
        section=section,
        key=key,
    )


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


def _dynamic_lore_line_entries(slots):
    grouped = {}
    for slot in slots:
        group_key = (slot.get("section"), slot.get("key"), slot["lore_index"])
        if group_key not in grouped:
            grouped[group_key] = [
                slot["lore_index"] + 1,
                slot["line_parts"],
            ]
    return list(grouped.values())


def collect_dynamic_lore(data):
    icon = data.get("icon", {})
    entries = _dynamic_lore_line_entries(data.get("_dynamic_lore_slots", []))

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
        dynamic_lore_slots = []
        if "description" in icon:
            desc = icon["description"]
            lines, slots = get_description_lore(data, desc, len(lore), "description")
            lore.extend(lines)
            dynamic_lore_slots.extend(slots)
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
                    lines, slots = get_description_lore(data, action["desc"], len(lore), "action_desc", key)
                    lore.extend(lines)
                    dynamic_lore_slots.extend(slots)
            lore.append({"text": ""})

        if "ability_boost" in icon:
            lore.append(textparser.parse_name("$$boost$ <white>Ability Boost", data))
            lines, slots = get_description_lore(data, icon["ability_boost"], len(lore), "ability_boost")
            lore.extend(lines)
            dynamic_lore_slots.extend(slots)
            lore.append({"text": ""})
        
        if lore:
            lore.pop()
            components["lore"] = lore


        # OVERRIDE
        if "components" in icon:
            components.update(normalize_icon_components(data, icon["components"]))

        if dynamic_lore_slots:
            data["_dynamic_lore_slots"] = dynamic_lore_slots
        else:
            data.pop("_dynamic_lore_slots", None)

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
    
    for item in items:
        apply_presets(item)

    itemsgen.create_items(items)

    for item in items:

        value_item = create_item(item)
        dynamic_lore = collect_dynamic_lore(item)
        if dynamic_lore:
            item["dynamic_lore"] = dynamic_lore
        item.pop("_dynamic_lore_slots", None)
        if "icon" in item:
            del item["icon"]
        
        item_data = encode_string(json.dumps(item))
        value_str = template_item_string(item_data)

        args.append(value_str)
        args.append(template_item_item(value_item))
    templates = create_templates_from_args(args)

    print(
        f"Sending {len(items)} items across {len(templates)} templates "
        f"with max {MAX_SET_VARS_PER_TEMPLATE} set vars each..."
    )

    send_templates(templates)


if __name__ == "__main__":
    main()

import json, gzip, base64
import websocket


def encode_string(str): 
    compressed = gzip.compress(str.encode())
    encoded = base64.b64encode(compressed).decode()
    return encoded

class Item():
    @staticmethod
    def Variable(name: str, scope: str = "line"):
        return Item("var", {
            "name": name,
            "scope": scope
        })
    
    def String(value: str, encode: bool = False):
        if encode:
            value = encode_string(value)
        
        return Item("txt", {
            "name": value
        })

    def __init__(self, id: str, data = {}):
        self.id = id
        self.data = data


class Block():

    @staticmethod
    def create_list(var_name: str, items: list[Item]):
        block = Block("set_var", None, "CreateList")
        block.add_item(Item.Variable(var_name))
        for item in items:
            block.add_item(item)
        return block

    def __init__(self, block: str, data: str, action: str, args = None, tags = None):
        self.block = block
        self.data = data
        self.action = action
        self.args: list[Item] = args or []
        self.tags: list[Item] = tags or []
    
    def add_item(self, item: Item):
        self.args.append(item)
    
    def add_tag(self, tag: Item):
        self.tags.append(tag)

    def to_json(self):
        v = {
            "id": "block",
            "block": self.block,
            "args": {
                "items": []
            }
        }

        slot = 0
        for item in self.args:
            v["args"]["items"].append({
                "slot": slot,
                "item": {
                    "id": item.id,
                    "data": item.data
                }
            })
            slot += 1
        slot = 26
        for tag in self.tags:
            v["args"]["items"].append({
                "slot": slot,
                "item": {
                    "id": tag.id,
                    "data": tag.data
                }
            })
            slot -= 1

        if self.data is not None:
            v["data"] = self.data
        if self.action is not None:
            v["action"] = self.action
        
        return v
        


class Template():
    def __init__(self, name):
        self.blocks: list[Block] = []
        self.add_block(Block("func", name, None))

    def add_parameter(self, name, type, plural = False, optional = False):
        self.blocks[0].add_item(Item("pn_el", {
            "name": name,
            "type": type,
            "plural": plural,
            "optional": optional
        }))

    def add_block(self, block):
        self.blocks.append(block)

    def to_json(self):
        return json.dumps({
            "blocks": [block.to_json() for block in self.blocks]
        })
    
    def to_millomod(self):
        b64 = encode_string(self.to_json())
        payload = {
            "type": "template",
            "source": "PyDf",
            "data": b64
        }

        wsUrl = "ws://localhost:31321"
        ws = websocket.create_connection(wsUrl)
        ws.send(json.dumps(payload))
        ws.close()
        






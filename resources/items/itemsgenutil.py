
class ItemUtility:
    def __init__(self, root):
        self.root = root
        pass

    
    def confirm_model(self, model):
        for key, value in model.items():
            if type(value) == dict:
                self.confirm_model(value)
            elif key == "model":
                self.confirm_file(value)

    def confirm_file(self, path):
        namespace, _path = path.split(":")
        file_path = self.root / "assets" / namespace / "models" / f"{_path}.json"
        if not file_path.exists():
            print(f"[WARN] Model does not exist: {path}")
        
        return path


    def select(self, index=0, cases=[], fallback=None, property="minecraft:custom_model_data"):
        if fallback is None:
            fallback = {
                "type": "minecraft:model",
                "model": "minecraft:item/none"
            }
        
        return {
            "type": "minecraft:select",
            "property": property,
            "index": index,
            "cases": cases,
            "fallback": fallback
        }

    def model(self, model=None, tints:str|int|list ="auto"):
        if model is None:
            return {
                "type": "minecraft:model",
                "model": "minecraft:item/none"
            }
            
        result = {
            "type": "minecraft:model",
            "model": self.confirm_file(model)
        }

        if tints == "auto":
            result["tints"] = self.tints(0)
        elif type(tints) == list:
            result["tints"] = tints
        elif type(tints) == int:
            result["tints"] = self.tints(tints)

        return result

    def when(self, condition, model):
        return {
            "when": condition,
            "model": model
        }
        
    
    def threshold(self, threshold, model):
        return {
            "threshold": threshold,
            "model": model
        }

    def tints(self, index):
        return [{
            "type": "minecraft:custom_model_data",
            "index": index,
            "default": 4294967295
        }]

    def range_dispatch(self, property="minecraft:custom_model_data", index=0, entries=[], fallback=None):
        if fallback is None:
            fallback = {
                "type": "minecraft:model",
                "model": "minecraft:item/none"
            }
        
        return {
            "type": "minecraft:range_dispatch",
            "property": property,
            "index": index,
            "entries": entries,
            "fallback": fallback
        }

    def condition(self, property="minecraft:custom_model_data", index=0, on_true=None, on_false=None):
        if on_true is None:
            on_true = {
                "type": "minecraft:model",
                "model": "minecraft:item/none"
            }
        if on_false is None:
            on_false = {
                "type": "minecraft:model",
                "model": "minecraft:item/none"
            }
        
        return {
            "type": "minecraft:condition",
            "property": property,
            "index": index,
            "on_true": on_true,
            "on_false": on_false
        }
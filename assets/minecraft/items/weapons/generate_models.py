import os

# === YOUR BASE JSON TEMPLATE ===
template = r'''
{
  "model": {
    "type": "minecraft:select",
    "property": "minecraft:display_context",
    "cases": [
      {
        "when": ["head", "gui", "ground", "fixed", "on_shelf"],
        "model": {
          "type": "minecraft:select",
          "property": "minecraft:custom_model_data",
          "cases": [
            {
              "when": ["gui"],
              "model": {
                "type": "minecraft:composite",
                "models": [
                  {
                    "type": "minecraft:model",
                    "model": "minecraft:item/weapons/tgun/base"
                  },
                  {
                    "type": "minecraft:model",
                    "model": "minecraft:item/background_gradient",
                    "tints": [
                      {
                        "type": "minecraft:custom_model_data",
                        "index": 0,
                        "default": 0
                      }
                    ]
                  }
                ]
              }
            }
          ],
          "fallback": {
            "type": "minecraft:model",
            "model": "minecraft:item/weapons/tgun/base"
          }
        }
      }
    ],
    "fallback": {
      "type": "minecraft:select",
      "property": "minecraft:custom_model_data",
      "cases": [
        {
          "when": ["gui"],
          "model": {
            "type": "minecraft:composite",
            "models": [
              {
                "type": "minecraft:model",
                "model": "minecraft:item/weapons/tgun/base"
              },
              {
                "type": "minecraft:model",
                "model": "minecraft:item/background_gradient",
                "tints": [
                  {
                    "type": "minecraft:custom_model_data",
                    "index": 0,
                    "default": 0
                  }
                ]
              }
            ]
          }
        },
        {
          "when": ["reload"],
          "model": {
            "type": "minecraft:model",
            "model": "minecraft:item/weapons/tgun/reload"
          }
        },
        {
          "when": ["equip"],
          "model": {
            "type": "minecraft:model",
            "model": "minecraft:item/weapons/tgun/equip"
          }
        },
        {
          "when": ["firing"],
          "model": {
            "type": "minecraft:model",
            "model": "minecraft:item/weapons/tgun/firing"
          }
        }
      ],
      "fallback": {
        "type": "minecraft:model",
        "model": "minecraft:item/weapons/tgun/base"
      }
    }
  },
  "swap_animation_scale": 0,
  "hand_animation_on_swap": false
}
'''

# === INPUT YOUR NAMES HERE ===
names = [
    "betty",
    "chopper",
    "grand",
    "nailer",
    "rattle",
    "shredder",
    "striker",
    "surge",
    "vector",
    "verdant",
    "winger"
]

# === GENERATE FILES ===
output_dir = os.path.dirname(os.path.abspath(__file__))

for name in names:
    new_content = template.replace("tgun", name)

    file_path = os.path.join(output_dir, f"{name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Created: {file_path}")
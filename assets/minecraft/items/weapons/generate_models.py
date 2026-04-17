import os

template = r'''
{
  "model": {
    "type": "minecraft:select",
    "property": "minecraft:custom_model_data",
    "cases": [
      {
        "when": ["gray"],
        "model": {
          "type": "minecraft:composite",
          "models": [
            {
              "type": "minecraft:model",
              "model": "minecraft:item/weapons/tgun/gray",
              "tints": [
                {
                  "type": "minecraft:custom_model_data",
                  "index": 1,
                  "default": 16777215
                }
              ]
            },

            {NUMBERS_BLOCK},

            {
              "type": "minecraft:model",
              "model": "minecraft:item/background_gradient",
              "tints": [
                {
                  "type": "minecraft:custom_model_data",
                  "index": 0,
                  "default": 16777215
                }
              ]
            }
          ]
        }
      }
    ],

    "fallback": {
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

                    {NUMBERS_BLOCK},

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
              "type": "minecraft:composite",
              "models": [
                {
                  "type": "minecraft:model",
                  "model": "minecraft:item/weapons/tgun/base"
                },

                {NUMBERS_BLOCK}

              ]
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

                {NUMBERS_BLOCK},

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
    }
  },
  "swap_animation_scale": 0,
  "hand_animation_on_swap": false
}
'''

# === NUMBERS BLOCK ===
numbers_block = '''
{
  "type": "minecraft:range_dispatch",
  "property": "minecraft:custom_model_data",
  "index": 0,
  "entries": [
    {ENTRIES1}
  ],
  "fallback": { "type": "minecraft:model", "model": "minecraft:item/air" }
},
{
  "type": "minecraft:range_dispatch",
  "property": "minecraft:custom_model_data",
  "index": 1,
  "entries": [
    {ENTRIES2}
  ],
  "fallback": { "type": "minecraft:model", "model": "minecraft:item/air" }
},
{
  "type": "minecraft:range_dispatch",
  "property": "minecraft:custom_model_data",
  "index": 2,
  "entries": [
    {ENTRIES3}
  ],
  "fallback": { "type": "minecraft:model", "model": "minecraft:item/air" }
}
'''

# === ENTRY GENERATION ===
entries1 = ",\n".join([
    f'''{{"threshold": {i}.1, "model": {{"type":"minecraft:model","model":"minecraft:item/numbersgui/a/{i}"}}}}'''
    for i in range(10)
])

entries2 = ",\n".join([
    f'''{{"threshold": {i}.1, "model": {{"type":"minecraft:model","model":"minecraft:item/numbersgui/b/{i}"}}}}'''
    for i in range(10)
])

entries3 = ",\n".join([
    f'''{{"threshold": {i}.1, "model": {{"type":"minecraft:model","model":"minecraft:item/numbersgui/c/{i}"}}}}'''
    for i in range(10)
])

numbers_block = numbers_block.replace("{ENTRIES1}", entries1)
numbers_block = numbers_block.replace("{ENTRIES2}", entries2)
numbers_block = numbers_block.replace("{ENTRIES3}", entries3)

template = template.replace("{NUMBERS_BLOCK}", numbers_block)

# === INPUT YOUR NAMES HERE ===
names = [
    "betty","chopper","grand","nailer","rattle",
    "shredder","striker","surge","vector","verdant","winger"
]

output_dir = os.path.dirname(os.path.abspath(__file__))

for name in names:
    new_content = template.replace("tgun", name)

    file_path = os.path.join(output_dir, f"{name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Created: {file_path}")
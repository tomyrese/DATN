import json
with open('scripts/world_pads_v2.json') as f:
    pads = json.load(f)

print("OLED pads:", pads["OLED"])


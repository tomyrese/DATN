import json

with open('scripts/parsed_world_pads.json', 'r', encoding='utf-8') as f:
    fps = json.load(f)

print("=== J_OLED ===")
for pnum, p in fps['J_OLED']['pads'].items():
    print(f"Pad {pnum}: ({p['wx']}, {p['wy']}) net={p['net_name']}")

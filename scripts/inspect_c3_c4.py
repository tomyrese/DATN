import json

with open('scripts/parsed_world_pads.json', 'r', encoding='utf-8') as f:
    fps = json.load(f)

for ref in ['C3', 'C4']:
    print(f"=== {ref} ===")
    for pnum, p in fps[ref]['pads'].items():
        print(f"Pad {pnum}: ({p['wx']}, {p['wy']}) net={p['net_name']}")

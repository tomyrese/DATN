import json

with open('scripts/world_pads.json', 'r') as f:
    comps = json.load(f)

for comp, pads in comps.items():
    print(f"\nComponent: {comp} ({len(pads)} pads)")
    pad_list = sorted(pads.items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0]))
    for p_num, pos in pad_list[:3]:
        print(f"  Pad {p_num}: ({pos['x']}, {pos['y']})")
    if len(pad_list) > 3:
        print(f"  ... (total {len(pad_list)} pads)")


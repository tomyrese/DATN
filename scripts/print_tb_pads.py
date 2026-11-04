import json

data = json.load(open('scripts/world_pads_actual.json', 'r', encoding='utf-8'))

for ref in ['LEFT', 'RIGHT']:
    print(f"=== Footprint {ref} ===")
    pads = data[ref]['pads']
    for p in sorted(pads.keys(), key=lambda x: int(x)):
        info = pads[p]
        print(f"  Pad {p:>2}: ({info['world'][0]:.2f}, {info['world'][1]:.2f}) -> {info['net']}")


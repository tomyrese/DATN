import json

data = json.load(open('scripts/world_pads_actual.json', 'r', encoding='utf-8'))

for ref in ['HC_SR04_1', 'R1', 'R2', 'HC_SR04_2', 'R3', 'R4']:
    print(f"=== {ref} ===")
    pads = data[ref]['pads']
    for p in sorted(pads.keys(), key=lambda x: int(x)):
        info = pads[p]
        print(f"  Pad {p:>2}: ({info['world'][0]:.2f}, {info['world'][1]:.2f}) -> {info['net']}")


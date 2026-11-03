import json

with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for comp in ['TCRT5000', 'OLED', 'Rasp_PI4']:
    print(f"\n=== {comp} ===")
    for p, val in data[comp].items():
        print(f"  Pad {p:>2}: ({val['x']:>8.4f}, {val['y']:>8.4f}) | net={val['net']}")

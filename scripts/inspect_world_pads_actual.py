import json

with open('scripts/world_pads_actual.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for ref in ['LEFT', 'RIGHT', 'Rasp_PI4', 'U_TB1', 'U_TB2', 'U_PI4']:
    if ref in data:
        print(f"=== {ref} ===")
        for p, info in sorted(data[ref]['pads'].items(), key=lambda x: int(x[0])):
            print(f"  Pad {int(p):2}: world={info['world']} net={info.get('net')}")

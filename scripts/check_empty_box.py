import json

with open('scripts/world_pads.json', 'r') as f:
    data = json.load(f)

for comp, pads in data.items():
    for pad_num, pos in pads.items():
        x, y = pos['x'], pos['y']
        if 112 <= x <= 135 and 64 <= y <= 93:
            print(f"{comp} Pad {pad_num} at ({x}, {y})")

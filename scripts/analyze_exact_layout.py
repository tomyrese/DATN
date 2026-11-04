import json

with open('scripts/world_pads.json', 'r') as f:
    data = json.load(f)

print("=== COMPONENT LOCATIONS & BOUNDS ===")
for comp, pads in sorted(data.items()):
    xs = [p['x'] for p in pads.values()]
    ys = [p['y'] for p in pads.values()]
    print(f"{comp:<12}: X=[{min(xs):.2f}, {max(xs):.2f}] Y=[{min(ys):.2f}, {max(ys):.2f}] (pins: {len(pads)})")


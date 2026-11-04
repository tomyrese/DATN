import json

# Check the true world pads of Rasp_PI4
data = json.load(open('scripts/true_world_pads.json', 'r', encoding='utf-8'))
pi = data['Rasp_PI4']
print(f"Rasp_PI4 footprint position: {pi['fp_pos']}")

# Let's see the coordinates of Pin 1, 2, 3, 4, 5, 6, and 33, 35, 37, 39, 40
for p in [1, 2, 3, 4, 5, 6, 32, 33, 35, 36, 37, 38, 39, 40]:
    pinfo = pi['pads'][str(p)]
    print(f"  Pin {p:>2}: world=({pinfo['world'][0]:>7.2f}, {pinfo['world'][1]:>7.2f})")


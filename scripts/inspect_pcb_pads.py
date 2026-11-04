import re
import math
import json

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split('(footprint ')
world_pads = {}

for part in parts[1:]:
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', part)
    if not ref_m:
        ref_m = re.search(r'\(fp_text\s+reference\s+"([^"]+)"', part)
    ref = ref_m.group(1) if ref_m else 'Unknown'
    
    at_m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', part)
    fp_x, fp_y, fp_rot = float(at_m.group(1)), float(at_m.group(2)), float(at_m.group(3) or 0)
    
    world_pads[ref] = {'pos': (fp_x, fp_y), 'rot': fp_rot, 'pads': {}}
    
    pad_matches = re.finditer(r'\(pad\s+"([^"]+)"\s+[^\s]+\s+[^\s]+\s+\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+(?:\d+\s+)?"([^"]+)"\)', part)
    for pm in pad_matches:
        p_num, px, py, net_name = pm.group(1), float(pm.group(2)), float(pm.group(3)), pm.group(4)
        rad = math.radians(fp_rot)
        wx = round(fp_x + px * math.cos(rad) - py * math.sin(rad), 4)
        wy = round(fp_y + px * math.sin(rad) + py * math.cos(rad), 4)
        world_pads[ref]['pads'][p_num] = {'world': (wx, wy), 'net': net_name}

with open('scripts/world_pads_actual.json', 'w', encoding='utf-8') as f:
    json.dump(world_pads, f, indent=2)

print("Saved world_pads_actual.json successfully!")
for ref, data in sorted(world_pads.items()):
    print(f"=== {ref} (at {data['pos']}, rot={data['rot']}) - {len(data['pads'])} pads ===")
    for p_num in sorted(data['pads'].keys(), key=lambda x: int(x) if x.isdigit() else x):
        p = data['pads'][p_num]
        print(f"  Pad {p_num:>2}: world {p['world']} | Net: {p['net']}")

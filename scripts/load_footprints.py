import math
import os
import re
import json

def parse_footprint(fp_path):
    with open(fp_path, 'r', encoding='utf-8') as f:
        text = f.read()
    pads = {}
    matches = re.finditer(r'\(pad\s+"([^"]+)"\s+(thru_hole|smd)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)\s*\(size\s+([-\d.]+)\s+([-\d.]+)\)\s*\(drill\s+([-\d.]+)\)?', text)
    for m in matches:
        p_num = m.group(1)
        p_type = m.group(2)
        shape = m.group(3)
        lx = float(m.group(4))
        ly = float(m.group(5))
        lrot = float(m.group(6)) if m.group(6) else 0.0
        sx = float(m.group(7))
        sy = float(m.group(8))
        drill = float(m.group(9)) if m.group(9) else 0.8
        pads[p_num] = {
            'lx': lx, 'ly': ly, 'lrot': lrot,
            'sx': sx, 'sy': sy, 'drill': drill,
            'shape': shape, 'type': p_type
        }
    return pads

# Test all footprints in libraries
lib_dir = 'libraries/robot_electronics.pretty'
fps = {}
for fname in os.listdir(lib_dir):
    if fname.endswith('.kicad_mod'):
        fp_name = fname[:-10]
        fps[fp_name] = parse_footprint(os.path.join(lib_dir, fname))

print(f"Loaded {len(fps)} footprints:")
for name, p_dict in sorted(fps.items()):
    print(f"  {name:40}: {len(p_dict)} pads")


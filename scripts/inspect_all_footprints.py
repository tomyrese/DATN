import os
import re

lib_dir = 'libraries/robot_electronics.pretty'
for fname in os.listdir(lib_dir):
    if not fname.endswith('.kicad_mod'):
        continue
    fpath = os.path.join(lib_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    pads = re.findall(r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\b.*?\((?:size|drill)\s+([-\d.]+)', content)
    print(f"Footprint: {fname} (Pads: {len(pads)})")
    for p in pads[:8]:
        print(f"   Pad {p[0]}: ({p[3]}, {p[4]}) shape={p[2]} size={p[5]}")
    if len(pads) > 8:
        print(f"   ... and {len(pads)-8} more pads")


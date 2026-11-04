with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
fps = re.findall(r'\(footprint "([^"]+)"\s+\(layer "[^"]+"\)\s+\(uuid "[^"]+"\)\s+\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?\).*?\(property "Reference" "([^"]+)"', text, re.DOTALL)
print(f"Total footprints in .bak: {len(fps)}")
for fp, x, y, rot, ref in sorted(fps, key=lambda item: item[4]):
    rot_str = rot if rot else '0'
    print(f"  {ref:10} at ({float(x):7.2f}, {float(y):7.2f}, rot={float(rot_str):5.1f}) fp={fp.split(':')[-1]}")


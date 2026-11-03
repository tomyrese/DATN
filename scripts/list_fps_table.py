with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
fps = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(at\s+([-\d\.]+)\s+([-\d\.]+)', bak)
print(f"Total footprints: {len(fps)}")
for fp, ref, x, y in fps:
    print(f"{ref:12} ({x:>7}, {y:>7}) - {fp}")

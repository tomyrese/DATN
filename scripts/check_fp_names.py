with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
fps = re.findall(r'\(footprint\s+"([^"]+)"', text)
print(fps)
m = re.search(r'\(footprint\s+"[^"]*TB6612[^"]*"[\s\S]*?\n\t\)', text)
if m:
    print("Found TB6612 footprint, first 500 chars:")
    print(m.group(0)[:500])

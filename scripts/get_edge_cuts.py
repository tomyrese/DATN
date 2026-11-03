with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
edges = re.findall(r'\(gr_line\s+\(start\s+[-\d\.]+\s+[-\d\.]+\)[\s\S]*?\(layer\s+"Edge\.Cuts"\)[\s\S]*?\n\t\)', text)
print(f"Total Edge.Cuts elements: {len(edges)}")
for e in edges:
    print(e)

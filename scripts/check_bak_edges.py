with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
edges = re.findall(r'\(gr_line\s+\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)[\s\S]*?\(layer\s+"Edge\.Cuts"\)', text)
print(f"Edge cuts in bak: {len(edges)}")
for e in edges:
    print(f"  ({float(e[0]):.2f}, {float(e[1]):.2f}) -> ({float(e[2]):.2f}, {float(e[3]):.2f})")


with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re
edges = re.findall(r'\(gr_line\s+\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(end\s+([-\d\.]+)\s+([-\d\.]+)\)\s+.*?\(layer\s+"Edge\.Cuts"\)', pcb)
print("Edge cuts segments:")
xs = []
ys = []
for e in edges:
    print(f"  ({e[0]}, {e[1]}) -> ({e[2]}, {e[3]})")
    xs.extend([float(e[0]), float(e[2])])
    ys.extend([float(e[1]), float(e[3])])

print(f"Board Bounding Box: X in [{min(xs):.2f}, {max(xs):.2f}], Y in [{min(ys):.2f}, {max(ys):.2f}]")


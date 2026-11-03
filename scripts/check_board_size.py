import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

edges = re.findall(r'\(gr_line\s+\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(end\s+([-\d\.]+)\s+([-\d\.]+)\)[\s\S]*?\(layer\s+"Edge\.Cuts"\)', text)
print("Board outlines (Edge.Cuts):")
for e in edges:
    print(e)

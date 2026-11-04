import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'\(segment\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)\s+\(width\s+([-\d.]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+(?:\d+\s+)?"([^"]+)"\)', text):
    net = m.group(7)
    if any(k in net for k in ['M1', 'M2', 'M3', 'M4']):
        print(f"{net:8}: ({float(m.group(1)):.2f}, {float(m.group(2)):.2f}) -> ({float(m.group(3)):.2f}, {float(m.group(4)):.2f})")


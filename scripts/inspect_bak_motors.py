import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    txt = f.read()

segs = re.findall(r'\(segment\s+\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(width\s+[\d\.\-]+\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+"([^"]+)"\)', txt)
for x1, y1, x2, y2, l, net in segs:
    if net in ['/M1_A', '/M1_B', '/M2_B', '/M2_A']:
        print(f"{net:8s} ({float(x1):6.2f}, {float(y1):6.2f}) -> ({float(x2):6.2f}, {float(y2):6.2f})")


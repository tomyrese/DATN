import sys
import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find segments with net "/VM_MOTOR" or "/M1_A"
segs = re.findall(r'\(segment\s+\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(end\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(width\s+([-\d\.]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+(\d+)\)', text)
# Let's find net numbers for VM_MOTOR, M1_A, PWMA_L
net_defs = re.findall(r'\(net\s+(\d+)\s+"([^"]+)"\)', text)
net_map = {num: name for num, name in net_defs}

for s in segs[:20]:
    sx, sy, ex, ey, w, layer, net = s
    n_name = net_map.get(net, net)
    if any(k in n_name for k in ['PWMA_L', 'M1_A', 'VM_MOTOR', 'AIN2_L']):
        print(f"Seg net={n_name}: ({sx}, {sy}) -> ({ex}, {ey})")

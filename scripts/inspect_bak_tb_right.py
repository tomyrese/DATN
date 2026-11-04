import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

segs = re.findall(r'\(segment\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)\s+\(width\s+([-\d.]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+"?([^"\s)]+)"?\)', text)

print(f"Total segs in bak: {len(segs)}")
for s in segs:
    net = s[6]
    if any(k in net for k in ['PWMA_R', 'AIN1_R', 'AIN2_R', 'M3', 'M4', 'ECHO_R', 'US2']):
        print(f"Net {net:<18} ({s[0]}, {s[1]}) -> ({s[2]}, {s[3]}) layer: {s[5]}")


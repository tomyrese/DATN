import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

nets = re.findall(r'\(net\s+(\d+)\s+"([^"]+)"\)', text)
print(f"Total nets defined: {len(nets)}")
for n in nets:
    print(f"Net {n[0]:>2}: {n[1]}")

import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Look for labels and wires near U_PI4 (at 105.41 180.34)
labels = re.findall(r'\(label\s+"([^"]+)"\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)', text)
for l in labels:
    print(l)


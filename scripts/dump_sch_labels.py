with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find all labels near U_PI4
# Let's see all labels with their positions
labels = re.findall(r'\(label\s+"([^"]+)"\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', text)
print(f"Total labels in schematic: {len(labels)}")
for l in labels:
    print(l)

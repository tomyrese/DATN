# Let's inspect the symbols and wires in Pi4_Robot_Carrier_1Layer.kicad_sch
with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find all wire connections
wires = re.findall(r'\(wire\s+\(pts\s+\(xy\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(xy\s+([\d\.-]+)\s+([\d\.-]+)\)\)', text)
print(f"Total wires in sch: {len(wires)}")

# Find all labels and their locations
labels = re.findall(r'\(label\s+"([^"]+)"\s+\(at\s+([\d\.-]+)\s+([\d\.-]+)', text)
print(f"Total labels in sch: {len(labels)}")
for l in sorted(labels, key=lambda x: x[0]):
    print(f"  {l[0]:<15} at ({float(l[1]):.2f}, {float(l[2]):.2f})")


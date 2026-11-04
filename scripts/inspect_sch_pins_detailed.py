import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Find symbol U_PI4
m = re.search(r'\(symbol\s+[\s\S]*?\(property\s+"Reference"\s+"U_PI4"[\s\S]*?\n\t\)', text)
if m:
    sym = m.group(0)
    print("Found U_PI4 in schematic:")
    # print pins
    pins = re.findall(r'\(pin\s+"([^"]+)"\s+\(uuid\s+"[^"]+"\)\)', sym)
    print(f"Pins: {len(pins)}")

# Let's see wires and labels connected to U_PI4
wires = re.findall(r'\(wire\s+\(pts\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\)', text)
labels = re.findall(r'\(label\s+"([^"]+)"\s+\(at\s+([-\d.]+)\s+([-\d.]+)', text)

# Find labels at X near 53.34 or 157.48 (the Pi 4 header area in sch)
pi_labels = [l for l in labels if abs(float(l[1]) - 53.34) < 1 or abs(float(l[1]) - 157.48) < 1]
print(f"Labels attached to Pi header: {len(pi_labels)}")
for l in sorted(pi_labels, key=lambda x: float(x[2])):
    print(f"  Y = {float(l[2]):<6.2f} (X={float(l[1]):<6.2f}): {l[0]}")


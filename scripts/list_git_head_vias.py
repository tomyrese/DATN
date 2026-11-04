import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all vias
vias = re.findall(r'\(via\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)\s+\(size\s+([-\d.]+)\)\s+\(drill\s+([-\d.]+)\)\s+\(layers\s+"([^"]+)"\s+"([^"]+)"\)\s+\(net\s+(\d+)\)', text)
print(f"Total vias in Git HEAD: {len(vias)}")

# Find all net numbers
net_map = {}
for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]+)"\)', text):
    net_map[m.group(1)] = m.group(2)

print("\nVias in Git HEAD:")
for x, y, sz, dr, l1, l2, net_id in vias:
    net_name = net_map.get(net_id, f"Net_{net_id}")
    print(f"  Via at ({float(x):.2f}, {float(y):.2f}) size={sz} drill={dr} | Net: {net_name}")


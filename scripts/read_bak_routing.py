import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

# Get segments by net
segs_by_net = {}
for m in re.finditer(r'\(segment\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)\s+\(width\s+([-\d.]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+(?:\d+\s+)?"([^"]+)"\)', text):
    p1 = (float(m.group(1)), float(m.group(2)))
    p2 = (float(m.group(3)), float(m.group(4)))
    w = float(m.group(5))
    layer = m.group(6)
    net_name = m.group(7)
    if net_name not in segs_by_net:
        segs_by_net[net_name] = []
    segs_by_net[net_name].append((p1, p2, w, layer))

print(f"Total nets with segments in .bak: {len(segs_by_net)}")
for net_name, segs in sorted(segs_by_net.items()):
    print(f"\nNet {net_name} ({len(segs)} segments):")
    for p1, p2, w, layer in segs:
        print(f"  {p1} -> {p2} (w={w}, {layer})")

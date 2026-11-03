with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
segments = re.findall(r'\(segment[\s\S]*?\)', bak)
print(f"Total segments in bak: {len(segments)}")

# Filter segments by net
nets_in_bak = {}
for s in segments:
    net_m = re.search(r'\(net\s+"([^"]+)"', s)
    if net_m:
        n = net_m.group(1)
        nets_in_bak[n] = nets_in_bak.get(n, 0) + 1

for n, count in sorted(nets_in_bak.items()):
    print(f"{n:20}: {count} segments")

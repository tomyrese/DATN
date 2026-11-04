with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
segments = re.findall(r'\(segment[\s\S]*?\n\t\)', bak)

nets = {}
for s in segments:
    m = re.search(r'\(net\s+"([^"]+)"\)', s)
    if m:
        n = m.group(1)
        if n not in nets: nets[n] = []
        nets[n].append(s)

print("Nets and segment count in bak:")
for n, segs in sorted(nets.items()):
    print(f"{n:20}: {len(segs)} segments")


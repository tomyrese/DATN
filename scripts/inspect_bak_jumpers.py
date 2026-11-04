with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
vias = re.findall(r'\(via[\s\S]*?\)', bak)
print(f"Total vias in bak: {len(vias)}")
for v in vias:
    net_m = re.search(r'\(net\s+"([^"]+)"', v)
    at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)', v)
    print(f"Via: {at_m.groups() if at_m else None} - net={net_m.group(1) if net_m else None}")

silks = re.findall(r'\(gr_text\s+"JMP[\s\S]*?\)', bak)
print(f"\nJumpers in bak: {len(silks)}")
for s in silks:
    print(s[:100])


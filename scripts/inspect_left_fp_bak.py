with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

pos = bak.find('(property "Reference" "LEFT"')
fp_start = bak.rfind('(footprint', 0, pos)
fp_end = bak.find('\n\t)', pos)

fp = bak[fp_start:fp_end+3]

import re
at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', fp)
print("Footprint placement:", at_m.groups())

for p in [1, 2, 7, 8, 9, 10, 15, 16]:
    pad_m = re.search(rf'\(pad\s+"{p}"[\s\S]*?\(at\s+([-\d\.]+)\s+([-\d\.]+)', fp)
    net_m = re.search(rf'\(pad\s+"{p}"[\s\S]*?\(net\s+"([^"]+)"', fp)
    print(f"pad {p}: at={pad_m.groups() if pad_m else None}, net={net_m.group(1) if net_m else None}")


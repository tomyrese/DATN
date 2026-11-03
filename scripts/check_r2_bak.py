with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
segs = re.findall(r'\(segment\s+\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(end\s+([-\d\.]+)\s+([-\d\.]+)\)[\s\S]*?\(net\s+"([^"]+)"\)', text)
r2_segs = [s for s in segs if any(abs(float(p) - 89.18) < 0.1 for p in [s[0], s[2]]) or any(abs(float(p) - 72.44) < 0.1 for p in [s[1], s[3]])]
for s in r2_segs:
    print(s)

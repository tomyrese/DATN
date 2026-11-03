with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
segs = re.findall(r'\(segment\s+\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(end\s+([-\d\.]+)\s+([-\d\.]+)\)[\s\S]*?\(net\s+"([^"]+)"\)', text)
top_segs = [s for s in segs if float(s[1]) < 55 or float(s[3]) < 55]
for s in top_segs:
    print(s)

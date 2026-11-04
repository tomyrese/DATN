with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
segs = re.findall(r'\(segment\s+\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(end\s+([-\d\.]+)\s+([-\d\.]+)\)[\s\S]*?\(net\s+"/\+5V_PWR"\)', text)
print(f"Total +5V segments in bak: {len(segs)}")
for s in segs:
    print(s)


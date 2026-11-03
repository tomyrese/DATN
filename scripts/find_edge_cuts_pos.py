with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
matches = [m.start() for m in re.finditer(r'Edge\.Cuts', bak)]
for m in matches:
    print(f"Edge.Cuts match at {m}")

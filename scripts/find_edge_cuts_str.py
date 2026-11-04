with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re
matches = [m.start() for m in re.finditer(r'Edge\.Cuts', pcb)]
for m in matches:
    print(pcb[m-100:m+200])


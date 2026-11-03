with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
lines = re.findall(r'\(gr_line[\s\S]*?Edge\.Cuts[\s\S]*?\n\t\)', text)
for l in lines:
    print(l)

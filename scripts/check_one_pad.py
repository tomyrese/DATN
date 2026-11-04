with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'\(pad\s+"1"\s+thru_hole[\s\S]*?\n\t\t\)', text)
if m:
    print(m.group(0))


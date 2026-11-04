with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'\(footprint\s+"[^"]+"[\s\S]*?reference "LEFT"[\s\S]*?\n\t\)', text)
if m:
    for line in m.group(0).split('\n'):
        if '(pad ' in line:
            print(line)


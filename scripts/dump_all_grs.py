with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
grs = re.findall(r'\(gr_\w+[\s\S]*?\n\t\)', text)
for i, g in enumerate(grs):
    l_m = re.search(r'\(layer\s+"([^"]+)"\)', g)
    l = l_m.group(1) if l_m else "?"
    print(f"{i+1}: layer={l} | {g.splitlines()[0]} ... {g.splitlines()[1]}")

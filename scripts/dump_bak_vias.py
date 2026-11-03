with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
vias = [m.start() for m in re.finditer(r'\(via', bak)]
for idx, vpos in enumerate(vias):
    vend = bak.find(')', vpos)
    # find full via
    lvl = 0
    i = vpos
    while i < len(bak):
        if bak[i] == '(': lvl += 1
        elif bak[i] == ')':
            lvl -= 1
            if lvl == 0:
                print(f"Via {idx+1}:")
                print(bak[vpos:i+1])
                break
        i += 1

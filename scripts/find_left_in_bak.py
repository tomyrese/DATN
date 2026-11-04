with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
pos = bak.find('reference "LEFT"')
print(bak[pos-200:pos+1500])


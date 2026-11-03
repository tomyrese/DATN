with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# find wires or labels connected near R3 at (279.4, 88.9) and R4 at (294.64, 101.6)
lines = [l for l in text.split('\n') if any(k in l for k in ['279.4', '294.64', 'R3', 'R4', 'ECHO'])]
for l in lines[:30]:
    print(l)

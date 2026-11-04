with open('Pi4_Robot_Carrier_1Layer-drc.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
lines = text.splitlines()
for i, line in enumerate(lines):
    if any(k in line for k in ['[shorting_items]', '[tracks_crossing]', '[copper_edge_clearance]']):
        print("\n".join(lines[i:i+6]))
        print('-'*30)


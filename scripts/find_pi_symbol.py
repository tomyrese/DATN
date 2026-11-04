with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'\(symbol\s+[^)]*Rasp_PI4[\s\S]*?\n\t\)', text)
if m:
    print(m.group(0)[:1000])
else:
    # search for Rasp_PI4 anywhere
    for block in text.split('(symbol '):
        if 'Rasp_PI4' in block:
            print("Found block:")
            print(block[:1000])
            break


with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
matches = [m.start() for m in re.finditer(r'LEFT', bak)]
print(f"Found {len(matches)} occurrences of LEFT in bak")
for m in matches[:5]:
    print(bak[m-50:m+50])
    print('---')

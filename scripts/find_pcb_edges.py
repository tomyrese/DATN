with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'Edge\.Cuts', text)]
print(f"Total occurrences of Edge.Cuts in Pi4_Robot_Carrier_1Layer.kicad_pcb: {len(matches)}")
for idx in matches:
    print(repr(text[max(0, idx-40):min(len(text), idx+60)]))

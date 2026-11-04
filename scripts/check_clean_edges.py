with open('Pi4_Robot_Carrier_1Layer_clean.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'Edge\.Cuts', text)]
print(f"Occurrences of Edge.Cuts in clean: {len(matches)}")


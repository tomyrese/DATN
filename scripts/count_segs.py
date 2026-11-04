with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
segs = re.findall(r'\(segment\b', text)
vias = re.findall(r'\(via\b', text)
print(f"Total segment tokens: {len(segs)}")
print(f"Total via tokens: {len(vias)}")


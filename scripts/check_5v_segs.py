with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
segs = re.findall(r'\(segment[\s\S]*?\/\+5V_PWR[\s\S]*?\n\t\)', text)
print(f"Total +5V_PWR segments: {len(segs)}")
for s in segs:
    print(s)

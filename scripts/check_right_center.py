with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
for m in re.finditer(r'\(footprint\s+"Module_TB6612FNG_Breakout"[\s\S]*?\n\t\)', text):
    fp = m.group(0)
    if 'RIGHT' in fp:
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', fp)
        print("RIGHT center:", m_at.group(0))

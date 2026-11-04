with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
for m in re.finditer(r'\(footprint\s+"PinSocket_2x20_P2.54mm_Vertical"[\s\S]*?\n\t\)', text):
    fp = m.group(0)
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', fp)
    print("Rasp_PI4 center:", m_at.group(0))


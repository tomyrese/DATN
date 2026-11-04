with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'\(pad\s+"1"\s+[\s\S]*?\n\t\)', text)
if m:
    print(m.group(0))


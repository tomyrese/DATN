with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
tags = set(re.findall(r'\((\w+)\b', text))
print("Tags in .bak:")
print(sorted(list(tags)))


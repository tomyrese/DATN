with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
refs = re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', text)
print("Refs in bak:", refs)


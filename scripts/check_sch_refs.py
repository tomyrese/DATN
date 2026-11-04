import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

refs = re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', text)
print('References in schematic:', sorted(set(refs)))


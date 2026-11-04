with open('Pi4_Robot_Carrier_1Layer_clean.kicad_pcb', 'r', encoding='utf-8') as f:
    clean = f.read()

import re
matches = re.findall(r'.{0,50}\(embedded_fonts.{0,50}', clean)
print("Near embedded_fonts in clean:")
for m in matches:
    print(repr(m))


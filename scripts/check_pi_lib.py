with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find lib_symbols -> Raspberry_Pi_4_40Pin
lib_pi = re.search(r'\(symbol\s+"robot_electronics:Raspberry_Pi_4_40Pin"[\s\S]*?\n\t\t\)', text)
if lib_pi:
    print(lib_pi.group(0)[:2500])

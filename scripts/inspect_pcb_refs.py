with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'\(footprint "([^"]+)"\s+\(layer "[^"]+"\)\s+\(uuid "[^"]+"\)\s+\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?\).*?\(property "Reference" "([^"]+)"', text, re.DOTALL)
for fp, x, y, rot, ref in matches:
    if ref in ['U_PI4', 'Rasp_PI4', 'U_TB1', 'LEFT', 'U_TB2', 'RIGHT', 'J_OLED', 'OLED']:
        print(f"{ref:10} at ({x}, {y}, rot={rot}) fp={fp}")


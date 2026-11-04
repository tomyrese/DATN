with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find symbols near X=274.32 and X=380.65
syms = re.findall(r'\(symbol\s+[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.-]+)\s+([\d\.-]+)[\s\S]*?\n\s+\)', text)
for ref, x, y in syms:
    if any(m in ref for m in ['M', 'J', 'MOTOR']):
        print(f"Ref {ref} at ({x}, {y})")


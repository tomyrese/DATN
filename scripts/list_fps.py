import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    txt = f.read()

fps = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"', txt)
for fp, x, y, rot, ref in fps:
    print(f'{ref:12s} at ({float(x):6.2f}, {float(y):6.2f}) rot={rot}  fp={fp}')

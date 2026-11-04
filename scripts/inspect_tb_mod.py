with open('libraries/robot_electronics.pretty/Module_TB6612FNG_Breakout.kicad_mod', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pads = re.findall(r'\(pad\s+"(\w+)"\s+(\w+)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\b.*?\((?:size|drill)\s+([-\d.]+)', text)
print(f"Pads in Module_TB6612FNG_Breakout: {len(pads)}")
for p in pads:
    print(p)


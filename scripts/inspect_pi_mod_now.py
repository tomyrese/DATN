with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'\(pad\s+"(\d+)"\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)', text)
for p in matches[:4]:
    print(f"Pad {p[0]}: ({p[1]}, {p[2]})")
for p in matches[-4:]:
    print(f"Pad {p[0]}: ({p[1]}, {p[2]})")


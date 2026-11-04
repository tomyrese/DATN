with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pads = re.findall(r'\(pad\s+"(\d+)"\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)', text)
for p in sorted(pads, key=lambda x: int(x[0])):
    print(f"Pad {int(p[0]):2}: ({float(p[1]):6.2f}, {float(p[2]):6.2f})")


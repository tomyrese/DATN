with open('robot_electronics.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

import re
matches = [m.start() for m in re.finditer(r'Reference"\s+"R[1-4]"', sch)]
for m in matches:
    print(sch[m-100:m+200])


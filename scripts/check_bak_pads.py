with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
left_pos = bak.find('(footprint "robot_electronics:Module_TB6612FNG_Breakout"')
fp = bak[left_pos:left_pos+3000]

# find at of fp
at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', fp)
print("LEFT footprint at:", at_m.groups())

# find pads 1 and 9 in fp
for p in [1, 8, 9, 16]:
    pad_m = re.search(rf'\(pad\s+"{p}"[\s\S]*?\(at\s+([-\d\.]+)\s+([-\d\.]+)', fp)
    print(f"pad {p}:", pad_m.groups())


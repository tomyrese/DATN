import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

def replace_rot(ref, old_rot, new_rot, s):
    pattern = rf'(\(footprint\s+"[^"]+".*?\(at\s+[-\d.]+\s+[-\d.]+)\s+{old_rot}(\).*?\(property\s+"Reference"\s+"{ref}")'
    match = re.search(pattern, s, re.DOTALL)
    if match:
        s = s[:match.start()] + match.group(1) + f" {new_rot}" + match.group(2) + s[match.end():]
        print(f"Updated {ref} rotation: {old_rot} -> {new_rot}")
    else:
        print(f"Could not find {ref} with rot {old_rot}")
    return s

for r in ['U_TB1', 'U_TB2', 'R_JMP1', 'R_JMP2', 'R_JMP3']:
    text = replace_rot(r, 270, 90, text)

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated rotations to 90.")

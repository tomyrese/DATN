with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'r', encoding='utf-8') as f:
    text = f.read()

import re

def repl_pad(m):
    num = m.group(1)
    ptype = m.group(2)
    shape = m.group(3)
    x = float(m.group(4))
    y = float(m.group(5))
    rest = m.group(6)
    new_x = -x
    return f'(pad "{num}" {ptype} {shape} (at {new_x:.2f} {y:.2f}) {rest}'

new_text = re.sub(r'\(pad\s+"(\d+)"\s+(\w+)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)\s+([^\)]+\)\))', repl_pad, text)

# Also mirror silk text "1" and "40"
def repl_text(m):
    ttype = m.group(1)
    val = m.group(2)
    x = float(m.group(3))
    y = float(m.group(4))
    rot = m.group(5)
    rest = m.group(6)
    new_x = -x
    rot_str = f" {rot}" if rot else ""
    return f'(fp_text {ttype} "{val}" (at {new_x:.2f} {y:.2f}{rot_str}) {rest}'

new_text = re.sub(r'\(fp_text\s+(\w+)\s+"(1|40)"\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)\s+([^\)]+\)\))', repl_text, new_text)

with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Updated PinSocket_2x20_P2.54mm_Vertical.kicad_mod!")

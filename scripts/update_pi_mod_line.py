with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
import re
for line in lines:
    m = re.search(r'\(pad\s+"(\d+)"\s+(thru_hole|smd)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)', line)
    if m:
        num = m.group(1)
        ptype = m.group(2)
        shape = m.group(3)
        x = float(m.group(4))
        y = float(m.group(5))
        new_x = -x
        new_line = re.sub(r'\(at\s+[-\d.]+\s+[-\d.]+\)', f'(at {new_x:.2f} {y:.2f})', line)
        new_lines.append(new_line)
    elif 'user "1"' in line or 'user "40"' in line:
        m2 = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', line)
        if m2:
            x = float(m2.group(1))
            y = float(m2.group(2))
            rot = m2.group(3)
            new_x = -x
            rot_str = f" {rot}" if rot else ""
            new_line = re.sub(r'\(at\s+[-\d.]+\s+[-\d.]+(?:\s+[-\d.]+)?\)', f'(at {new_x:.2f} {y:.2f}{rot_str})', line)
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Updated line-by-line successfully!")


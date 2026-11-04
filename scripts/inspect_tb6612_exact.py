with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find Module_TB6612FNG_Breakout
matches = list(re.finditer(r'\(footprint\s+"Module_TB6612FNG_Breakout"[\s\S]*?\n\t\)', text))
print(f"Found {len(matches)} TB6612 footprints")

for i, m in enumerate(matches):
    block = m.group(0)
    ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block).group(1)
    at_m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', block)
    print(f"\n--- {ref} at ({at_m.group(1)}, {at_m.group(2)}, rot={at_m.group(3)}) ---")
    pads = re.findall(r'\(pad\s+"([^"]+)"\s+thru_hole\s+[^\s]+\s+\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+"([^"]+)"\)', block)
    for p_num, lx, ly, net in pads:
        print(f"  Pad {p_num:>2}: local ({float(lx):.2f}, {float(ly):.2f}) | Net: {net}")


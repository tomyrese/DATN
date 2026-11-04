import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find LEFT footprint
idx = text.find('(property "Reference" "LEFT"')
fp_left = text[idx-200:idx+4000]

print("Pads of LEFT directly from file:")
for m in re.finditer(r'\(pad\s+"([^"]+)"\s+thru_hole\s+[^\s]+\s+\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)[\s\S]*?\(net\s+"([^"]+)"\)', fp_left):
    p_num, lx, ly, net = m.groups()
    print(f"  Pad {p_num:>2}: local at ({float(lx):.2f}, {float(ly):.2f}) -> net={net}")


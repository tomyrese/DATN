with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
seg = re.search(r'\(segment[\s\S]*?\n\t\)', text)
if seg:
    print("Sample segment from bak:")
    print(seg.group(0))

via = re.search(r'\(via[\s\S]*?\n\t\)', text)
if via:
    print("Sample via from bak:")
    print(via.group(0))

nets = re.findall(r'\(net\s+(\d+)\s+"([^"]+)"\)', text)
print(f"Total nets defined: {len(nets)}")
for n in nets[:10]:
    print(n)

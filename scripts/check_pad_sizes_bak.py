with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re

# Find unique pad sizes
pad_sizes = re.findall(r'\(pad\s+"[^"]+"\s+thru_hole\s+\w+\s+\(at\s+[-\d\.]+\s+[-\d\.]+(?:\s+[-\d\.]+)?\)\s+\(size\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(drill\s+([-\d\.]+)\)', pcb)
unique_sizes = set(pad_sizes)
print("Unique pad sizes in bak:")
for s in unique_sizes:
    print(f"  Size: ({s[0]}, {s[1]}), Drill: {s[2]}")


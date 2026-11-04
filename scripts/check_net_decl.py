import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

# Look for (net declarations
lines = [l for l in text.splitlines() if l.strip().startswith('(net ')]
print(f"Total (net lines: {len(lines)}")
for l in lines[:10]:
    print(" ", repr(l))


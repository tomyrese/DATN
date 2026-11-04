import json
import re

# Read Pi4_Robot_Carrier_1Layer.kicad_pcb
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb_text = f.read()

# Extract all nets
net_defs = re.findall(r'\(net\s+(\d+)\s+"([^"]+)"\)', pcb_text)
print(f"Total net definitions: {len(net_defs)}")
for num, name in net_defs:
    if name and not name.startswith("unconnected-"):
        print(f"  Net {num:>2}: {name}")


with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    curr = f.read()

import re
bak_edges = re.findall(r'\(gr_[a-z]+[\s\S]*?Edge\.Cuts[\s\S]*?\n\t\)', bak)
curr_edges = re.findall(r'\(gr_[a-z]+[\s\S]*?Edge\.Cuts[\s\S]*?\n\t\)', curr)

print(f"Bak edges count: {len(bak_edges)}")
for e in bak_edges:
    print(e.strip())

print("="*40)
print(f"Curr edges count: {len(curr_edges)}")
for e in curr_edges:
    print(e.strip())


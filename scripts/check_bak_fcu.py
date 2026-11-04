with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
fcu_segs = re.findall(r'\(segment\s+.*?layer\s+"F\.Cu".*?\)', bak, re.DOTALL)
print(f"Total F.Cu segments in bak: {len(fcu_segs)}")
for s in fcu_segs[:5]:
    print(s)

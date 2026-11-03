with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
segments = re.findall(r'\(segment[\s\S]*?\n\t\)', bak)
print(f"Matched {len(segments)} segments")
for s in segments[:5]:
    print(s)

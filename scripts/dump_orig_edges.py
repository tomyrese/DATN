with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find all gr_line, gr_circle, gr_text, gr_rect, gr_poly
grs = re.findall(r'\(gr_\w+[\s\S]*?\n\t\)', text)
print(f"Total graphics items in bak: {len(grs)}")
for g in grs:
    if 'Edge.Cuts' in g:
        print(repr(g))

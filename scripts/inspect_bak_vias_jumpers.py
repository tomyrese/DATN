with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re
vias = re.findall(r'\(via\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\).*?\(net\s+"([^"]+)"\)', pcb, re.DOTALL)
print(f"Total vias in bak: {len(vias)}")
for v in vias:
    print(f"Via at ({float(v[0]):.2f}, {float(v[1]):.2f}), net: {v[2]}")

gr_texts = re.findall(r'\(gr_text\s+"([^"]+)"\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\)', pcb)
print("\nSilk text in bak:")
for t in gr_texts:
    if 'JMP' in t[0] or 'J' in t[0]:
        print(f"Text: '{t[0]}' at ({float(t[1]):.2f}, {float(t[2]):.2f})")


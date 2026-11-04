with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    pcb = f.read()

import re

for ref in ['R1', 'R2', 'R3', 'R4', 'U_US1', 'U_US2']:
    idx = pcb.find(f'"{ref}"')
    if idx != -1:
        start = pcb.rfind('(footprint', 0, idx)
        end = pcb.find('\n\t)', idx)
        block = pcb[start:end+3]
        print(f"=== {ref} ===")
        pads = re.findall(r'\(pad\s+"([^"]+)".*?\(net\s+"([^"]+)"\)', block, re.DOTALL)
        for p in pads:
            print(f"  Pad {p[0]}: {p[1]}")

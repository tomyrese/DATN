import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    pcb = f.read()

for ref in ['R1', 'R2', 'R3', 'R4']:
    idx = pcb.find(f'(property "Reference" "{ref}"')
    if idx != -1:
        start = pcb.rfind('(footprint', 0, idx)
        end = pcb.find('\n\t)', idx)
        block = pcb[start:end+3]
        print(f"=== {ref} ===")
        pads = re.findall(r'\(pad\s+"([^"]+)"\s+([^\s]+)\s+([^\s]+)\s+\(at\s+([-\d\.]+)\s+([-\d\.]+).*?\(net\s+(\d+)\s+"([^"]+)"\)', block)
        for p in pads:
            print(f"  Pad {p[0]}: at ({p[3]}, {p[4]}), net {p[6]}")


with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    pcb = f.read()

for ref in ['R2', 'R3', 'R4']:
    idx = pcb.find(f'(property "Reference" "{ref}"')
    if idx != -1:
        start = pcb.rfind('(footprint', 0, idx)
        end = pcb.find('\n\t)', idx)
        print(f"=== {ref} ===")
        print(pcb[start:end+3])


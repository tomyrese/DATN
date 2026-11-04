with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    pcb = f.read()

idx = pcb.find('(property "Reference" "R1"')
if idx != -1:
    start = pcb.rfind('(footprint', 0, idx)
    end = pcb.find('\n\t)', idx)
    print(pcb[start:end+3])


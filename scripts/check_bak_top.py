with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[50:150]):
    print(f"{i+51}: {l}", end='')

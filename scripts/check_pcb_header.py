with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = [f.readline() for _ in range(60)]

for i, l in enumerate(lines):
    print(f"{i+1}: {l}", end='')

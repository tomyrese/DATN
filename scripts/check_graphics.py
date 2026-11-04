with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2640, 2715):
    print(f"{i+1}: {lines[i]}", end='')


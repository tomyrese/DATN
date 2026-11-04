import sys
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'TB6612_Left' in line:
        for j in range(i, i+150):
            print(f"{j+1}: {lines[j]}", end='')
            if lines[j].strip() == ')': # footprint end
                break
        break


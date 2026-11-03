import sys
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_fp = False
indent = 0
for i, line in enumerate(lines):
    if '(footprint "Module_TB6612FNG_Breakout"' in line:
        in_fp = True
    if in_fp:
        print(f"{i+1}: {line}", end='')
        if line.startswith('\t)'):
            break

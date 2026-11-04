with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[:200]):
    if '(net ' in l and not '(pad ' in l and not '(segment ' in l and not '(via ' in l:
        print(f"{i+1}: {l}", end='')


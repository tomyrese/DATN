with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Edge.Cuts' in line:
        print(f"Line {i+1}: {line.strip()}")
        for j in range(max(0, i-3), min(len(lines), i+6)):
            print(f"  {j+1}: {lines[j].strip()}")
        print('='*40)


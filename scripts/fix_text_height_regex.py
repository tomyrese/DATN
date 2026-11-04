import re

for path in ['Pi4_Robot_Carrier_1Layer.kicad_pcb', 'robot_electronics.kicad_pcb']:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'\(size\s+0\.7\s+0\.7\)\s+\(thickness\s+[-\d.]+\)', '(size 0.8 0.8) (thickness 0.12)', text)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

print("Updated text height properly to 0.8mm.")

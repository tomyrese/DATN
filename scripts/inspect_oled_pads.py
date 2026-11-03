import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'\(footprint\s+"[^"]*OLED[^"]*"[\s\S]*?\n\t\)', text):
    fp = m.group(0)
    print(fp)

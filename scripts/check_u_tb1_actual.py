import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'\(footprint\s+"[^"]+".*?\(property\s+"Reference"\s+"U_TB1".*?\n\t\)', text, re.DOTALL)
if m:
    for line in m.group(0).splitlines():
        if '(at ' in line or '(pad ' in line:
            print(line)

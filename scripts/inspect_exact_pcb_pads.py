import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find U_TB1 block
m = re.search(r'\(footprint\s+"[^"]+".*?\(property\s+"Reference"\s+"U_TB1".*?\n\t\)', text, re.DOTALL)
if m:
    print("=== FOOTPRINT U_TB1 in kicad_pcb ===")
    for line in m.group(0).splitlines():
        if '(at ' in line or '(pad ' in line:
            print(line)

# Find R_JMP1 block
m2 = re.search(r'\(footprint\s+"[^"]+".*?\(property\s+"Reference"\s+"R_JMP1".*?\n\t\)', text, re.DOTALL)
if m2:
    print("\n=== FOOTPRINT R_JMP1 in kicad_pcb ===")
    for line in m2.group(0).splitlines():
        if '(at ' in line or '(pad ' in line:
            print(line)

import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find U_TB1
for match in re.finditer(r'\(footprint\s+"([^"]+)".*?\(property\s+"Reference"\s+"U_TB1".*?\n\t\)', text, re.DOTALL):
    s = match.group(0)
    print("=== U_TB1 ===")
    for line in s.splitlines():
        if '(at ' in line or '(pad ' in line or '(property "Reference"' in line:
            print(line)

# Find U_PI4
for match in re.finditer(r'\(footprint\s+"([^"]+)".*?\(property\s+"Reference"\s+"U_PI4".*?\n\t\)', text, re.DOTALL):
    s = match.group(0)
    print("=== U_PI4 ===")
    for line in s.splitlines():
        if '(at ' in line or '(pad 1 ' in line or '(pad 2 ' in line or '(pad 39 ' in line or '(pad 40 ' in line or '(property "Reference"' in line:
            print(line)

import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

setup_m = re.search(r'\(setup\b[\s\S]*?\n\t\)', text)
if setup_m:
    print("=== SETUP ===")
    print(setup_m.group(0))

for m in re.finditer(r'\(net_class\b[\s\S]*?\n\t\)', text):
    print("=== NET_CLASS ===")
    print(m.group(0))


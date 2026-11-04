import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

nets = sorted(list(set(re.findall(r'\(net\s+"([^"]+)"\)', text))))
print("Total unique nets:", len(nets))
for n in nets:
    if not n.startswith("unconnected-"):
        print("  ", n)


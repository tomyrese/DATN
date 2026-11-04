import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\n\t\)', text):
    fp = m.group(0)
    ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp)
    ref_name = ref.group(1) if ref else ""
    if ref_name in ['R3', 'R4']:
        print(f"================ {ref_name} ================")
        print(fp)


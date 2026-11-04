import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

refs = re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', text)
if not refs:
    refs = re.findall(r'\(fp_text\s+reference\s+"([^"]+)"', text)
print("Footprint references found:", refs)


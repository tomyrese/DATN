import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

fps = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\n\t\)', text)
for m in re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\n\t\)', text):
    fp_text = m.group(0)
    fp_lib = m.group(1)
    ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_text)
    ref_val = ref.group(1) if ref else "UNKNOWN"
    print(f"Ref: {ref_val:<15} Lib: {fp_lib}")

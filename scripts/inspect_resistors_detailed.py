import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\n\t\)', text):
    fp = m.group(0)
    ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp)
    ref_name = ref.group(1) if ref else ""
    if ref_name in ['R1', 'R2', 'R3', 'R4']:
        at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', fp)
        print(f"=== {ref_name} at {at.group(1)}, {at.group(2)} ===")
        pads = re.findall(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)[\s\S]*?\(net\s+\d+\s+"([^"]+)"\)', fp)
        for p in pads:
            print(f"  Pad {p[0]} relative ({p[1]}, {p[2]}) net: {p[3]}")

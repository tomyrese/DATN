import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'\(footprint\s+"PinSocket_2x20_P2\.54mm_Vertical"[\s\S]*?\n\t\)', text):
    fp = m.group(0)
    at_m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', fp)
    print("Pi4 header at:", at_m.groups() if at_m else None)
    pads = re.findall(r'\(pad\s+"(\d+)"\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)', fp)
    for p in pads[:6]:
        print(f"  Pad {p[0]} at ({p[1]}, {p[2]})")
    for p in pads[-4:]:
        print(f"  Pad {p[0]} at ({p[1]}, {p[2]})")

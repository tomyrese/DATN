import re, math

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    txt = f.read()

chunks = txt.split('(footprint ')
for c in chunks[1:]:
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', c)
    if not ref_m: continue
    ref = ref_m.group(1)
    if ref in ['LEFT', 'RIGHT']:
        at_m = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', c[:300])
        fx, fy = float(at_m.group(1)), float(at_m.group(2))
        frot = float(at_m.group(3)) if at_m.group(3) else 0.0
        print(f"\n=== {ref} in .bak at ({fx}, {fy}), rot={frot} ===")
        pads = re.findall(r'\(pad\s+"(\d+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)[\s\S]*?\(net\s+"([^"]*)"\)', c)
        for p, px, py, prot, net in sorted(pads, key=lambda x: int(x[0])):
            px, py = float(px), float(py)
            rad = math.radians(frot)
            wx = round(fx + px * math.cos(rad) - py * math.sin(rad), 4)
            wy = round(fy + px * math.sin(rad) + py * math.cos(rad), 4)
            print(f"  Pad {int(p):2d}: local=({px:6.2f}, {py:6.2f}) -> world=({wx:7.2f}, {wy:7.2f})  net={net}")


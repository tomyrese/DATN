import re
import math

content = open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8').read()

fp_indices = [m.start() for m in re.finditer(r'\(footprint\s+"', content)]
fp_indices.append(len(content))

pads_info = []

for i in range(len(fp_indices) - 1):
    fp_str = content[fp_indices[i]:fp_indices[i+1]]
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_str)
    ref = ref_m.group(1) if ref_m else '?'

    at_m = re.search(r'\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)', fp_str)
    fcx = float(at_m.group(1)) if at_m else 0.0
    fcy = float(at_m.group(2)) if at_m else 0.0
    frot = float(at_m.group(3)) if at_m and at_m.group(3) else 0.0

    rad = math.radians(frot)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)

    pad_matches = re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([0-9.-]+)\s+([0-9.-]+)[^\)]*\)(.*?)(?=\n\t\t\(pad|\n\t\))', fp_str, re.DOTALL)
    for pm in pad_matches:
        pnum = pm.group(1)
        px_rel = float(pm.group(2))
        py_rel = float(pm.group(3))
        prest = pm.group(4)
        net_m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', prest)
        nname = net_m.group(1) if net_m else "None"

        # KiCad rotation: positive is CCW or CW? In KiCad:
        # (x_rel, y_rel) rotated by angle:
        # rx = x_rel * cos - y_rel * sin
        # ry = x_rel * sin + y_rel * cos (in standard math with Y down, let's verify)
        # Actually KiCad uses CW rotation:
        rx = px_rel * math.cos(rad) - py_rel * math.sin(rad)
        ry = px_rel * math.sin(rad) + py_rel * math.cos(rad)
        abs_x = round(fcx + rx, 2)
        abs_y = round(fcy + ry, 2)
        pads_info.append((ref, pnum, abs_x, abs_y, nname))

pads_info.sort(key=lambda p: (p[0], int(p[1]) if p[1].isdigit() else p[1]))
for p in pads_info:
    print(f"{p[0]:12s} pad {p[1]:3s} at ({p[2]:6.2f}, {p[3]:6.2f}) -> {p[4]}")

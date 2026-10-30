import re

content = open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8').read()

fp_indices = [m.start() for m in re.finditer(r'\(footprint\s+"', content)]
fp_indices.append(len(content))

nets_pads = {}

for i in range(len(fp_indices) - 1):
    fp_str = content[fp_indices[i]:fp_indices[i+1]]
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_str)
    ref = ref_m.group(1) if ref_m else '?'

    pad_matches = re.finditer(r'\(pad\s+"([^"]+)"', fp_str)
    for pm in pad_matches:
        pnum = pm.group(1)
        sub = fp_str[pm.start():pm.start()+300]
        net_m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', sub)
        if net_m:
            nname = net_m.group(1)
            nets_pads.setdefault(nname, []).append((ref, pnum))

for n, plist in sorted(nets_pads.items()):
    print(f"{n:20s} ({len(plist)} pads): {plist}")

import math
import json
from parse_fps_exact import parse_sexpr

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

tree = parse_sexpr(text)

world_pads = {}

for item in tree:
    if isinstance(item, list) and item and item[0] == 'footprint':
        ref = None
        for sub in item:
            if isinstance(sub, list) and len(sub) >= 3 and sub[0] == 'property' and sub[1] == '"Reference"':
                ref = sub[2].strip('"')
        if not ref:
            continue

        at_val = None
        for sub in item:
            if isinstance(sub, list) and sub and sub[0] == 'at':
                at_val = sub[1:]
                break
        
        fp_x = float(at_val[0])
        fp_y = float(at_val[1])
        fp_rot = float(at_val[2]) if len(at_val) > 2 else 0.0

        world_pads[ref] = {
            'fp_pos': [fp_x, fp_y, fp_rot],
            'pads': {}
        }

        for sub in item:
            if isinstance(sub, list) and sub and sub[0] == 'pad':
                pnum = sub[1].strip('"')
                p_at = None
                p_net = ""
                for psub in sub:
                    if isinstance(psub, list) and psub:
                        if psub[0] == 'at':
                            p_at = psub[1:]
                        elif psub[0] == 'net':
                            p_net = psub[1].strip('"')
                
                lx = float(p_at[0])
                ly = float(p_at[1])
                rad = math.radians(fp_rot)
                wx = fp_x + lx * math.cos(rad) - ly * math.sin(rad)
                wy = fp_y + lx * math.sin(rad) + ly * math.cos(rad)

                world_pads[ref]['pads'][pnum] = {
                    'world': [round(wx, 4), round(wy, 4)],
                    'net': p_net
                }

with open('scripts/true_world_pads.json', 'w', encoding='utf-8') as f:
    json.dump(world_pads, f, indent=2)

print(f"Saved true world pads for {len(world_pads)} footprints.")
for ref in sorted(world_pads.keys()):
    print(f"\nFootprint {ref} ({world_pads[ref]['fp_pos']}):")
    for p in sorted(world_pads[ref]['pads'].keys(), key=lambda x: int(x) if x.isdigit() else x):
        pinfo = world_pads[ref]['pads'][p]
        if not pinfo['net'].startswith("unconnected-"):
            print(f"  Pad {p:>2}: ({pinfo['world'][0]:>7.2f}, {pinfo['world'][1]:>7.2f}) -> {pinfo['net']}")


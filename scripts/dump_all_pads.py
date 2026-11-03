import sys, re
from test_fp_swap import swap_tb6612_rows, mirror_pi4_header

with open('Pi4_Robot_Carrier_1Layer_clean.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

def fp_repl(m):
    fp = m.group(0)
    if 'TB6612_Left' in fp or 'reference "LEFT"' in fp:
        return swap_tb6612_rows(fp)
    elif 'TB6612_Right' in fp or 'reference "RIGHT"' in fp:
        return swap_tb6612_rows(fp)
    elif 'Raspberry_Pi_4_40Pin' in fp or 'reference "Rasp_PI4"' in fp:
        return mirror_pi4_header(fp)
    return fp

text = re.sub(r'\(footprint\s+"[^"]+"[\s\S]*?\n\t\)', fp_repl, text)

# Parse footprints and their pads
from parse_pcb_sexpr import parse_sexpr

tree = parse_sexpr(text)

all_pads = {}
for item in tree:
    if isinstance(item, list) and len(item) > 0 and item[0] == 'footprint':
        ref = "?"
        fp_at = (0, 0, 0)
        for prop in item:
            if isinstance(prop, list) and len(prop) > 0:
                if prop[0] == 'property' and prop[1] == 'Reference':
                    ref = prop[2]
                elif prop[0] == 'at':
                    fp_at = [float(x) for x in prop[1:]]
                    if len(fp_at) == 2:
                        fp_at.append(0.0)
        all_pads[ref] = {}
        for prop in item:
            if isinstance(prop, list) and len(prop) > 0 and prop[0] == 'pad':
                pad_num = prop[1]
                pad_at = None
                pad_net = None
                for p_attr in prop:
                    if isinstance(p_attr, list) and len(p_attr) > 0:
                        if p_attr[0] == 'at':
                            pad_at = [float(x) for x in p_attr[1:]]
                            if len(pad_at) == 2:
                                pad_at.append(0.0)
                        elif p_attr[0] == 'net':
                            pad_net = p_attr[2] if len(p_attr) > 2 else p_attr[1]
                
                # Calculate world coordinate:
                # rotation:
                import math
                rad = math.radians(fp_at[2])
                # KiCad 2D rotation:
                xw = fp_at[0] + pad_at[0]*math.cos(rad) - pad_at[1]*math.sin(rad)
                yw = fp_at[1] + pad_at[0]*math.sin(rad) + pad_at[1]*math.cos(rad)
                # Wait, earlier we found KiCad Y is down, so rot 90:
                # Let's check with the actual KiCad behavior!
                all_pads[ref][pad_num] = (pad_at, pad_net)

print("Footprints parsed.")
for ref, pads in all_pads.items():
    print(f"\n{ref}: {len(pads)} pads")
    for p_num in sorted(pads.keys(), key=lambda x: int(x) if x.isdigit() else x):
        print(f"  Pad {p_num:>2}: local={pads[p_num][0]} net={pads[p_num][1]}")

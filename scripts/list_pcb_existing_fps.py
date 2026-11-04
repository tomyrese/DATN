from parse_fps_exact import parse_sexpr

tree = parse_sexpr(open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8').read())

fps_in_pcb = {}
for item in tree:
    if isinstance(item, list) and item and item[0] == 'footprint':
        fp_name = item[1].strip('"')
        ref = None
        for sub in item:
            if isinstance(sub, list) and len(sub) >= 3 and sub[0] == 'property' and sub[1] == '"Reference"':
                ref = sub[2].strip('"')
        if ref:
            fps_in_pcb[ref] = fp_name

print("Footprints in existing PCB:")
for r, name in sorted(fps_in_pcb.items()):
    print(f"  {r:>10}: {name}")


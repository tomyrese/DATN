from inspect_placed_symbols import parse_sexpr

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

tree = parse_sexpr(text)

# Find lib_symbols
lib_syms = {}
for item in tree:
    if isinstance(item, list) and item and item[0] == 'lib_symbols':
        for sym in item[1:]:
            if isinstance(sym, list) and sym and sym[0] == 'symbol':
                name = sym[1].strip('"')
                pins = []
                for sub in sym:
                    if isinstance(sub, list) and sub and sub[0] == 'symbol':
                        for sub2 in sub:
                            if isinstance(sub2, list) and sub2 and sub2[0] == 'pin':
                                ptype = sub2[1]
                                pshape = sub2[2]
                                pnum = None
                                pname = None
                                pat = None
                                for pprop in sub2:
                                    if isinstance(pprop, list) and pprop:
                                        if pprop[0] == 'name':
                                            pname = pprop[1].strip('"')
                                        elif pprop[0] == 'number':
                                            pnum = pprop[1].strip('"')
                                        elif pprop[0] == 'at':
                                            pat = pprop[1:]
                                pins.append((pnum, pname, ptype, pat))
                lib_syms[name] = pins

print(f"Total lib symbols: {len(lib_syms)}")
for name, pins in sorted(lib_syms.items()):
    print(f"\n--- Symbol: {name} ({len(pins)} pins) ---")
    for p in sorted(pins, key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        print(f"  Pin {p[0]:>2}: {p[1]:<20} type: {p[2]} at: {p[3]}")


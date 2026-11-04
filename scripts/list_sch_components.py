import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# Separate lib_symbols from sheet content
lib_end = sch.find('(lib_symbols')
sheet_part = sch
if lib_end != -1:
    # find closing parenthesis of lib_symbols
    # let's just find symbols outside lib_symbols
    pass

# We can parse sheet symbols using parse_sexpr
from parse_fps_exact import parse_sexpr

tree = parse_sexpr(sch)
symbols = []
for item in tree:
    if isinstance(item, list) and item and item[0] == 'symbol':
        ref = None
        val = None
        fp = None
        at = None
        for sub in item:
            if isinstance(sub, list) and len(sub) >= 3 and sub[0] == 'property':
                if sub[1] == '"Reference"':
                    ref = sub[2].strip('"')
                elif sub[1] == '"Value"':
                    val = sub[2].strip('"')
                elif sub[1] == '"Footprint"':
                    fp = sub[2].strip('"')
            elif isinstance(sub, list) and sub and sub[0] == 'at':
                at = sub[1:]
        if ref and not ref.startswith('#'):
            symbols.append((ref, val, fp, at))

print(f"Placed components in schematic: {len(symbols)}")
for s in sorted(symbols, key=lambda x: x[0]):
    print(f"  {s[0]:>10}: {s[1]:<20} at {s[3]} fp: {s[2]}")


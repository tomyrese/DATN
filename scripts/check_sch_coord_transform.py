# Check how KiCad schematic transforms symbol pins
# In KiCad sexpr schematic:
# Symbol at (X, Y, rot), where rot is 0, 90, 180, 270.
# Pin in lib_symbol: (pin type shape (at px py prot) ...)
# Note: in KiCad schematic sexpr, standard rotation is:
# rot = 0: x' = X + px, y' = Y - py (since KiCad schematic Y is inverted or standard?)
# Let's verify by checking the original schematic!

from inspect_placed_symbols import parse_sexpr
with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

tree = parse_sexpr(text)

# Find a symbol and a wire connected to it
for item in tree:
    if isinstance(item, list) and item and item[0] == 'symbol':
        ref = None
        for sub in item:
            if isinstance(sub, list) and len(sub) >= 3 and sub[0] == 'property' and sub[1] == '"Reference"':
                ref = sub[2].strip('"')
        if ref == 'U_US1':
            print("Found U_US1 symbol:")
            for sub in item:
                if isinstance(sub, list) and sub[0] in ['at', 'property']:
                    print(" ", sub[:3])

# Find wires or labels near U_US1 in bak
for item in tree:
    if isinstance(item, list) and item and item[0] in ['label', 'wire']:
        item_str = str(item)
        if 'TRIG_L' in item_str or 'ECHO_L' in item_str:
            print("Found item:", item)


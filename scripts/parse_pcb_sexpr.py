import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def parse_sexpr(text):
    tokens = re.findall(r'\(|\)|"[^"]*"|[^\s()]+', text)
    stack = [[]]
    for token in tokens:
        if token == '(':
            new_list = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif token == ')':
            stack.pop()
        else:
            if token.startswith('"') and token.endswith('"'):
                token = token[1:-1]
            stack[-1].append(token)
    return stack[0][0]

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    tree = parse_sexpr(f.read())

print(f"Root: {tree[0]}")

for item in tree:
    if isinstance(item, list) and len(item) > 0 and item[0] == 'footprint':
        fp_name = item[1]
        ref = "?"
        val = "?"
        at = None
        pads = []
        for prop in item:
            if isinstance(prop, list) and len(prop) > 0:
                if prop[0] == 'fp_text':
                    if len(prop) > 2 and prop[1] == 'reference':
                        ref = prop[2]
                    elif len(prop) > 2 and prop[1] == 'value':
                        val = prop[2]
                elif prop[0] == 'property':
                    if len(prop) > 2 and prop[1] == 'Reference':
                        ref = prop[2]
                    elif len(prop) > 2 and prop[1] == 'Value':
                        val = prop[2]
                elif prop[0] == 'at':
                    at = prop[1:]
                elif prop[0] == 'pad':
                    pad_num = prop[1]
                    pad_type = prop[2]
                    pad_shape = prop[3]
                    pad_at = None
                    net_name = None
                    for pad_prop in prop:
                        if isinstance(pad_prop, list) and len(pad_prop) > 0:
                            if pad_prop[0] == 'at':
                                pad_at = pad_prop[1:]
                            elif pad_prop[0] == 'net':
                                net_name = pad_prop[2] if len(pad_prop) > 2 else pad_prop[1]
                    pads.append((pad_num, pad_type, pad_shape, pad_at, net_name))
        print(f"\nFootprint {ref} ({val}) [{fp_name}] at {at}:")
        for p in pads:
            print(f"  Pad {p[0]:>3}: at {p[3]} | Net: {p[4]}")


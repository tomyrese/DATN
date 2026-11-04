def parse_sexpr(text):
    tokens = []
    i = 0
    n = len(text)
    stack = [[]]
    cur_token = []
    in_quote = False
    
    while i < n:
        c = text[i]
        if in_quote:
            if c == '"':
                in_quote = False
                cur_token.append(c)
                stack[-1].append("".join(cur_token))
                cur_token = []
            elif c == '\\':
                cur_token.append(c)
                i += 1
                if i < n:
                    cur_token.append(text[i])
            else:
                cur_token.append(c)
        else:
            if c == '"':
                in_quote = True
                cur_token.append(c)
            elif c == '(':
                new_list = []
                stack[-1].append(new_list)
                stack.append(new_list)
            elif c == ')':
                if cur_token:
                    stack[-1].append("".join(cur_token))
                    cur_token = []
                stack.pop()
            elif c in ' \t\r\n':
                if cur_token:
                    stack[-1].append("".join(cur_token))
                    cur_token = []
            else:
                cur_token.append(c)
        i += 1
    return stack[0][0]

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

tree = parse_sexpr(text)
print("Root tag:", tree[0])

# Find all footprints
fps = {}
for item in tree:
    if isinstance(item, list) and item and item[0] == 'footprint':
        # get reference property
        ref = None
        for sub in item:
            if isinstance(sub, list) and len(sub) >= 3:
                if sub[0] == 'property' and sub[1] == '"Reference"':
                    ref = sub[2].strip('"')
        if ref:
            fps[ref] = item

print(f"Total footprints parsed: {len(fps)}")
for ref in ['LEFT', 'RIGHT', 'Rasp_PI4', 'OLED']:
    fp = fps.get(ref)
    if not fp:
        print(f"FP {ref} not found!")
        continue
    # find (at ...)
    at_val = None
    for sub in fp:
        if isinstance(sub, list) and sub and sub[0] == 'at':
            at_val = sub[1:]
            break
    print(f"\nFootprint {ref}: at {at_val}")
    # find pads
    for sub in fp:
        if isinstance(sub, list) and sub and sub[0] == 'pad':
            pnum = sub[1].strip('"')
            p_at = None
            p_net = None
            for psub in sub:
                if isinstance(psub, list) and psub:
                    if psub[0] == 'at':
                        p_at = psub[1:]
                    elif psub[0] == 'net':
                        p_net = psub[1:]
            print(f"  Pad {pnum:>2}: at {p_at} -> net {p_net}")


def parse_sexpr(text):
    stack = [[]]
    cur_token = []
    in_quote = False
    i = 0
    n = len(text)
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

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

tree = parse_sexpr(text)

symbols_info = {}
for item in tree:
    if isinstance(item, list) and item and item[0] == 'symbol':
        # check if it is a placed symbol
        ref = None
        val = None
        lib_id = None
        for sub in item:
            if isinstance(sub, list) and len(sub) >= 2 and sub[0] == 'lib_id':
                lib_id = sub[1].strip('"')
            elif isinstance(sub, list) and len(sub) >= 3 and sub[0] == 'property':
                if sub[1] == '"Reference"':
                    ref = sub[2].strip('"')
                elif sub[1] == '"Value"':
                    val = sub[2].strip('"')
        if ref and not ref.startswith('#'):
            symbols_info[ref] = {'val': val, 'lib_id': lib_id}

print(f"Total unique symbols placed: {len(symbols_info)}")
for r, d in sorted(symbols_info.items()):
    print(f"  {r:>10}: {d['val']:<20} (lib: {d['lib_id']})")

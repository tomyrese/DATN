with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('(lib_symbols')
print("lib_symbols start:", start)
if start != -1:
    depth = 0
    in_quote = False
    for i in range(start, len(text)):
        c = text[i]
        if c == '"' and text[i-1] != '\\':
            in_quote = not in_quote
        elif not in_quote:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    print(f"lib_symbols end: {end}, length: {end - start}")
                    with open('scripts/lib_symbols.sexpr', 'w', encoding='utf-8') as out:
                        out.write(text[start:end])
                    break


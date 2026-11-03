with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

for r in ['R3', 'R4']:
    pos = text.find(f'"{r}"')
    start = text.rfind('(footprint', 0, pos)
    count = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == '(': count += 1
        elif text[i] == ')':
            count -= 1
            if count == 0:
                end = i + 1
                break
    print(f"=== {r} ===")
    print(text[start:end])

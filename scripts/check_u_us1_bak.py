with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"U_US1"')
if idx != -1:
    start = text.rfind('(symbol', 0, idx)
    end = text.find('\n\t)', idx)
    print("U_US1 in bak:")
    print(text[start:end+4])


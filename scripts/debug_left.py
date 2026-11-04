with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"LEFT"')
print("idx:", idx)
if idx != -1:
    print(text[idx-100:idx+600])


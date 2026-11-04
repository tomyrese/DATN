with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('(segment ')
print(text[idx:idx+400])


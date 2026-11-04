with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('(pad "1"')
print("First pad from idx:")
print(text[idx:idx+1500])


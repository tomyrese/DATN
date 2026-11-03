with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('"LEFT"')
print(text[pos+5500:pos+7000])

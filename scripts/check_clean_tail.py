with open('Pi4_Robot_Carrier_1Layer_clean.kicad_pcb', 'r', encoding='utf-8') as f:
    clean = f.read()

pos = clean.rfind('(embedded_fonts no)')
print(clean[pos-300:pos+100])


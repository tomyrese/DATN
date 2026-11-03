with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

pos = bak.find('(segment')
print("First segment in bak:")
print(bak[pos:pos+300])

pos_via = bak.find('(via')
print("First via in bak:")
print(bak[pos_via:pos_via+300])

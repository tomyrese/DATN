with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

pos = sch.find('(at 109.22 55.88 0)')
print(sch[pos-400:pos+300])


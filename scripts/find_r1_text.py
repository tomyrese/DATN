with open('robot_electronics.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

idx = sch.find('"R1"')
print(sch[idx-100:idx+400])


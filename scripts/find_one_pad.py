with open('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('(pad "1" ')
print(text[idx:idx+300])


with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('(font (size 0.7 0.7) (thickness 0.1))', '(font (size 0.8 0.8) (thickness 0.12))')

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated text height to 0.8mm.")

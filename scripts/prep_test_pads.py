import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace rotation of U_TB1 and U_TB2 to 90
text = re.sub(r'\(at (68\.00 68\.00) 270\)', r'(at \1 90)', text)
text = re.sub(r'\(at (140\.00 68\.00) 270\)', r'(at \1 90)', text)

# Replace rotation of R_JMP1..3 to 90
text = re.sub(r'\(at (130\.00 84\.00) 270\)', r'(at \1 90)', text)
text = re.sub(r'\(at (133\.50 84\.00) 270\)', r'(at \1 90)', text)
text = re.sub(r'\(at (137\.00 84\.00) 270\)', r'(at \1 90)', text)

# Remove all tracks temporarily to inspect pure pad coordinates
text = re.sub(r'\t\(segment.*?\n', '', text)

with open('test_pads.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Created test_pads.kicad_pcb with rot 90 and no tracks.")

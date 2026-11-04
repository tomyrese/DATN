import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update C4 position to (114.00 100.00)
text = re.sub(
    r'(\(at\s+)119\.00(\s+100\.00\)\s+\(property\s+"Reference"\s+"C4")',
    r'\g<1>114.00\2',
    text
)
print("Updated C4 position to (114.00, 100.00)")

# 2. Update R_JMP4, R_JMP5, R_JMP6 to vertical (rot 90) at X=112, 118, 124
# R_JMP4
text = re.sub(
    r'\(at\s+114\.00\s+78\.00(?:\s+\d+)?\)(\s+\(property\s+"Reference"\s+"R_JMP4")',
    r'(at 112.00 78.00 90)\1',
    text
)
# R_JMP5
text = re.sub(
    r'\(at\s+122\.00\s+78\.00(?:\s+\d+)?\)(\s+\(property\s+"Reference"\s+"R_JMP5")',
    r'(at 118.00 78.00 90)\1',
    text
)
# R_JMP6
text = re.sub(
    r'\(at\s+130\.00\s+78\.00(?:\s+\d+)?\)(\s+\(property\s+"Reference"\s+"R_JMP6")',
    r'(at 124.00 78.00 90)\1',
    text
)
print("Updated R_JMP4..6 positions and rot=90")

# 3. Remove duplicate gr_text on F.SilkS
text = re.sub(r'\t\(gr_text\s+"(BAT 11\.1V|MAIN SW|FUSE 7\.5A|XL4015 5V|M1 \(FL\)|M2 \(RL\)|M3 \(FR\)|M4 \(RR\)|US LEFT|LINE 3CH|US RIGHT|OLED 1\.3)".*?\n', '', text)
print("Removed duplicate gr_text")

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved files.")

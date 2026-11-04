import re

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Move C3 reference to (at 0 3.5 0)
    text = re.sub(
        r'(\(property\s+"Reference"\s+"C3"\s+\(at\s+0\s+)-3\.5(\s+0\))',
        r'\g<1>3.5\2',
        text
    )

    # Move C4 reference to (at 0 3.5 0)
    text = re.sub(
        r'(\(property\s+"Reference"\s+"C4"\s+\(at\s+0\s+)-3\.5(\s+0\))',
        r'\g<1>3.5\2',
        text
    )

    # For R_JMP1..3, reduce font to (size 0.7 0.7) and set position to (at 0 -2.5 90) or vertical
    for r in ['R_JMP1', 'R_JMP2', 'R_JMP3', 'R_JMP4', 'R_JMP5', 'R_JMP6']:
        # Match Reference property of this jumper
        pattern = rf'(\(property\s+"Reference"\s+"{r}"\s+\(at\s+)[-\d.]+\s+[-\d.]+(?:\s+[-\d.]+)?(\)\s+\(layer\s+"F\.SilkS"\)\s+\(effects\s+\(font\s+\(size\s+)[-\d.]+\s+[-\d.]+(\)\s+\(thickness\s+)[-\d.]+(\)\)\))'
        text = re.sub(pattern, r'\g<1>0 -2.5 90\2 0.7 0.7\3 0.10\4', text)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Cleaned silkscreen in {path}")

clean_file('Pi4_Robot_Carrier_1Layer.kicad_pcb')
clean_file('robot_electronics.kicad_pcb')

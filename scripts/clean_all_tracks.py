import sys, re

def clean_pcb(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # In KiCad PCB, segments and vias are top-level items under (kicad_pcb ...)
    # Let's remove any top-level (segment ...) or (via ...)
    # We can match them by regex:
    # Pattern: \n\s*\((segment|via)\b[\s\S]*?\n\s*\)
    # Let's verify by testing on the file
    cleaned = re.sub(r'\n\s*\((segment|via)\b[\s\S]*?\n\s*\)', '', text)
    # Also clean old jumper silkscreen items (gr_line, gr_circle, gr_text for JMP)
    cleaned = re.sub(r'\n\s*\(gr_(line|circle|text)\b[\s\S]*?JMP[\s\S]*?\n\s*\)', '', cleaned)
    
    segs = re.findall(r'\(segment\b', cleaned)
    vias = re.findall(r'\(via\b', cleaned)
    print(f"After cleaning: segments={len(segs)}, vias={len(vias)}")
    return cleaned

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

cleaned = clean_pcb('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak')

with open('Pi4_Robot_Carrier_1Layer_clean.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(cleaned)

print("Saved Pi4_Robot_Carrier_1Layer_clean.kicad_pcb")


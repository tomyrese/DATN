import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

fps = re.findall(r'\(footprint\s+.*?\n\t\)', text, re.DOTALL)
for fp in fps:
    for r in ['R1', 'R2', 'R3', 'R4']:
        if f'"{r}"' in fp:
            m = re.search(r'\(property\s+"Reference"\s+"(.*?)"', fp)
            m_old = re.search(r'\(fp_text\s+reference\s+"(.*?)"', fp)
            print(f"{r} match -> property Reference: {m.group(1) if m else None}, fp_text: {m_old.group(1) if m_old else None}")


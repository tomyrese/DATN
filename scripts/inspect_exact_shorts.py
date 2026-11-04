with open('drc_master_v30.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'\[(shorting_items|tracks_crossing)\]:[^\n]+\n[^\n]+\n@\(([-\d.]+)\s+mm,\s+([-\d.]+)\s+mm\):\s+([^\n]+)\n@\(([-\d.]+)\s+mm,\s+([-\d.]+)\s+mm\):\s+([^\n]+)', text)

for m in list(matches)[:15]:
    code, x1, y1, item1, x2, y2, item2 = m.groups()
    print(f"[{code}] at ({x1}, {y1}) vs ({x2}, {y2}):\n  Item 1: {item1}\n  Item 2: {item2}\n")

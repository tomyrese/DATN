with open('drc_final_report.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'\[unconnected_items\]:[^\n]*\n(?:[ \t]+[^\n]*\n){1,3}', text)
for i, m in enumerate(matches):
    print(f"{i+1}: {m.strip()}")


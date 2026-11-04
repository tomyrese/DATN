with open('drc_final_v16.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
types = re.findall(r'\[([^\]]+)\]:\s*([^\n]+)', text)
type_counts = {}
for t, desc in types:
    type_counts[t] = type_counts.get(t, 0) + 1

print("DRC final v16 summary:")
for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  [{t}]: {c} occurrences")

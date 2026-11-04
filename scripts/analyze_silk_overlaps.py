with open('drc_v20.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
overlaps = re.findall(r'\[silk_overlap\]:.*?\n\s+Rule:.*?\n\s+@\([^\)]+\):\s*([^\n]+)\n\s+@\([^\)]+\):\s*([^\n]+)', text)
print(f"Total silk overlaps: {len(overlaps)}")
items = {}
for o1, o2 in overlaps:
    items[o1] = items.get(o1, 0) + 1
    items[o2] = items.get(o2, 0) + 1

for k, v in sorted(items.items(), key=lambda x: -x[1])[:15]:
    print(f"  {k}: {v}")


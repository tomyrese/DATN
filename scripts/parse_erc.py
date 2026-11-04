with open('erc_clean.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
from collections import defaultdict

violations = defaultdict(list)
entries = re.split(r'\[(.*?)\]:\s+', text)
for i in range(1, len(entries), 2):
    t = entries[i]
    b = entries[i+1].strip()
    violations[t].append(b[:120].replace('\n', ' '))

print(f"Total ERC violations: {sum(len(v) for v in violations.values())}")
for t, lst in sorted(violations.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  [{t}]: {len(lst)}")
    for s in lst[:3]:
        print(f"    sample: {s}")


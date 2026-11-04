with open('drc_industrial_test.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
violations = re.findall(r'\[([^\]]+)\]:', text)
from collections import Counter
counts = Counter(violations)
print("=== DRC VIOLATION BREAKDOWN ===")
for v, c in counts.most_common():
    print(f"  {v:30}: {c}")

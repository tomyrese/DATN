with open('drc_git_head.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
violations = re.findall(r'\[([^\]]+)\]:\s+([^\n]+)', text)
counts = {}
for code, desc in violations:
    counts[code] = counts.get(code, 0) + 1

print(f"Total violations in Git HEAD: {len(violations)}")
for code, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  [{code}]: {count}")


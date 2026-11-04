with open('drc_clean_v25.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
violations = re.findall(r'\[([^\]]+)\]:\s+([^\n]+)', text)
counts = {}
for code, desc in violations:
    counts[code] = counts.get(code, 0) + 1

print(f"Total violations: {len(violations)}")
for code, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  [{code}]: {count}")

print("\nSample violations:")
for code, desc in violations[:15]:
    print(f"  [{code}]: {desc}")


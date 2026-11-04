with open('drc_master_v30.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
violations = re.findall(r'\[([^\]]+)\]:\s+([^\n]+)', text)
counts = {}
for code, desc in violations:
    counts[code] = counts.get(code, 0) + 1

print(f"Total violations in master v30: {len(violations)}")
for code, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  [{code}]: {count}")

print("\nSample shorting/crossing/clearance violations:")
for code, desc in violations:
    if code in ['shorting_items', 'tracks_crossing', 'clearance']:
        print(f"  [{code}]: {desc}")


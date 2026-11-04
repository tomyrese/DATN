with open('drc_v20.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Split sections
sections = re.findall(r'\*\* (Found [^\*]+) \*\*', text)
print("Sections found:", sections)

# Find unique violation types
types = re.findall(r'\[([^\]]+)\]:\s*([^\n]+)', text)
type_counts = {}
for t, desc in types:
    type_counts[t] = type_counts.get(t, 0) + 1

print("\nViolation types:")
for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  [{t}]: {c} occurrences")

print("\nFirst 10 violations details:")
blocks = text.split('\n\n')
for b in blocks[:15]:
    if '[' in b:
        print("---")
        print(b.strip())


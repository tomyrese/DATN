with open('drc_final_report.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
violations = re.findall(r'\[([^\]]+)\]:\s*([^\n]+)', text)
counts = {}
for code, desc in violations:
    key = f"[{code}] {desc}"
    counts[key] = counts.get(key, 0) + 1

print("DRC Violations Summary:")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Print first 5 violations of each type
print("\nSample Details:")
for code in set([c[0] for c in violations]):
    print(f"\n--- Code: {code} ---")
    matches = re.findall(rf'\[{code}\]:[^\n]*\n(?:[ \t]+[^\n]*\n){{1,4}}', text)
    for m in matches[:3]:
        print(m.strip())


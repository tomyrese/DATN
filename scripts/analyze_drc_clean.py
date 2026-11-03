import re

with open('drc_clean.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

# KiCad reports violations like:
# [rule_type]: message
#     severity
#     item 1
#     item 2

items = re.findall(r'\[([a-zA-Z0-9_]+)\]:\s*([^\n]+)', text)
counts = {}
for rule, msg in items:
    counts[rule] = counts.get(rule, 0) + 1

print(f"Total violations found: {len(items)}")
for k, v in sorted(counts.items()):
    print(f"  {k}: {v}")

print("\nSample of violations by type:")
seen = set()
for rule, msg in items:
    if rule not in seen:
        seen.add(rule)
        print(f"\n--- {rule} ---")
        print(msg)

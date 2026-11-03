with open('drc_final_v16.rpt', 'r', encoding='utf-8') as f:
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

print("\n--- Unconnected items ---")
unconn = re.findall(r'\[unconnected_items\]:[^\n]*\n(?:[ \t]+[^\n]*\n){1,3}', text)
for u in unconn:
    print(u.strip())

print("\n--- Other Errors (non-silk) ---")
non_silk = [m for m in re.findall(r'\[([^\]]+)\]:[^\n]*\n(?:[ \t]+[^\n]*\n){1,3}', text) if 'silk' not in m[0].lower()]
for m in non_silk[:10]:
    print(m.strip() if isinstance(m, str) else m)

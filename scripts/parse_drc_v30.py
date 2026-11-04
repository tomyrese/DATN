import re
from collections import defaultdict

with open('drc_v30.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all violations by type
violations = re.findall(r'\*\*\s+Found\s+\d+\s+DRC\s+violations\s+\*\*(.*?)\*\*\s+Found', text, re.DOTALL)
if violations:
    v_text = violations[0]
else:
    v_text = text

v_types = defaultdict(list)
entries = re.split(r'\[(.*?)\]:\s+', v_text)
# entries[0] is header, then pairs of (type, body)
for i in range(1, len(entries), 2):
    t = entries[i]
    b = entries[i+1].strip()
    v_types[t].append(b[:120].replace('\n', ' '))

print("DRC Violations Summary:")
for t, lst in sorted(v_types.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  [{t}]: {len(lst)} occurrences")
    for sample in lst[:3]:
        print(f"    sample: {sample}")

# Check unconnected
unconnected = re.findall(r'\*\*\s+Found\s+\d+\s+unconnected\s+items\s+\*\*(.*)', text, re.DOTALL)
if unconnected:
    u_entries = re.findall(r'\[(.*?)\b.*?\]:\s+(.*?)(?=\n\[|\Z)', unconnected[0], re.DOTALL)
    print(f"\nUnconnected items ({len(u_entries)}):")
    for ut, ub in u_entries[:10]:
        print(f"  [{ut}]: {ub.strip()[:100].replace(chr(10), ' ')}")


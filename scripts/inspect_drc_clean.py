with open('drc_clean_v25.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
print(f"Total lines in drc_clean_v25.rpt: {len(lines)}")
print("\n".join(lines[:20]))
print("...")
print("\n".join(lines[-20:]))


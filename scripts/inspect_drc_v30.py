with open('drc_v30.rpt', 'r', encoding='utf-8') as f:
    text = f.read()
print(f"Length of drc_v30.rpt: {len(text)}")
lines = text.splitlines()
print("\n".join(lines[:35]))
print("...")
print("\n".join(lines[-20:]))


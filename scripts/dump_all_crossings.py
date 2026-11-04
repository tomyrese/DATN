with open('Pi4_Robot_Carrier_1Layer-drc.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines):
    if '[tracks_crossing]' in line or '[shorting_items]' in line:
        print(f"--- Line {i+1} ---")
        print("\n".join(lines[i:i+6]))


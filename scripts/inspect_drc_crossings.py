with open('Pi4_Robot_Carrier_1Layer-drc.rpt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '[tracks_crossing]' in line or '[shorting_items]' in line:
        print("".join(lines[i:i+6]))

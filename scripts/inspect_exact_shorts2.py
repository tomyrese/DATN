with open('drc_master_v30.rpt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[:100]):
    if '[shorting_items]' in l or '[tracks_crossing]' in l:
        print("".join(lines[i:i+8]))
        print("="*50)


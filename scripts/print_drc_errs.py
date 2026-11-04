with open('Pi4_Robot_Carrier_1Layer-drc.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
entries = text.split('\n\n')
for e in entries:
    if '[shorting_items]' in e:
        print('=== SHORT ===')
        print(e.strip())
        print()
    elif '[tracks_crossing]' in e:
        print('=== CROSSING ===')
        print(e.strip())
        print()


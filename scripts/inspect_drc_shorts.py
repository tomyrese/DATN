with open('drc_industrial_test.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
blocks = text.split('\n\n')
short_blocks = [b for b in blocks if '[shorting_items]' in b or '[tracks_crossing]' in b]
print(f"Total short/crossing blocks: {len(short_blocks)}")
for b in short_blocks[:15]:
    print("--------------------------------------------------")
    print(b.strip())

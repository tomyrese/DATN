import re

with open('drc_clean.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

entries = text.split('\n\n')
for entry in entries:
    if '[shorting_items]' in entry or '[track_dangling]' in entry:
        print("--------------------------------------------------")
        print(entry.strip())


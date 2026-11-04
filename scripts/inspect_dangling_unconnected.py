import re

with open('drc_clean2.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

entries = text.split('\n\n')
for entry in entries:
    if '[track_dangling]' in entry or '[unconnected_items]' in entry:
        print("--------------------------------------------------")
        print(entry.strip())


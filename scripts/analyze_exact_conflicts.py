with open('Pi4_Robot_Carrier_1Layer-drc.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'\[tracks_crossing\]: Tracks crossing\s+Local override; error\s+@\(([^)]+)\): Track \[([^\]]+)\] on B.Cu[^\n]+\s+@\(([^)]+)\): Track \[([^\]]+)\] on B.Cu', text)

print(f"Total crossing pairs: {len(matches)}")
for idx, (p1, n1, p2, n2) in enumerate(matches):
    print(f"{idx+1:2d}. {n1:15} at {p1}  <--->  {n2:15} at {p2}")


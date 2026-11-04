import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

refs = re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', text)
print(f"Total references: {len(refs)}")
from collections import Counter
counts = Counter(refs)
duplicates = {k: v for k, v in counts.items() if v > 1}
print("Duplicate references:", duplicates)


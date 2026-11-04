with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
labels = re.findall(r'\(label\s+"(M[1-4]_[AB])"\s+\(at\s+([\d\.-]+)\s+([\d\.-]+)\s+([\d\.-]+)\)', text)
for l in labels:
    print(f"Label {l[0]} at ({l[1]}, {l[2]}), rot={l[3]}")


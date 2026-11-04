with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+[\s\S]*?\n\t\)', text)
if m:
    print("Sample placed symbol in bak:")
    print(m.group(0)[:500])


with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

import re
matches = [m.start() for m in re.finditer(r'VM_MOTOR', sch)]
print(f"Found {len(matches)} occurrences of VM_MOTOR in sch:")
for m in matches:
    print(sch[m-60:m+100])
    print('---')


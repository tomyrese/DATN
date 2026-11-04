with open('scripts/build_flawless_pcb.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Length:", len(text))
idx = text.find('jumper')
if idx != -1:
    print(text[idx-50:idx+400])

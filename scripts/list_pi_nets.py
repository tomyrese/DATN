with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('"Rasp_PI4"')
# find the footprint enclosing Rasp_PI4
# find '(' before pos
start = text.rfind('(footprint', 0, pos)
# find matching closing parenthesis for this footprint
count = 0
end = start
for i in range(start, len(text)):
    if text[i] == '(':
        count += 1
    elif text[i] == ')':
        count -= 1
        if count == 0:
            end = i + 1
            break

fp_pi = text[start:end]

pads = re.findall(r'\(pad\s+"(\d+)"[^\n]*[\s\S]*?\(net\s+"([^"]+)"\)', fp_pi)
for p, net in sorted([(int(p), net) for p, net in pads]):
    print(f"Pi Pin {p:2d}: {net}")

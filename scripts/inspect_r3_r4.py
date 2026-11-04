with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

for r in ['R3', 'R4']:
    pos = text.find(f'reference "{r}"')
    block = text[pos-100:pos+2500]
    import re
    pads = re.findall(r'\(pad\s+"(\d+)"[^\n]*[\s\S]*?\(net\s+"([^"]+)"\)', block)
    print(r, pads)


with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

idx = 0
while True:
    pos = text.find('"Edge.Cuts"', idx)
    if pos == -1:
        break
    start = text.rfind('(gr_line', 0, pos)
    end = text.find('\n\t)', pos)
    print(text[start:end+3])
    print('---')
    idx = pos + 10

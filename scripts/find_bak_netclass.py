with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('(net_class ')
if idx != -1:
    print(text[idx:idx+400])
else:
    print("net_class not found, looking for (net ")
    idx2 = text.find('(net ')
    print(text[idx2:idx2+400])


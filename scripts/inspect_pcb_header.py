with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect everything before the first footprint
first_fp = text.find('(footprint ')
print("=== HEADER & SETUP ===")
print(text[:first_fp])


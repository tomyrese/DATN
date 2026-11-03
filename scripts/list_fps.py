import sys, re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's see the footprint references and their locations
fps = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', text)
for fp in fps:
    print(f"FP {fp[1]:15s}: at ({fp[2]}, {fp[3]}) rot={fp[4]}")

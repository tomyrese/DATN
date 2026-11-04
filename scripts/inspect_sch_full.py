import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# Extract all symbol references and values
symbols = re.findall(r'\(symbol\s+[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(property\s+"Value"\s+"([^"]+)"[\s\S]*?\(property\s+"Footprint"\s+"([^"]*)"', sch)
print(f"Total symbols found in schematic: {len(symbols)}")
for ref, val, fp in sorted(symbols, key=lambda x: x[0]):
    print(f"  {ref:>12}: {val:<25} footprint: {fp}")

# Extract labels
labels = sorted(list(set(re.findall(r'\(label\s+"([^"]+)"', sch))))
print(f"\nTotal labels found: {len(labels)}")
for l in labels:
    print(f"  {l}")

# Extract global labels / hierarchical labels / power
glabels = sorted(list(set(re.findall(r'\(global_label\s+"([^"]+)"', sch))))
print(f"\nGlobal labels: {glabels}")


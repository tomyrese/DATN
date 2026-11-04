with open('robot_electronics.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

import re

# Find wires connected to R3
# Look for R3 symbol pin positions
idx = sch.find('"R3"')
start = sch.rfind('(symbol', 0, idx)
end = sch.find('\n  )', idx)
block = sch[start:end+4]
print("R3 block:")
print(block)


with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re

# Find all top-level tokens in kicad_pcb
# In KiCad PCB format:
# (kicad_pcb ...
#   (version ...)
#   (generator ...)
#   (general ...)
#   (paper ...)
#   (layers ...)
#   (setup ...)
#   (net ...)
#   (footprint ...)
#   (gr_line ...)
#   (gr_text ...)
#   (segment ...)
#   (via ...)
# )

# Let's see the balance of parentheses in bak
open_count = bak.count('(')
close_count = bak.count(')')
print(f"bak: '('={open_count}, ')'={close_count}")

# Check where the first (segment or (via occurs in bak
seg_pos = bak.find('(segment')
via_pos = bak.find('(via')
first_pos = min(p for p in [seg_pos, via_pos] if p != -1)
print(f"First track/via at character {first_pos}")

# What comes before first track/via?
print("Before first track/via (last 200 chars):")
print(bak[first_pos-200:first_pos])

import uuid
import math
import re

def u():
    return str(uuid.uuid4())

# Load footprints from libraries/robot_electronics.pretty
def load_mod(name):
    path = f'libraries/robot_electronics.pretty/{name}.kicad_mod'
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

print("Testing footprint loading:")
for m in ['Module_TB6612FNG_Breakout', 'PinSocket_2x20_P2.54mm_Vertical', 'CP_Radial_D8.0mm_P3.50mm', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal']:
    content = load_mod(m)
    print(f"  {m}: {len(content)} chars")


import uuid
import re

def make_uuid():
    return str(uuid.uuid4())

# Load original lib_symbols from Pi4_Robot_Carrier_1Layer.kicad_sch
with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    orig_sch = f.read()

# Extract lib_symbols block exactly
m_lib = re.search(r'\(lib_symbols[\s\S]*?\n  \)', orig_sch)
if not m_lib:
    raise ValueError("lib_symbols block not found!")
lib_symbols_str = m_lib.group(0)

print(f"Extracted lib_symbols ({len(lib_symbols_str)} chars)")


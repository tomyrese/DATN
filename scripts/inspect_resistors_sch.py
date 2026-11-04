import re

with open('robot_electronics.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

for ref in ['R1', 'R2', 'R3', 'R4']:
    idx = sch.find(f'(property "Reference" "{ref}"')
    if idx != -1:
        # find the full symbol block
        start = sch.rfind('(symbol', 0, idx)
        end = sch.find('\n  )', idx)
        block = sch[start:end+4]
        print(f"=== {ref} ===")
        # find pins and their connections or at least coordinates
        pins = re.findall(r'\(pin\s+"([^"]+)"\s+\(uuid\s+"([^"]+)"\)', block)
        print("Pins:", pins)
        at_m = re.findall(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)', block)
        print("At:", at_m[:2])


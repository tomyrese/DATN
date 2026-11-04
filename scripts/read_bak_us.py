import re

# Find bak file
import glob
baks = glob.glob('*.bak') + glob.glob('*.kicad_pcb-bak')
print("Bak files:", baks)

bak_file = 'Pi4_Robot_Carrier_1Layer.kicad_pcb-bak' if 'Pi4_Robot_Carrier_1Layer.kicad_pcb-bak' in baks else (baks[0] if baks else None)
if bak_file:
    with open(bak_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all segments for TRIG_L and Net-(U_US1-ECHO)
    for net in ['/TRIG_L', 'Net-(U_US1-ECHO)', '/ECHO_L', '/TRIG_R', 'Net-(U_US2-ECHO)', '/ECHO_R']:
        segs = re.findall(r'\(segment\s+\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)[\s\S]*?\(net\s+"' + re.escape(net) + r'"\)', content)
        print(f"Net {net} in bak has {len(segs)} segments:")
        for s in segs[:8]:
            print(f"  ({float(s[0]):.2f}, {float(s[1]):.2f}) -> ({float(s[2]):.2f}, {float(s[3]):.2f})")


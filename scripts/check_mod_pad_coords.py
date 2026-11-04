# Check footprint pad definitions in libraries/robot_electronics.pretty
import re

def parse_mod_pads(mod_path):
    with open(mod_path, 'r', encoding='utf-8') as f:
        text = f.read()
    pads = {}
    for m in re.finditer(r'\(pad\s+"?(\w+)"?\s+([^\s]+)\s+([^\s]+)\s+\(at\s+([\d\.-]+)\s+([\d\.-]+)(?:\s+([\d\.-]+))?\)\s+\(size\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(drill\s+([\d\.-]+)\)', text):
        pnum = m.group(1)
        ptype = m.group(2)
        pshape = m.group(3)
        px = float(m.group(4))
        py = float(m.group(5))
        prot = float(m.group(6) or 0)
        sx = float(m.group(7))
        sy = float(m.group(8))
        drill = float(m.group(9))
        pads[pnum] = {
            'local': [px, py, prot],
            'size': [sx, sy],
            'drill': drill
        }
    return pads

tb_pads = parse_mod_pads('libraries/robot_electronics.pretty/Module_TB6612FNG_Breakout.kicad_mod')
print("Module_TB6612FNG_Breakout pad count:", len(tb_pads))
pi_pads = parse_mod_pads('libraries/robot_electronics.pretty/PinSocket_2x20_P2.54mm_Vertical.kicad_mod')
print("PinSocket_2x20_P2.54mm_Vertical pad count:", len(pi_pads))
r_pads = parse_mod_pads('libraries/robot_electronics.pretty/R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal.kicad_mod')
print("R_Axial pad count:", len(r_pads), r_pads)
c_pads = parse_mod_pads('libraries/robot_electronics.pretty/CP_Radial_D8.0mm_P3.50mm.kicad_mod')
print("C 8mm pad count:", len(c_pads), c_pads)
oled_pads = parse_mod_pads('libraries/robot_electronics.pretty/Sensor_OLED_1.3.kicad_mod')
print("OLED pad count:", len(oled_pads), oled_pads)


import re
import math

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

def inspect_fp(ref):
    # Match footprint block
    # Each footprint starts with (footprint and ends with matching closing
    # Let's find by property Reference
    pattern = r'\(footprint\s+"[^\"]*"[\s\S]*?\(property\s+"Reference"\s+"' + ref + r'"[\s\S]*?\n\t\)'
    m = re.search(pattern, text)
    if not m:
        print(f"FP {ref} not found!")
        return
    fp_text = m.group(0)
    
    # get fp (at X Y [ROT])
    at_m = re.search(r'\(at\s+([\d\.-]+)\s+([\d\.-]+)(?:\s+([\d\.-]+))?\)', fp_text)
    fp_x, fp_y, fp_rot = float(at_m.group(1)), float(at_m.group(2)), float(at_m.group(3) or 0)
    print(f"\nFootprint {ref}: at ({fp_x}, {fp_y}), rot={fp_rot}")
    
    # get pads
    pads = re.findall(r'\(pad\s+"?(\w+)"?\s+([^\s]+)\s+([^\s]+)\s+\(at\s+([\d\.-]+)\s+([\d\.-]+)(?:\s+([\d\.-]+))?\)[\s\S]*?\(net\s+"?([^"\)\s]+)"?\)', fp_text)
    for pnum, ptype, pshape, px, py, prot, net in pads:
        # calculate world pos with rot
        rad = math.radians(fp_rot)
        # Note: KiCad rotation is clockwise or counter-clockwise?
        # In KiCad screen coords (Y down), positive rotation rotates +X towards +Y (clockwise).
        # x' = x*cos(a) - y*sin(a)
        # y' = x*sin(a) + y*cos(a)
        wx = fp_x + float(px) * math.cos(rad) - float(py) * math.sin(rad)
        wy = fp_y + float(px) * math.sin(rad) + float(py) * math.cos(rad)
        print(f"  Pad {pnum:>2}: local=({float(px):>6.2f}, {float(py):>6.2f}) -> world=({wx:>7.2f}, {wy:>7.2f}) | net={net}")

inspect_fp('LEFT')
inspect_fp('RIGHT')

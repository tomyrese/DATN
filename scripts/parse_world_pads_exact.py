import math
import re
import json

def parse_pcb_world_pads(pcb_path):
    with open(pcb_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Parse net mapping
    nets = {}
    for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]+)"\)', text):
        nets[int(m.group(1))] = m.group(2)

    # Footprints
    fps = {}
    # Split by footprint
    fp_matches = re.finditer(r'\(footprint\s+"([^"]+)".*?\n\t\)', text, re.DOTALL)
    for fm in fp_matches:
        fp_str = fm.group(0)
        # Ref
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_str)
        if not ref_m: continue
        ref = ref_m.group(1)

        # at pos and rot
        at_m = re.search(r'^\t\t\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', fp_str, re.MULTILINE)
        if not at_m: continue
        fx, fy = float(at_m.group(1)), float(at_m.group(2))
        frot = float(at_m.group(3)) if at_m.group(3) else 0.0

        rad = math.radians(frot)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        pads = {}
        for pm in re.finditer(r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)\s+\(size\s+([-\d.]+)\s+([-\d.]+)\)\s+\(drill\s+([-\d.]+)\).*?\(net\s+(\d+)\s+"([^"]+)"\)', fp_str):
            pnum = pm.group(1)
            lx, ly = float(pm.group(4)), float(pm.group(5))
            # KiCad rotation is clockwise for positive angles in screen coords (y down)
            # x_w = fx + lx*cos - ly*sin
            # y_w = fy + lx*sin + ly*cos
            wx = round(fx + lx * cos_a - ly * sin_a, 4)
            wy = round(fy + lx * sin_a + ly * cos_a, 4)
            net_id = int(pm.group(10))
            net_name = pm.group(11)
            pads[pnum] = {
                'wx': wx, 'wy': wy,
                'lx': lx, 'ly': ly,
                'net_id': net_id,
                'net_name': net_name,
                'size': (float(pm.group(7)), float(pm.group(8))),
                'drill': float(pm.group(9))
            }
        fps[ref] = {
            'fp_name': fm.group(1),
            'at': (fx, fy),
            'rot': frot,
            'pads': pads
        }
    return fps

if __name__ == '__main__':
    fps = parse_pcb_world_pads('Pi4_Robot_Carrier_1Layer.kicad_pcb')
    print(f"Parsed {len(fps)} footprints.")
    for ref, d in sorted(fps.items()):
        print(f"{ref:8s}: at ({d['at'][0]:.2f}, {d['at'][1]:.2f}) rot={d['rot']} ({len(d['pads'])} pads)")
    with open('scripts/parsed_world_pads.json', 'w', encoding='utf-8') as f:
        json.dump(fps, f, indent=2)

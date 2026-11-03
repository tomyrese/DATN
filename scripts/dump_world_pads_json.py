import math, json

# Exact pad definitions in local coordinates
# We get local coordinates from the footprints in the clean PCB
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

from parse_pcb_sexpr import parse_sexpr
tree = parse_sexpr(text)

world_pads = {}

fp_rots = {
    "Rasp_PI4": 0,
    "LEFT": 90,
    "RIGHT": 90,
    "HC_SR04_1": 0,
    "HC_SR04_2": 0,
    "MOTOR1": 0,
    "MOTOR2": 0,
    "MOTOR3": 0,
    "MOTOR4": 0,
    "TCRT5000": 180,
    "OLED": 180,
    "R1": 0,
    "R2": 180,
    "R3": 180,
    "R4": 0
}

fp_locs = {
    "Rasp_PI4": (103.19, 94.8275),
    "LEFT": (67.69, 68.8275),
    "RIGHT": (140.69, 68.8275),
    "HC_SR04_1": (90.19, 50.4425),
    "HC_SR04_2": (118.415917, 50.513844),
    "MOTOR1": (67.67802, 53.400498),
    "MOTOR2": (76.8, 53.4425),
    "MOTOR3": (139.8, 53.9425),
    "MOTOR4": (150.8, 53.9425),
    "TCRT5000": (104.46, 50.4425),
    "OLED": (148.31, 96.5),
    "R1": (93.03, 65.9425),
    "R2": (92.99, 72.4425),
    "R3": (120.934925, 61.435956),
    "R4": (120.97, 65.445234)
}

def to_w(ref, lx, ly):
    fx, fy = fp_locs[ref]
    rot = fp_rots[ref]
    rad = math.radians(rot)
    xw = fx + lx * math.cos(rad) + ly * math.sin(rad)
    yw = fy - lx * math.sin(rad) + ly * math.cos(rad)
    return round(xw, 4), round(yw, 4)

for item in tree:
    if isinstance(item, list) and len(item) > 0 and item[0] == 'footprint':
        ref = None
        for prop in item:
            if isinstance(prop, list) and len(prop) > 0 and prop[0] == 'property' and prop[1] == 'Reference':
                ref = prop[2]
        if ref and ref in fp_locs:
            world_pads[ref] = {}
            for prop in item:
                if isinstance(prop, list) and len(prop) > 0 and prop[0] == 'pad':
                    pad_num = prop[1]
                    lx, ly = 0, 0
                    net = ""
                    for p_attr in prop:
                        if isinstance(p_attr, list) and len(p_attr) > 0:
                            if p_attr[0] == 'at':
                                lx, ly = float(p_attr[1]), float(p_attr[2])
                            elif p_attr[0] == 'net':
                                net = p_attr[2] if len(p_attr) > 2 else p_attr[1]
                    wx, wy = to_w(ref, lx, ly)
                    world_pads[ref][pad_num] = {
                        "x": wx,
                        "y": wy,
                        "net": net
                    }

with open('scripts/world_pads.json', 'w', encoding='utf-8') as f:
    json.dump(world_pads, f, indent=2)

print("Saved scripts/world_pads.json")

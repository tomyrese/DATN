import re, sys
sys.path.append('scripts')
from generate_final_pcb import gen_uuid
from test_fp_swap import swap_tb6612_rows, mirror_pi4_header
from solve_planar_pcb_v16 import paths

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

first_seg = bak.find('(segment')
base_part = bak[:first_seg]

def update_tb_footprint(fp_text, is_left=True):
    fp_text = swap_tb6612_rows(fp_text)
    prefix = "_L" if is_left else "_R"
    m_pref = "1" if is_left else "3"
    m_pref2 = "2" if is_left else "4"
    nets = {
        "1": f"/PWMA{prefix}",
        "2": f"/AIN2{prefix}",
        "3": f"/AIN1{prefix}",
        "4": f"/STBY{prefix}",
        "5": f"/AIN1{prefix}",
        "6": f"/AIN2{prefix}",
        "7": f"/PWMA{prefix}",
        "8": "GND",
        "9": "/VM_MOTOR",
        "10": "/+5V_PWR",
        "11": "GND",
        "12": f"/M{m_pref}_A",
        "13": f"/M{m_pref}_B",
        "14": f"/M{m_pref2}_B",
        "15": f"/M{m_pref2}_A",
        "16": "GND"
    }
    for pad_num, net_name in nets.items():
        fp_text = re.sub(rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"', rf'\1"{net_name}"', fp_text)
    return fp_text

def update_pi_footprint(fp_text):
    fp_text = mirror_pi4_header(fp_text)
    pi_nets = {
        "37": "/PWMA_L",
        "35": "/AIN2_L",
        "33": "/AIN1_L",
        "38": "/STBY_L",
        "31": "/TRIG_L",
        "29": "/ECHO_L",
        "3": "/PWMA_R",
        "5": "/AIN2_R",
        "7": "/AIN1_R",
        "11": "/STBY_R",
        "15": "/TRIG_R",
        "13": "/ECHO_R",
        "19": "/LINE_L",
        "21": "/LINE_C",
        "23": "/LINE_R",
        "27": "/I2C_SDA",
        "28": "/I2C_SCL",
        "2": "/+5V_PWR",
        "4": "/+5V_PWR",
        "6": "GND",
        "9": "GND",
        "14": "GND",
        "20": "GND",
        "25": "GND",
        "30": "GND",
        "34": "GND",
        "39": "GND",
        "17": "/+3V3_LOGIC"
    }
    for pad_num, net_name in pi_nets.items():
        fp_text = re.sub(rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"', rf'\1"{net_name}"', fp_text)
    return fp_text

def update_tcrt_footprint(fp_text):
    tcrt_nets = {
        "1": "GND",
        "2": "/+3V3_LOGIC",
        "3": "/LINE_L",
        "4": "/LINE_C",
        "5": "/LINE_R"
    }
    for pad_num, net_name in tcrt_nets.items():
        fp_text = re.sub(rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"', rf'\1"{net_name}"', fp_text)
    return fp_text

def update_resistor_nets(fp_text, ref):
    if ref == 'R1':
        fp_text = re.sub(r'(\(pad\s+"1"[\s\S]*?\(net\s+)"[^"]*"', r'\1"Net-(U_US1-ECHO)"', fp_text)
        fp_text = re.sub(r'(\(pad\s+"2"[\s\S]*?\(net\s+)"[^"]*"', r'\1"/ECHO_L"', fp_text)
    elif ref == 'R2':
        fp_text = re.sub(r'(\(pad\s+"1"[\s\S]*?\(net\s+)"[^"]*"', r'\1"/ECHO_L"', fp_text)
        fp_text = re.sub(r'(\(pad\s+"2"[\s\S]*?\(net\s+)"[^"]*"', r'\1"GND"', fp_text)
    elif ref == 'R3':
        fp_text = re.sub(r'(\(pad\s+"1"[\s\S]*?\(net\s+)"[^"]*"', r'\1"/ECHO_R"', fp_text)
        fp_text = re.sub(r'(\(pad\s+"2"[\s\S]*?\(net\s+)"[^"]*"', r'\1"Net-(U_US2-ECHO)"', fp_text)
    elif ref == 'R4':
        fp_text = re.sub(r'(\(pad\s+"1"[\s\S]*?\(net\s+)"[^"]*"', r'\1"GND"', fp_text)
        fp_text = re.sub(r'(\(pad\s+"2"[\s\S]*?\(net\s+)"[^"]*"', r'\1"/ECHO_R"', fp_text)
    return fp_text

def fp_repl(m):
    fp = m.group(0)
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp)
    ref = ref_m.group(1) if ref_m else ""
    if ref == 'LEFT':
        return update_tb_footprint(fp, is_left=True)
    elif ref == 'RIGHT':
        return update_tb_footprint(fp, is_left=False)
    elif ref == 'Rasp_PI4':
        return update_pi_footprint(fp)
    elif ref == 'TCRT5000':
        return update_tcrt_footprint(fp)
    elif ref in ['R1', 'R2', 'R3', 'R4']:
        return update_resistor_nets(fp, ref)
    return fp

base_part = re.sub(r'\(footprint\s+"[^"]+"[\s\S]*?\n\t\)', fp_repl, base_part)

segments = []
vias = []
silk_items = []

def make_segment(x1, y1, x2, y2, width, net, layer="B.Cu"):
    return f"""\t(segment
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{gen_uuid()}")
\t)\n"""

def make_via(x, y, net, size=1.6, drill=0.8):
    return f"""\t(via
\t\t(at {x:.4f} {y:.4f})
\t\t(size {size})
\t\t(drill {drill})
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "{net}")
\t\t(uuid "{gen_uuid()}")
\t)\n"""

def make_silk_jumper(x1, y1, x2, y2, label):
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2 - 1.2
    return f"""\t(gr_line
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t)
\t(gr_circle
\t\t(center {x1:.4f} {y1:.4f})
\t\t(end {x1+0.9:.4f} {y1:.4f})
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t)
\t(gr_circle
\t\t(center {x2:.4f} {y2:.4f})
\t\t(end {x2+0.9:.4f} {y2:.4f})
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t)
\t(gr_text "{label}"
\t\t(at {mid_x:.4f} {mid_y:.4f})
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)\n"""

# Add all segments on B.Cu
for s in paths:
    segments.append(make_segment(s['p1'][0], s['p1'][1], s['p2'][0], s['p2'][1], s['width'], s['net'], layer="B.Cu"))

# Top Wire Jumpers (NO F.Cu copper tracks - strictly through-hole vias + silkscreen lines)
jumpers = [
    ("JMP1_SDA", "/I2C_SDA", (94.30, 87.00), (144.50, 87.00), "JMP1: SDA (Wire 50mm)"),
    ("JMP2_SCL", "/I2C_SCL", (94.30, 99.00), (147.04, 99.00), "JMP2: SCL (Wire 53mm)"),
    ("JMP3_3V3", "/+3V3_LOGIC", (107.00, 84.00), (152.12, 88.00), "JMP3: 3V3 (Wire 45mm)"),
    ("JMP4_STBY_L", "/STBY_L", (66.42, 58.00), (81.60, 99.00), "JMP4: STBY_L (Wire 44mm)"),
    ("JMP5_STBY_R", "/STBY_R", (139.42, 58.00), (114.62, 85.00), "JMP5: STBY_R (Wire 37mm)"),
    ("JMP6_VM", "/VM_MOTOR", (58.80, 74.00), (131.80, 74.00), "JMP6: VM_MOTOR (Wire 73mm)"),
    ("JMP7_ECHO_R", "/ECHO_R", (124.78, 67.50), (112.08, 88.00), "JMP7: ECHO_R (Wire 24mm)"),
    ("JMP8_GND_R", "GND", (149.58, 69.00), (149.58, 90.00), "JMP8: GND_R (Wire 21mm)"),
    ("JMP9_GND_PI", "GND", (96.84, 89.00), (96.84, 99.00), "JMP9: GND_PI (Wire 10mm)"),
    ("JMP10_5V_L", "/+5V_PWR", (61.34, 43.50), (61.34, 74.00), "JMP10: 5V_L (Wire 30mm)"),
    ("JMP11_5V_R", "/+5V_PWR", (127.32, 99.00), (134.34, 74.00), "JMP11: 5V_R (Wire 26mm)"),
    ("JMP12_GND_TOP", "GND", (94.00, 73.50), (91.76, 99.00), "JMP12: GND_TOP (Wire 26mm)"),
    ("JMP13_GND_US2", "GND", (128.00, 50.00), (136.88, 73.00), "JMP13: GND_US2 (Wire 25mm)")
]

for name, net, v1, v2, label in jumpers:
    vias.append(make_via(v1[0], v1[1], net))
    vias.append(make_via(v2[0], v2[1], net))
    silk_items.append(make_silk_jumper(v1[0], v1[1], v2[0], v2[1], label))

clean_pcb = base_part + "".join(vias) + "".join(segments) + "".join(silk_items) + "\t(embedded_fonts no)\n)\n"

with open('Pi4_Robot_Carrier_1Layer_clean.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(clean_pcb)

print("Wrote Pi4_Robot_Carrier_1Layer_clean.kicad_pcb with updated resistor properties.")

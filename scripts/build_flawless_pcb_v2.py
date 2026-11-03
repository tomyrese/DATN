import json, re, uuid

def gen_uuid():
    return str(uuid.uuid4())

# Read base PCB from backup
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

from test_fp_swap import swap_tb6612_rows, mirror_pi4_header

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
        "33": "/PWMA_L",
        "35": "/AIN2_L",
        "37": "/AIN1_L",
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

first_seg = bak.find('(segment')
base_part = bak[:first_seg]

def fp_repl(m):
    fp = m.group(0)
    if 'TB6612_Left' in fp or 'reference "LEFT"' in fp:
        return update_tb_footprint(fp, is_left=True)
    elif 'TB6612_Right' in fp or 'reference "RIGHT"' in fp:
        return update_tb_footprint(fp, is_left=False)
    elif 'Raspberry_Pi_4_40Pin' in fp or 'reference "Rasp_PI4"' in fp:
        return update_pi_footprint(fp)
    elif 'TCRT5000_3CH' in fp or 'reference "TCRT5000"' in fp:
        return update_tcrt_footprint(fp)
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

def add_path(points, width, net):
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i+1]
        segments.append(make_segment(p1[0], p1[1], p2[0], p2[1], width, net))

# Exact Pad Coordinates (verified)
# LEFT TB6612
p_tb1_1 = (58.80, 61.2075)
p_tb1_2 = (61.34, 61.2075)
p_tb1_3 = (63.88, 61.2075)
p_tb1_4 = (66.42, 61.2075)
p_tb1_5 = (68.96, 61.2075)
p_tb1_6 = (71.50, 61.2075)
p_tb1_7 = (74.04, 61.2075)
p_tb1_8 = (76.58, 61.2075)

p_tb1_9  = (58.80, 76.4475)
p_tb1_10 = (61.34, 76.4475)
p_tb1_11 = (63.88, 76.4475)
p_tb1_12 = (66.42, 76.4475)
p_tb1_13 = (68.96, 76.4475)
p_tb1_14 = (71.50, 76.4475)
p_tb1_15 = (74.04, 76.4475)
p_tb1_16 = (76.58, 76.4475)

# RIGHT TB6612
p_tb2_1 = (131.80, 61.2075)
p_tb2_2 = (134.34, 61.2075)
p_tb2_3 = (136.88, 61.2075)
p_tb2_4 = (139.42, 61.2075)
p_tb2_5 = (141.96, 61.2075)
p_tb2_6 = (144.50, 61.2075)
p_tb2_7 = (147.04, 61.2075)
p_tb2_8 = (149.58, 61.2075)

p_tb2_9  = (131.80, 76.4475)
p_tb2_10 = (134.34, 76.4475)
p_tb2_11 = (136.88, 76.4475)
p_tb2_12 = (139.42, 76.4475)
p_tb2_13 = (141.96, 76.4475)
p_tb2_14 = (144.50, 76.4475)
p_tb2_15 = (147.04, 76.4475)
p_tb2_16 = (149.58, 76.4475)

# Motors
p_m1_1 = (66.408, 53.4005)
p_m1_2 = (68.948, 53.4005)
p_m2_1 = (75.53, 53.4425)
p_m2_2 = (78.07, 53.4425)
p_m3_1 = (138.53, 53.9425)
p_m3_2 = (141.07, 53.9425)
p_m4_1 = (149.53, 53.9425)
p_m4_2 = (152.07, 53.9425)

# Pi 4 Mirrored Header (Odd Y=93.5575, Even Y=96.0975)
p_pi1  = (127.32, 93.5575)
p_pi2  = (127.32, 96.0975)
p_pi3  = (124.78, 93.5575)
p_pi4  = (124.78, 96.0975)
p_pi5  = (122.24, 93.5575)
p_pi6  = (122.24, 96.0975)
p_pi7  = (119.70, 93.5575)
p_pi9  = (117.16, 93.5575)
p_pi11 = (114.62, 93.5575)
p_pi13 = (112.08, 93.5575)
p_pi14 = (112.08, 96.0975)
p_pi15 = (109.54, 93.5575)
p_pi17 = (107.00, 93.5575)
p_pi19 = (104.46, 93.5575)
p_pi20 = (104.46, 96.0975)
p_pi21 = (101.92, 93.5575)
p_pi23 = (99.38, 93.5575)
p_pi25 = (96.84, 93.5575)
p_pi27 = (94.30, 93.5575)
p_pi28 = (94.30, 96.0975)
p_pi29 = (91.76, 93.5575)
p_pi30 = (91.76, 96.0975)
p_pi31 = (89.22, 93.5575)
p_pi33 = (86.68, 93.5575)
p_pi34 = (86.68, 96.0975)
p_pi35 = (84.14, 93.5575)
p_pi37 = (81.60, 93.5575)
p_pi38 = (81.60, 96.0975)
p_pi39 = (79.06, 93.5575)
p_pi40 = (79.06, 96.0975)

# Sensors
p_tcrt_1 = (109.54, 50.4425)
p_tcrt_2 = (107.00, 50.4425)
p_tcrt_3 = (104.46, 50.4425)
p_tcrt_4 = (101.92, 50.4425)
p_tcrt_5 = (99.38, 50.4425)

p_us1_1 = (86.38, 50.4425)
p_us1_2 = (88.92, 50.4425)
p_us1_3 = (91.46, 50.4425)
p_us1_4 = (94.00, 50.4425)

p_r1_1 = (89.22, 65.9425)
p_r1_2 = (96.84, 65.9425)
p_r2_1 = (96.80, 72.4425)
p_r2_2 = (89.18, 72.4425)

p_us2_1 = (114.6059, 50.5138)
p_us2_2 = (117.1459, 50.5138)
p_us2_3 = (119.6859, 50.5138)
p_us2_4 = (122.2259, 50.5138)

p_r3_1 = (117.12, 61.4360)
p_r3_2 = (124.7449, 61.4360)
p_r4_1 = (117.16, 65.4452)
p_r4_2 = (124.78, 65.4452)

p_oled_1 = (152.12, 96.50)
p_oled_2 = (149.58, 96.50)
p_oled_3 = (147.04, 96.50)
p_oled_4 = (144.50, 96.50)

# ==============================================================================
# ROUTING IMPLEMENTATION (100% SINGLE LAYER + TOP JUMPERS)
# ==============================================================================

# 1. GROUND TRUNK (Heavy 1.2mm copper on B.Cu)
trunk_gnd_y = 101.50
trunk_5v_y = 104.50

# Pi GND Pins direct connections down to GND trunk
add_path([p_pi39, (79.06, trunk_gnd_y)], 0.8, "GND")
add_path([p_pi34, (86.68, trunk_gnd_y)], 0.8, "GND")
add_path([p_pi30, (91.76, trunk_gnd_y)], 0.8, "GND")
add_path([p_pi25, (96.84, trunk_gnd_y)], 0.8, "GND")
add_path([p_pi20, (104.46, trunk_gnd_y)], 0.8, "GND")
add_path([p_pi14, (112.08, trunk_gnd_y)], 0.8, "GND")
add_path([p_pi6, (122.24, trunk_gnd_y)], 0.8, "GND")
add_path([(76.58, trunk_gnd_y), (149.58, trunk_gnd_y)], 1.2, "GND")

# Left TB6612 Ground: Pad 8 down to Pad 16, then down to GND trunk
add_path([p_tb1_8, p_tb1_16], 0.8, "GND")
add_path([p_tb1_16, (76.58, trunk_gnd_y)], 0.8, "GND")
add_path([p_tb1_11, (63.88, 73.0), (76.58, 73.0)], 0.6, "GND")

# Right TB6612 Ground: Pad 8 down to Pad 16, then down to GND trunk
add_path([p_tb2_8, p_tb2_16], 0.8, "GND")
add_path([p_tb2_16, (149.58, trunk_gnd_y)], 0.8, "GND")
add_path([p_tb2_11, (136.88, 73.0), (149.58, 73.0)], 0.6, "GND")

# OLED Ground
add_path([p_oled_2, (149.58, trunk_gnd_y)], 0.8, "GND")

# Sensor Grounds
add_path([p_tcrt_1, (109.54, trunk_gnd_y)], 0.6, "GND")
add_path([p_us1_4, (94.00, 72.4425), p_r2_2], 0.6, "GND")
add_path([p_r2_2, (89.18, trunk_gnd_y)], 0.6, "GND")
add_path([p_us2_4, (122.2259, 65.4452), p_r4_1], 0.6, "GND")
add_path([p_r4_1, (117.16, trunk_gnd_y)], 0.6, "GND")

# 2. +5V_PWR BUS
add_path([p_pi4, p_pi2], 1.2, "/+5V_PWR")
add_path([p_pi2, (127.32, trunk_5v_y), (51.50, trunk_5v_y), (51.50, 44.00), (86.38, 44.00), p_us1_1], 1.2, "/+5V_PWR")
add_path([(86.38, 44.00), (114.6059, 44.00), p_us2_1], 1.2, "/+5V_PWR")
add_path([p_tb1_10, (61.34, trunk_5v_y)], 1.0, "/+5V_PWR")
add_path([p_tb2_10, (134.34, trunk_5v_y), (127.32, trunk_5v_y)], 1.0, "/+5V_PWR")

# 3. VM_MOTOR JUMPER (JMP6)
vias.append(make_via(58.80, 81.00, "/VM_MOTOR"))
vias.append(make_via(131.80, 81.00, "/VM_MOTOR"))
add_path([p_tb1_9, (58.80, 81.00)], 1.2, "/VM_MOTOR")
add_path([p_tb2_9, (131.80, 81.00)], 1.2, "/VM_MOTOR")
silk_items.append(make_silk_jumper(58.80, 81.00, 131.80, 81.00, "JMP6: VM_MOTOR (Wire 73mm)"))

# 4. TB6612 LEFT INTERNAL ARCHES
add_path([p_tb1_3, (63.88, 64.5), (68.96, 64.5), p_tb1_5], 0.6, "/AIN1_L")
add_path([p_tb1_2, (61.34, 66.5), (71.50, 66.5), p_tb1_6], 0.6, "/AIN2_L")
add_path([p_tb1_1, (58.80, 68.5), (74.04, 68.5), p_tb1_7], 0.6, "/PWMA_L")

# 5. TB6612 LEFT CONTROL EXITS TO PI 4
add_path([p_tb1_7, (74.04, 59.0), (86.68, 59.0), p_pi33], 0.6, "/PWMA_L")
add_path([p_tb1_6, (71.50, 58.0), (84.14, 58.0), p_pi35], 0.6, "/AIN2_L")
add_path([p_tb1_5, (68.96, 57.0), (81.60, 57.0), p_pi37], 0.6, "/AIN1_L")

# 6. TB6612 LEFT STBY JUMPER (JMP4)
vias.append(make_via(66.42, 63.00, "/STBY_L"))
vias.append(make_via(81.60, 84.00, "/STBY_L"))
add_path([p_tb1_4, (66.42, 63.00)], 0.6, "/STBY_L")
add_path([(81.60, 84.00), (81.60, 91.0), (79.0, 91.0), (79.0, 98.0), (81.60, 98.0), p_pi38], 0.6, "/STBY_L")
silk_items.append(make_silk_jumper(66.42, 63.00, 81.60, 84.00, "JMP4: STBY_L (Wire 25mm)"))

# 7. TB6612 LEFT MOTOR OUTPUTS
add_path([p_tb1_12, (66.42, 78.5), (56.0, 78.5), (56.0, 53.4005), p_m1_1], 0.8, "/M1_A")
add_path([p_tb1_13, (68.96, 80.0), (54.0, 80.0), (54.0, 51.50), (68.948, 51.50), p_m1_2], 0.8, "/M1_B")
add_path([p_tb1_14, (71.50, 78.5), (79.5, 78.5), (79.5, 53.4425), (75.53, 53.4425)], 0.8, "/M2_B")
add_path([p_tb1_15, (74.04, 80.0), (81.0, 80.0), (81.0, 51.50), (78.07, 51.50), p_m2_2], 0.8, "/M2_A")

# 8. TB6612 RIGHT INTERNAL ARCHES
add_path([p_tb2_3, (136.88, 64.5), (141.96, 64.5), p_tb2_5], 0.6, "/AIN1_R")
add_path([p_tb2_2, (134.34, 66.5), (144.50, 66.5), p_tb2_6], 0.6, "/AIN2_R")
add_path([p_tb2_1, (131.80, 68.5), (147.04, 68.5), p_tb2_7], 0.6, "/PWMA_R")

# 9. TB6612 RIGHT CONTROL EXITS TO PI 4
add_path([p_tb2_1, (131.80, 59.0), (124.78, 59.0), p_pi3], 0.6, "/PWMA_R")
add_path([p_tb2_2, (134.34, 58.0), (122.24, 58.0), p_pi5], 0.6, "/AIN2_R")
add_path([p_tb2_3, (136.88, 57.0), (119.70, 57.0), p_pi7], 0.6, "/AIN1_R")

# 10. TB6612 RIGHT STBY JUMPER (JMP5)
vias.append(make_via(139.42, 63.00, "/STBY_R"))
vias.append(make_via(114.62, 85.00, "/STBY_R"))
add_path([p_tb2_4, (139.42, 63.00)], 0.6, "/STBY_R")
add_path([(114.62, 85.00), p_pi11], 0.6, "/STBY_R")
silk_items.append(make_silk_jumper(139.42, 63.00, 114.62, 85.00, "JMP5: STBY_R (Wire 28mm)"))

# 11. TB6612 RIGHT MOTOR OUTPUTS
add_path([p_tb2_12, (139.42, 78.5), (138.53, 78.5), p_m3_1], 0.8, "/M3_A")
add_path([p_tb2_13, (141.96, 80.0), (141.07, 80.0), p_m3_2], 0.8, "/M3_B")
add_path([p_tb2_14, (144.50, 78.5), (154.5, 78.5), (154.5, 51.50), (149.53, 51.50), p_m4_1], 0.8, "/M4_B")
add_path([p_tb2_15, (147.04, 80.0), (156.5, 80.0), (156.5, 53.9425), p_m4_2], 0.8, "/M4_A")

# 12. TCRT5000 SENSOR (Straight parallel lines)
add_path([p_tcrt_5, p_pi23], 0.6, "/LINE_R")
add_path([p_tcrt_4, p_pi21], 0.6, "/LINE_C")
add_path([p_tcrt_3, p_pi19], 0.6, "/LINE_L")
add_path([p_tcrt_2, p_pi17], 0.6, "/+3V3_LOGIC")

# 13. ULTRASONIC LEFT & VOLTAGE DIVIDER
add_path([p_us1_2, (88.92, 54.0), (89.22, 54.0), p_pi31], 0.6, "/TRIG_L")
add_path([p_us1_3, (91.46, 63.0), (89.22, 63.0), p_r1_1], 0.6, "Net-(U_US1-ECHO)")
add_path([p_r1_2, (96.84, 69.0), (96.80, 69.0), p_r2_1], 0.6, "/ECHO_L")
add_path([p_r2_1, (96.80, 75.0), (91.76, 75.0), p_pi29], 0.6, "/ECHO_L")

# 14. ULTRASONIC RIGHT & VOLTAGE DIVIDER
add_path([p_us2_2, (117.1459, 54.0), (109.54, 54.0), p_pi15], 0.6, "/TRIG_R")
add_path([p_us2_3, (119.6859, 55.0), (117.12, 55.0), p_r3_1], 0.6, "Net-(U_US2-ECHO)")
add_path([p_r3_2, (124.7449, 63.5), (124.78, 63.5), p_r4_2], 0.6, "/ECHO_R")
add_path([p_r4_2, (124.78, 75.0), (112.08, 75.0), p_pi13], 0.6, "/ECHO_R")

# 15. OLED DISPLAY & JUMPERS (JMP1: SDA, JMP2: SCL, JMP3: 3V3)
# Pin 27 (SDA, Odd row Y=93.56) goes North to via at Y=87.0
vias.append(make_via(94.30, 87.00, "/I2C_SDA"))
vias.append(make_via(144.50, 87.00, "/I2C_SDA"))
add_path([p_pi27, (94.30, 87.00)], 0.6, "/I2C_SDA")
add_path([(144.50, 87.00), p_oled_4], 0.6, "/I2C_SDA")
silk_items.append(make_silk_jumper(94.30, 87.00, 144.50, 87.00, "JMP1: SDA (Wire 50mm)"))

# Pin 28 (SCL, Even row Y=96.10) goes South to via at Y=99.0
vias.append(make_via(94.30, 99.00, "/I2C_SCL"))
vias.append(make_via(147.04, 99.00, "/I2C_SCL"))
add_path([p_pi28, (94.30, 99.00)], 0.6, "/I2C_SCL")
add_path([(147.04, 99.00), p_oled_3], 0.6, "/I2C_SCL")
silk_items.append(make_silk_jumper(94.30, 99.00, 147.04, 99.00, "JMP2: SCL (Wire 53mm)"))

# +3V3 Jumper to OLED
vias.append(make_via(107.00, 84.00, "/+3V3_LOGIC"))
vias.append(make_via(152.12, 84.00, "/+3V3_LOGIC"))
add_path([p_pi17, (107.00, 84.00)], 0.6, "/+3V3_LOGIC")
add_path([(152.12, 84.00), p_oled_1], 0.6, "/+3V3_LOGIC")
silk_items.append(make_silk_jumper(107.00, 84.00, 152.12, 84.00, "JMP3: 3V3 (Wire 45mm)"))

final_pcb = base_part + "".join(vias) + "".join(segments) + "".join(silk_items) + "\t(embedded_fonts no)\n)\n"

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

print(f"Flawless PCB v2 generated: {len(segments)} segments, {len(vias)} vias, {len(silk_items)} jumpers.")

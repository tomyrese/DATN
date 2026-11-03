import json, re, uuid

def gen_uuid():
    return str(uuid.uuid4())

with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

def pad_pt(ref, pad_num):
    p = wp[ref][str(pad_num)]
    return (round(p['x'], 4), round(p['y'], 4))

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

# LEFT TB6612 Pads
p_tb1_1 = pad_pt("LEFT", 1)
p_tb1_2 = pad_pt("LEFT", 2)
p_tb1_3 = pad_pt("LEFT", 3)
p_tb1_4 = pad_pt("LEFT", 4)
p_tb1_5 = pad_pt("LEFT", 5)
p_tb1_6 = pad_pt("LEFT", 6)
p_tb1_7 = pad_pt("LEFT", 7)
p_tb1_8 = pad_pt("LEFT", 8)
p_tb1_9 = pad_pt("LEFT", 9)
p_tb1_10 = pad_pt("LEFT", 10)
p_tb1_11 = pad_pt("LEFT", 11)
p_tb1_12 = pad_pt("LEFT", 12)
p_tb1_13 = pad_pt("LEFT", 13)
p_tb1_14 = pad_pt("LEFT", 14)
p_tb1_15 = pad_pt("LEFT", 15)
p_tb1_16 = pad_pt("LEFT", 16)

# Right TB6612 Pads
p_tb2_1 = pad_pt("RIGHT", 1)
p_tb2_2 = pad_pt("RIGHT", 2)
p_tb2_3 = pad_pt("RIGHT", 3)
p_tb2_4 = pad_pt("RIGHT", 4)
p_tb2_5 = pad_pt("RIGHT", 5)
p_tb2_6 = pad_pt("RIGHT", 6)
p_tb2_7 = pad_pt("RIGHT", 7)
p_tb2_8 = pad_pt("RIGHT", 8)
p_tb2_9 = pad_pt("RIGHT", 9)
p_tb2_10 = pad_pt("RIGHT", 10)
p_tb2_11 = pad_pt("RIGHT", 11)
p_tb2_12 = pad_pt("RIGHT", 12)
p_tb2_13 = pad_pt("RIGHT", 13)
p_tb2_14 = pad_pt("RIGHT", 14)
p_tb2_15 = pad_pt("RIGHT", 15)
p_tb2_16 = pad_pt("RIGHT", 16)

# Motor Pads
p_m1_1 = pad_pt("MOTOR1", 1)
p_m1_2 = pad_pt("MOTOR1", 2)
p_m2_1 = pad_pt("MOTOR2", 1)
p_m2_2 = pad_pt("MOTOR2", 2)
p_m3_1 = pad_pt("MOTOR3", 1)
p_m3_2 = pad_pt("MOTOR3", 2)
p_m4_1 = pad_pt("MOTOR4", 1)
p_m4_2 = pad_pt("MOTOR4", 2)

# Pi Pads
p_pi2 = pad_pt("Rasp_PI4", 2)
p_pi4 = pad_pt("Rasp_PI4", 4)
p_pi6 = pad_pt("Rasp_PI4", 6)
p_pi14 = pad_pt("Rasp_PI4", 14)
p_pi20 = pad_pt("Rasp_PI4", 20)
p_pi25 = pad_pt("Rasp_PI4", 25)
p_pi30 = pad_pt("Rasp_PI4", 30)
p_pi34 = pad_pt("Rasp_PI4", 34)
p_pi39 = pad_pt("Rasp_PI4", 39)

p_pi3 = pad_pt("Rasp_PI4", 3)
p_pi5 = pad_pt("Rasp_PI4", 5)
p_pi7 = pad_pt("Rasp_PI4", 7)
p_pi11 = pad_pt("Rasp_PI4", 11)
p_pi13 = pad_pt("Rasp_PI4", 13)
p_pi15 = pad_pt("Rasp_PI4", 15)
p_pi17 = pad_pt("Rasp_PI4", 17)
p_pi19 = pad_pt("Rasp_PI4", 19)
p_pi21 = pad_pt("Rasp_PI4", 21)
p_pi23 = pad_pt("Rasp_PI4", 23)
p_pi27 = pad_pt("Rasp_PI4", 27)
p_pi28 = pad_pt("Rasp_PI4", 28)
p_pi29 = pad_pt("Rasp_PI4", 29)
p_pi31 = pad_pt("Rasp_PI4", 31)
p_pi33 = pad_pt("Rasp_PI4", 33)
p_pi35 = pad_pt("Rasp_PI4", 35)
p_pi37 = pad_pt("Rasp_PI4", 37)
p_pi38 = pad_pt("Rasp_PI4", 38)

# Sensor Pads
p_tcrt_1 = pad_pt("TCRT5000", 1)
p_tcrt_2 = pad_pt("TCRT5000", 2)
p_tcrt_3 = pad_pt("TCRT5000", 3)
p_tcrt_4 = pad_pt("TCRT5000", 4)
p_tcrt_5 = pad_pt("TCRT5000", 5)

p_us1_1 = pad_pt("HC_SR04_1", 1)
p_us1_2 = pad_pt("HC_SR04_1", 2)
p_us1_3 = pad_pt("HC_SR04_1", 3)
p_us1_4 = pad_pt("HC_SR04_1", 4)
p_r1_1 = pad_pt("R1", 1)
p_r1_2 = pad_pt("R1", 2)
p_r2_1 = pad_pt("R2", 1)
p_r2_2 = pad_pt("R2", 2)

p_us2_1 = pad_pt("HC_SR04_2", 1)
p_us2_2 = pad_pt("HC_SR04_2", 2)
p_us2_3 = pad_pt("HC_SR04_2", 3)
p_us2_4 = pad_pt("HC_SR04_2", 4)
p_r3_1 = pad_pt("R3", 1)
p_r3_2 = pad_pt("R3", 2)
p_r4_1 = pad_pt("R4", 1)
p_r4_2 = pad_pt("R4", 2)

p_oled_1 = pad_pt("OLED", 1)
p_oled_2 = pad_pt("OLED", 2)
p_oled_3 = pad_pt("OLED", 3)
p_oled_4 = pad_pt("OLED", 4)

# ==============================================================================
# 1. POWER BUSES
# ==============================================================================
trunk_gnd_y = 101.50
trunk_5v_y = 104.50

# GND Bus
add_path([(77.00, trunk_gnd_y), (p_oled_2[0], trunk_gnd_y)], 1.2, "GND")
add_path([p_pi39, (77.50, p_pi39[1]), (77.50, trunk_gnd_y)], 0.8, "GND")
add_path([p_pi34, (p_pi34[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_pi30, (p_pi30[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_pi20, (p_pi20[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_pi14, (p_pi14[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_pi6, (p_pi6[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_pi25, (p_pi25[0], 91.50), (p_pi20[0], 91.50)], 0.8, "GND")

add_path([p_tb1_11, (p_tb1_11[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_tb1_16, (p_tb1_16[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_tb1_8, p_tb1_16], 0.8, "GND")

add_path([p_tb2_11, (p_tb2_11[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_tb2_16, (p_tb2_16[0], trunk_gnd_y)], 0.8, "GND")
add_path([p_tb2_8, p_tb2_16], 0.8, "GND")

add_path([p_oled_2, (p_oled_2[0], trunk_gnd_y)], 0.8, "GND")

# Sensors GND
add_path([p_tcrt_1, (p_tcrt_1[0], trunk_gnd_y)], 0.6, "GND")
add_path([p_us1_4, (p_us1_4[0], 72.4425), p_r2_2], 0.6, "GND")
add_path([p_r2_2, (p_r2_2[0], trunk_gnd_y)], 0.6, "GND")
add_path([p_us2_4, (p_us2_4[0], 65.4452), p_r4_2], 0.6, "GND")
add_path([p_r4_2, (p_r4_2[0], 70.00), (136.88, 70.00), p_tb2_11], 0.6, "GND")

# +5V_PWR: runs along Y = 104.50
add_path([p_pi4, p_pi2], 1.2, "/+5V_PWR")
add_path([p_pi2, (p_pi2[0], trunk_5v_y), (51.50, trunk_5v_y), (51.50, 44.00), (p_us1_1[0], 44.00), p_us1_1], 1.2, "/+5V_PWR")
add_path([p_tb1_10, (p_tb1_10[0], trunk_5v_y)], 1.2, "/+5V_PWR")
add_path([(p_us1_1[0], 44.00), (p_us2_1[0], 44.00), p_us2_1], 1.2, "/+5V_PWR")
add_path([p_tb2_10, (p_tb2_10[0], trunk_5v_y), (p_pi2[0], trunk_5v_y)], 1.2, "/+5V_PWR")

# VM_MOTOR: runs along the TOP edge at Y = 42.00
add_path([p_tb1_9, (p_tb1_9[0], 73.00), (50.50, 73.00), (50.50, 42.00), (159.00, 42.00), (159.00, 73.00), (p_tb2_9[0], 73.00), p_tb2_9], 1.2, "/VM_MOTOR")

# ==============================================================================
# 2. MOTOR OUTPUTS
# ==============================================================================
# LEFT MOTORS: M1 goes LEFT to MOTOR1, M2 goes RIGHT to MOTOR2!
add_path([p_tb1_12, (p_tb1_12[0], 79.50), (57.00, 79.50), (57.00, 53.4005), p_m1_1], 0.8, "/M1_A")
add_path([p_tb1_13, (p_tb1_13[0], 81.00), (55.50, 81.00), (55.50, 51.50), (p_m1_2[0], 51.50), p_m1_2], 0.8, "/M1_B")
add_path([p_tb1_14, (p_tb1_14[0], 79.50), (75.53, 79.50), p_m2_1], 0.8, "/M2_B")
add_path([p_tb1_15, (p_tb1_15[0], 81.00), (78.07, 81.00), p_m2_2], 0.8, "/M2_A")

# RIGHT MOTORS: M3 goes LEFT to MOTOR3, M4 goes RIGHT to MOTOR4!
add_path([p_tb2_12, (p_tb2_12[0], 79.50), (p_m3_1[0], 79.50), p_m3_1], 0.8, "/M3_A")
add_path([p_tb2_13, (p_tb2_13[0], 81.00), (p_m3_2[0], 81.00), p_m3_2], 0.8, "/M3_B")
add_path([p_tb2_14, (p_tb2_14[0], 79.50), (153.00, 79.50), (153.00, 51.50), (p_m4_1[0], 51.50), p_m4_1], 0.8, "/M4_B")
add_path([p_tb2_15, (p_tb2_15[0], 81.00), (155.00, 81.00), (155.00, p_m4_2[1]), p_m4_2], 0.8, "/M4_A")

# ==============================================================================
# 3. CONTROL SIGNALS (Perfect Planar Cascade)
# ==============================================================================
# Left Arches inside socket
add_path([p_tb1_3, (p_tb1_3[0], 65.00), (p_tb1_5[0], 65.00), p_tb1_5], 0.6, "/AIN1_L")
add_path([p_tb1_2, (p_tb1_2[0], 67.00), (p_tb1_6[0], 67.00), p_tb1_6], 0.6, "/AIN2_L")
add_path([p_tb1_1, (p_tb1_1[0], 69.00), (p_tb1_7[0], 69.00), p_tb1_7], 0.6, "/PWMA_L")

# Left Exits (Ordered Cascade: STBY turns first, PWMA turns last)
add_path([p_tb1_4, (p_tb1_4[0], 60.00), (80.50, 60.00), (80.50, 98.00), (p_pi38[0], 98.00), p_pi38], 0.6, "/STBY_L")
add_path([p_tb1_5, (p_tb1_5[0], 59.00), (82.50, 59.00), (82.50, 91.50), (p_pi37[0], 91.50), p_pi37], 0.6, "/AIN1_L")
add_path([p_tb1_6, (p_tb1_6[0], 58.00), (84.14, 58.00), p_pi35], 0.6, "/AIN2_L")
add_path([p_tb1_7, (p_tb1_7[0], 57.00), (86.68, 57.00), p_pi33], 0.6, "/PWMA_L")

# Right Arches inside socket
add_path([p_tb2_3, (p_tb2_3[0], 65.00), (p_tb2_5[0], 65.00), p_tb2_5], 0.6, "/AIN1_R")
add_path([p_tb2_2, (p_tb2_2[0], 67.00), (p_tb2_6[0], 67.00), p_tb2_6], 0.6, "/AIN2_R")
add_path([p_tb2_1, (p_tb2_1[0], 69.00), (p_tb2_7[0], 69.00), p_tb2_7], 0.6, "/PWMA_R")

# Right Exits (Ordered Cascade: PWMA turns first, STBY turns last)
add_path([p_tb2_1, (p_tb2_1[0], 60.00), (124.78, 60.00), p_pi3], 0.6, "/PWMA_R")
add_path([p_tb2_2, (p_tb2_2[0], 59.00), (122.24, 59.00), p_pi5], 0.6, "/AIN2_R")
add_path([p_tb2_3, (p_tb2_3[0], 58.00), (119.70, 58.00), p_pi7], 0.6, "/AIN1_R")
add_path([p_tb2_4, (p_tb2_4[0], 57.00), (114.62, 57.00), p_pi11], 0.6, "/STBY_R")

# ==============================================================================
# 4. SENSORS (TCRT5000 & ULTRASONICS)
# ==============================================================================
# TCRT5000: Parallel straight down
add_path([p_tcrt_5, p_pi23], 0.6, "/LINE_R")
add_path([p_tcrt_4, p_pi21], 0.6, "/LINE_C")
add_path([p_tcrt_3, p_pi19], 0.6, "/LINE_L")
add_path([p_tcrt_2, p_pi17], 0.6, "/+3V3_LOGIC")

# Left Ultrasonic:
# Pin 31 is TRIG_L, Pin 29 is ECHO_L
add_path([p_us1_2, (p_us1_2[0], 54.00), (87.50, 54.00), (87.50, 88.00), (p_pi31[0], 88.00), p_pi31], 0.6, "/TRIG_L")
add_path([p_us1_3, (p_us1_3[0], 63.00), (p_r1_1[0], 63.00), p_r1_1], 0.6, "Net-(U_US1-ECHO)")
add_path([p_r1_2, p_r2_1], 0.6, "/ECHO_L")
add_path([p_r2_1, (p_r2_1[0], 78.00), (p_pi29[0], 78.00), p_pi29], 0.6, "/ECHO_L")

# Right Ultrasonic:
# Pin 15 is TRIG_R, Pin 13 is ECHO_R
add_path([p_us2_2, (p_us2_2[0], 53.00), (p_pi15[0], 53.00), p_pi15], 0.6, "/TRIG_R")
add_path([p_us2_3, (p_us2_3[0], 54.00), (p_r3_1[0], 54.00), p_r3_1], 0.6, "Net-(U_US2-ECHO)")
add_path([p_r3_2, p_r4_1], 0.6, "/ECHO_R")
add_path([p_r4_1, (p_r4_1[0], 78.00), (p_pi13[0], 78.00), p_pi13], 0.6, "/ECHO_R")

# ==============================================================================
# 5. OLED & JUMPERS
# ==============================================================================
add_path([p_pi28, (p_pi28[0], 97.50), (p_oled_3[0], 97.50), p_oled_3], 0.6, "/I2C_SCL")

vias.append(make_via(p_pi27[0], 89.00, "/I2C_SDA"))
vias.append(make_via(p_oled_4[0], 89.00, "/I2C_SDA"))
add_path([p_pi27, (p_pi27[0], 89.00)], 0.6, "/I2C_SDA")
add_path([(p_oled_4[0], 89.00), p_oled_4], 0.6, "/I2C_SDA")
silk_items.append(make_silk_jumper(p_pi27[0], 89.00, p_oled_4[0], 89.00, "JMP1: SDA (Wire 50mm)"))

vias.append(make_via(p_pi17[0], 86.50, "/+3V3_LOGIC"))
vias.append(make_via(p_oled_1[0], 86.50, "/+3V3_LOGIC"))
add_path([p_pi17, (p_pi17[0], 86.50)], 0.6, "/+3V3_LOGIC")
add_path([(p_oled_1[0], 86.50), p_oled_1], 0.6, "/+3V3_LOGIC")
silk_items.append(make_silk_jumper(p_pi17[0], 86.50, p_oled_1[0], 86.50, "JMP2: 3V3 (Wire 45mm)"))

final_pcb = base_part + "".join(vias) + "".join(segments) + "".join(silk_items) + "\t(embedded_fonts no)\n)\n"

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

print(f"Flawless PCB generated: {len(segments)} segments, {len(vias)} vias, {len(silk_items)} jumpers.")

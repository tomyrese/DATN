import json, re, uuid

def gen_uuid():
    return str(uuid.uuid4())

# Load world pads
with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

def pad_pt(ref, pad_num):
    p = wp[ref][str(pad_num)]
    return (p['x'], p['y'])

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
        "29": "/TRIG_L",
        "31": "/ECHO_L",
        "3": "/PWMA_R",
        "5": "/AIN2_R",
        "7": "/AIN1_R",
        "11": "/STBY_R",
        "13": "/TRIG_R",
        "15": "/ECHO_R",
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

# ==============================================================================
# 1. TB6612 LEFT MOTOR OUTPUTS (Via Left Outer Channel)
# ==============================================================================
p_tb1_12 = pad_pt("LEFT", 12)
p_tb1_13 = pad_pt("LEFT", 13)
p_tb1_14 = pad_pt("LEFT", 14)
p_tb1_15 = pad_pt("LEFT", 15)

p_m1_1 = pad_pt("MOTOR1", 1)
p_m1_2 = pad_pt("MOTOR1", 2)
p_m2_1 = pad_pt("MOTOR2", 1)
p_m2_2 = pad_pt("MOTOR2", 2)

# M1_A (Pad 12 -> MOTOR1-1)
add_path([p_tb1_12, (p_tb1_12[0], 79.50), (55.50, 79.50), (55.50, p_m1_1[1]), p_m1_1], 0.8, "/M1_A")
# M1_B (Pad 13 -> MOTOR1-2)
add_path([p_tb1_13, (p_tb1_13[0], 81.00), (54.00, 81.00), (54.00, 51.50), (p_m1_2[0], 51.50), p_m1_2], 0.8, "/M1_B")
# M2_B (Pad 14 -> MOTOR2-1)
add_path([p_tb1_14, (p_tb1_14[0], 82.50), (52.50, 82.50), (52.50, 49.50), (p_m2_1[0], 49.50), p_m2_1], 0.8, "/M2_B")
# M2_A (Pad 15 -> MOTOR2-2)
add_path([p_tb1_15, (p_tb1_15[0], 84.00), (51.00, 84.00), (51.00, 47.50), (p_m2_2[0], 47.50), p_m2_2], 0.8, "/M2_A")

# ==============================================================================
# 2. TB6612 LEFT CONTROL INPUTS (Exits Up & Right to Mirrored Pi)
# ==============================================================================
p_tb1_1 = pad_pt("LEFT", 1)
p_tb1_2 = pad_pt("LEFT", 2)
p_tb1_3 = pad_pt("LEFT", 3)
p_tb1_4 = pad_pt("LEFT", 4)
p_tb1_5 = pad_pt("LEFT", 5)
p_tb1_6 = pad_pt("LEFT", 6)
p_tb1_7 = pad_pt("LEFT", 7)

p_pi38 = pad_pt("Rasp_PI4", 38)
p_pi37 = pad_pt("Rasp_PI4", 37)
p_pi35 = pad_pt("Rasp_PI4", 35)
p_pi33 = pad_pt("Rasp_PI4", 33)

# Internal Arches inside socket cavity (Pads 1-7, 2-6, 3-5)
add_path([p_tb1_3, (p_tb1_3[0], 65.00), (p_tb1_5[0], 65.00), p_tb1_5], 0.6, "/AIN1_L")
add_path([p_tb1_2, (p_tb1_2[0], 67.00), (p_tb1_6[0], 67.00), p_tb1_6], 0.6, "/AIN2_L")
add_path([p_tb1_1, (p_tb1_1[0], 69.00), (p_tb1_7[0], 69.00), p_tb1_7], 0.6, "/PWMA_L")

# Exits to Pi via corridor between TB6612 and HC_SR04_1
# STBY_L: Pad 4 up to 58.00, right to 79.50, down past Pi to 98.00, into Pin 38 from below
add_path([p_tb1_4, (p_tb1_4[0], 58.00), (79.50, 58.00), (79.50, 98.00), (p_pi38[0], 98.00), p_pi38], 0.6, "/STBY_L")
# AIN1_L: Pad 5 up to 59.20, right to 81.60, down to Pi Pin 37
add_path([p_tb1_5, (p_tb1_5[0], 59.20), (p_pi37[0], 59.20), p_pi37], 0.6, "/AIN1_L")
# AIN2_L: Pad 6 up to 60.40, right to 84.14, down to Pi Pin 35
add_path([p_tb1_6, (p_tb1_6[0], 60.40), (p_pi35[0], 60.40), p_pi35], 0.6, "/AIN2_L")
# PWMA_L: Pad 7 right to 86.68, down to Pi Pin 33
add_path([p_tb1_7, (p_pi33[0], p_tb1_7[1]), p_pi33], 0.6, "/PWMA_L")

# ==============================================================================
# 3. TB6612 RIGHT MOTOR OUTPUTS (Via Right Outer Channel)
# ==============================================================================
p_tb2_12 = pad_pt("RIGHT", 12)
p_tb2_13 = pad_pt("RIGHT", 13)
p_tb2_14 = pad_pt("RIGHT", 14)
p_tb2_15 = pad_pt("RIGHT", 15)

p_m3_1 = pad_pt("MOTOR3", 1)
p_m3_2 = pad_pt("MOTOR3", 2)
p_m4_1 = pad_pt("MOTOR4", 1)
p_m4_2 = pad_pt("MOTOR4", 2)

# M4_A (Pad 15 -> MOTOR4-2)
add_path([p_tb2_15, (p_tb2_15[0], 79.50), (154.00, 79.50), (154.00, p_m4_2[1]), p_m4_2], 0.8, "/M4_A")
# M4_B (Pad 14 -> MOTOR4-1)
add_path([p_tb2_14, (p_tb2_14[0], 81.00), (155.50, 81.00), (155.50, 51.50), (p_m4_1[0], 51.50), p_m4_1], 0.8, "/M4_B")
# M3_B (Pad 13 -> MOTOR3-2)
add_path([p_tb2_13, (p_tb2_13[0], 82.50), (157.00, 82.50), (157.00, 49.50), (p_m3_2[0], 49.50), p_m3_2], 0.8, "/M3_B")
# M3_A (Pad 12 -> MOTOR3-1)
add_path([p_tb2_12, (p_tb2_12[0], 84.00), (158.50, 84.00), (158.50, 47.50), (p_m3_1[0], 47.50), p_m3_1], 0.8, "/M3_A")

# ==============================================================================
# 4. TB6612 RIGHT CONTROL INPUTS (Exits Up & Left to Mirrored Pi)
# ==============================================================================
p_tb2_1 = pad_pt("RIGHT", 1)
p_tb2_2 = pad_pt("RIGHT", 2)
p_tb2_3 = pad_pt("RIGHT", 3)
p_tb2_4 = pad_pt("RIGHT", 4)
p_tb2_5 = pad_pt("RIGHT", 5)
p_tb2_6 = pad_pt("RIGHT", 6)
p_tb2_7 = pad_pt("RIGHT", 7)

p_pi3 = pad_pt("Rasp_PI4", 3)
p_pi5 = pad_pt("Rasp_PI4", 5)
p_pi7 = pad_pt("Rasp_PI4", 7)
p_pi11 = pad_pt("Rasp_PI4", 11)

# Internal Arches inside socket cavity (Pads 1-7, 2-6, 3-5)
add_path([p_tb2_3, (p_tb2_3[0], 65.00), (p_tb2_5[0], 65.00), p_tb2_5], 0.6, "/AIN1_R")
add_path([p_tb2_2, (p_tb2_2[0], 67.00), (p_tb2_6[0], 67.00), p_tb2_6], 0.6, "/AIN2_R")
add_path([p_tb2_1, (p_tb2_1[0], 69.00), (p_tb2_7[0], 69.00), p_tb2_7], 0.6, "/PWMA_R")

# Exits to Pi via corridor between TB6612 and HC_SR04_2
# PWMA_R: Pad 1 left to 124.78, down to Pi Pin 3
add_path([p_tb2_1, (p_pi3[0], p_tb2_1[1]), p_pi3], 0.6, "/PWMA_R")
# AIN2_R: Pad 2 up to 60.40, left to 122.24, down to Pi Pin 5
add_path([p_tb2_2, (p_tb2_2[0], 60.40), (p_pi5[0], 60.40), p_pi5], 0.6, "/AIN2_R")
# AIN1_R: Pad 3 up to 59.20, left to 119.70, down to Pi Pin 7
add_path([p_tb2_3, (p_tb2_3[0], 59.20), (p_pi7[0], 59.20), p_pi7], 0.6, "/AIN1_R")
# STBY_R: Pad 4 up to 58.00, left to 114.62, down to Pi Pin 11
add_path([p_tb2_4, (p_tb2_4[0], 58.00), (p_pi11[0], 58.00), p_pi11], 0.6, "/STBY_R")

# ==============================================================================
# 5. TCRT5000 LINE SENSORS (Straight down to Pi)
# ==============================================================================
p_tcrt_5 = pad_pt("TCRT5000", 5)
p_tcrt_4 = pad_pt("TCRT5000", 4)
p_tcrt_3 = pad_pt("TCRT5000", 3)
p_tcrt_2 = pad_pt("TCRT5000", 2)
p_tcrt_1 = pad_pt("TCRT5000", 1)

p_pi23 = pad_pt("Rasp_PI4", 23)
p_pi21 = pad_pt("Rasp_PI4", 21)
p_pi19 = pad_pt("Rasp_PI4", 19)
p_pi17 = pad_pt("Rasp_PI4", 17)
p_pi14 = pad_pt("Rasp_PI4", 14)

add_path([p_tcrt_5, p_pi23], 0.6, "/LINE_R")
add_path([p_tcrt_4, p_pi21], 0.6, "/LINE_C")
add_path([p_tcrt_3, p_pi19], 0.6, "/LINE_L")
add_path([p_tcrt_2, p_pi17], 0.6, "/+3V3_LOGIC")
add_path([p_tcrt_1, (p_tcrt_1[0], 75.00), (p_pi14[0], 75.00), p_pi14], 0.6, "GND")

# ==============================================================================
# 6. ULTRASONIC SENSORS
# ==============================================================================
p_us1_1 = pad_pt("HC_SR04_1", 1)
p_us1_2 = pad_pt("HC_SR04_1", 2)
p_us1_3 = pad_pt("HC_SR04_1", 3)
p_us1_4 = pad_pt("HC_SR04_1", 4)
p_r1_1 = pad_pt("R1", 1)
p_r1_2 = pad_pt("R1", 2)
p_r2_1 = pad_pt("R2", 1)
p_r2_2 = pad_pt("R2", 2)
p_pi29 = pad_pt("Rasp_PI4", 29)
p_pi31 = pad_pt("Rasp_PI4", 31)

# TRIG_L
add_path([p_us1_2, (p_us1_2[0], 55.00), (p_pi29[0], 55.00), p_pi29], 0.6, "/TRIG_L")
# ECHO_L to R1
add_path([p_us1_3, (p_us1_3[0], 63.00), (p_r1_1[0], 63.00), p_r1_1], 0.6, "Net-(U_US1-ECHO)")
# R1 to R2 and to Pi Pin 31
add_path([p_r1_2, p_r2_1], 0.6, "/ECHO_L")
add_path([p_r2_1, (p_r2_1[0], 78.00), (p_pi31[0], 78.00), p_pi31], 0.6, "/ECHO_L")
# HC_SR04_1 GND and R2 GND
add_path([p_us1_4, (p_us1_4[0], 72.4425), p_r2_2], 0.6, "GND")

# HC_SR04_2 (Right US)
p_us2_1 = pad_pt("HC_SR04_2", 1)
p_us2_2 = pad_pt("HC_SR04_2", 2)
p_us2_3 = pad_pt("HC_SR04_2", 3)
p_us2_4 = pad_pt("HC_SR04_2", 4)
p_r3_1 = pad_pt("R3", 1)
p_r3_2 = pad_pt("R3", 2)
p_r4_1 = pad_pt("R4", 1)
p_r4_2 = pad_pt("R4", 2)
p_pi13 = pad_pt("Rasp_PI4", 13)
p_pi15 = pad_pt("Rasp_PI4", 15)

# TRIG_R
add_path([p_us2_2, (p_us2_2[0], 55.00), (p_pi13[0], 55.00), p_pi13], 0.6, "/TRIG_R")
# ECHO_R to R3
add_path([p_us2_3, (p_us2_3[0], 58.00), (p_r3_1[0], 58.00), p_r3_1], 0.6, "Net-(U_US2-ECHO)")
# R3 to R4 and to Pi Pin 15
add_path([p_r3_2, p_r4_1], 0.6, "/ECHO_R")
add_path([p_r4_1, (p_r4_1[0], 78.00), (p_pi15[0], 78.00), p_pi15], 0.6, "/ECHO_R")
# HC_SR04_2 GND and R4 GND
add_path([p_us2_4, (p_r4_2[0], p_us2_4[1]), p_r4_2], 0.6, "GND")

# ==============================================================================
# 7. OLED DISPLAY & JUMPERS
# ==============================================================================
p_oled_1 = pad_pt("OLED", 1)
p_oled_2 = pad_pt("OLED", 2)
p_oled_3 = pad_pt("OLED", 3)
p_oled_4 = pad_pt("OLED", 4)

p_pi28 = pad_pt("Rasp_PI4", 28)
p_pi27 = pad_pt("Rasp_PI4", 27)

# I2C_SCL (Pad 3 -> Pi Pin 28)
add_path([p_pi28, (p_pi28[0], 97.50), (p_oled_3[0], 97.50), p_oled_3], 0.6, "/I2C_SCL")

# I2C_SDA via JMP1
vias.append(make_via(p_pi27[0], 89.00, "/I2C_SDA"))
vias.append(make_via(p_oled_4[0], 89.00, "/I2C_SDA"))
add_path([p_pi27, (p_pi27[0], 89.00)], 0.6, "/I2C_SDA")
add_path([(p_oled_4[0], 89.00), p_oled_4], 0.6, "/I2C_SDA")
silk_items.append(make_silk_jumper(p_pi27[0], 89.00, p_oled_4[0], 89.00, "JMP1: SDA (Wire 50mm)"))

# +3V3_LOGIC to OLED via JMP2
vias.append(make_via(p_pi17[0], 86.50, "/+3V3_LOGIC"))
vias.append(make_via(p_oled_1[0], 86.50, "/+3V3_LOGIC"))
add_path([p_pi17, (p_pi17[0], 86.50)], 0.6, "/+3V3_LOGIC")
add_path([(p_oled_1[0], 86.50), p_oled_1], 0.6, "/+3V3_LOGIC")
silk_items.append(make_silk_jumper(p_pi17[0], 86.50, p_oled_1[0], 86.50, "JMP2: 3V3 (Wire 45mm)"))

# ==============================================================================
# 8. POWER RAILS (+5V_PWR, VM_MOTOR, GND)
# ==============================================================================
p_pi2 = pad_pt("Rasp_PI4", 2)
p_pi4 = pad_pt("Rasp_PI4", 4)
p_tb1_10 = pad_pt("LEFT", 10)
p_tb2_10 = pad_pt("RIGHT", 10)

# +5V_PWR:
# Pi Pin 2 & 4 bridged
add_path([p_pi4, p_pi2], 1.2, "/+5V_PWR")
# Bottom rail at Y = 104.50
add_path([p_pi2, (p_pi2[0], 104.50), (49.50, 104.50), (49.50, 44.00), (p_us1_1[0], 44.00), p_us1_1], 1.2, "/+5V_PWR")
add_path([(49.50, 76.4475), p_tb1_10], 1.2, "/+5V_PWR")
add_path([(p_us1_1[0], 44.00), (p_us2_1[0], 44.00), p_us2_1], 1.2, "/+5V_PWR")
add_path([(p_us2_1[0], 44.00), (134.34, 44.00), (134.34, 55.00)], 1.2, "/+5V_PWR")
# To connect to RIGHT TB6612 Pad 10 cleanly without crossing:
# Pad 10 of RIGHT is at (134.34, 76.45). It faces downwards to Y = 86.00
add_path([p_tb2_10, (p_tb2_10[0], 86.00), (131.00, 86.00), (131.00, 104.50), (p_pi2[0], 104.50)], 1.2, "/+5V_PWR")

# VM_MOTOR:
p_tb1_9 = pad_pt("LEFT", 9)
p_tb2_9 = pad_pt("RIGHT", 9)
add_path([p_tb1_9, (p_tb1_9[0], 86.00), (50.00, 86.00), (50.00, 106.00), (130.00, 106.00), (130.00, 88.00), (p_tb2_9[0], 88.00), p_tb2_9], 1.2, "/VM_MOTOR")

# GND BUS:
trunk_y = 101.50
gnd_pi_pins = [pad_pt("Rasp_PI4", p) for p in [39, 34, 30, 25, 20, 14, 6]]
p39, p34, p30, p25, p20, p14, p6 = gnd_pi_pins

# Bottom GND trunk
add_path([(p39[0], trunk_y), (p_oled_2[0], trunk_y)], 1.2, "GND")
for p in gnd_pi_pins:
    add_path([p, (p[0], trunk_y)], 0.8, "GND")
add_path([p_oled_2, (p_oled_2[0], trunk_y)], 0.8, "GND")

# Left TB6612 GND (Pads 8, 11, 16)
p_tb1_8 = pad_pt("LEFT", 8)
p_tb1_11 = pad_pt("LEFT", 11)
p_tb1_16 = pad_pt("LEFT", 16)
add_path([p_tb1_8, (p_tb1_8[0], 56.50), (p_tb1_16[0], 56.50), p_tb1_16], 0.8, "GND")
add_path([p_tb1_16, (p_tb1_16[0], trunk_y)], 0.8, "GND")
add_path([p_tb1_11, (p_tb1_11[0], 88.00), (p_tb1_16[0], 88.00)], 0.8, "GND")

# Right TB6612 GND (Pads 8, 11, 16)
p_tb2_8 = pad_pt("RIGHT", 8)
p_tb2_11 = pad_pt("RIGHT", 11)
p_tb2_16 = pad_pt("RIGHT", 16)
add_path([p_tb2_8, (p_tb2_8[0], 56.50), (p_tb2_16[0], 56.50), p_tb2_16], 0.8, "GND")
add_path([p_tb2_16, (p_tb2_16[0], trunk_y)], 0.8, "GND")
add_path([p_tb2_11, (p_tb2_11[0], 88.00), (p_tb2_16[0], 88.00)], 0.8, "GND")

# Connect R2 GND and R4 GND to GND bus
add_path([p_r2_2, (p_r2_2[0], trunk_y)], 0.8, "GND")
add_path([p_r4_2, (p_r4_2[0], trunk_y)], 0.8, "GND")

# Assemble final PCB
final_pcb = base_part + "".join(vias) + "".join(segments) + "".join(silk_items) + "\t(embedded_fonts no)\n)\n"

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

print(f"Generated PCB: {len(segments)} segments, {len(vias)} vias, {len(silk_items)} jumpers.")


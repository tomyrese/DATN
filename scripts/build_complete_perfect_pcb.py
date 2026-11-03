import re
import uuid
import subprocess

def gen_uuid():
    return str(uuid.uuid4())

# Load clean PCB template
with open('Pi4_Robot_Carrier_1Layer_clean.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update TB6612 footprints: swap row 1 and row 2
from test_fp_swap import swap_tb6612_rows, mirror_pi4_header

def update_tb_footprint(fp_text, is_left=True):
    fp_text = swap_tb6612_rows(fp_text)
    # Update net names
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
    # TCRT5000:
    # Pad 1 (109.54): GND
    # Pad 2 (107.00): /+3V3_LOGIC
    # Pad 3 (104.46): /LINE_L
    # Pad 4 (101.92): /LINE_C
    # Pad 5 (99.38): /LINE_R
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

text = re.sub(r'\(footprint\s+"[^"]+"[\s\S]*?\n\t\)', fp_repl, text)

# Helper functions for tracks, vias, jumpers
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
# 1. POWER RAILS (+5V_PWR, VM_MOTOR, GND)
# ==============================================================================
# +5V_PWR:
# Bridge Pi Pin 2 (127.32, 96.10) and Pin 4 (124.78, 96.10)
add_path([(124.78, 96.10), (127.32, 96.10)], 2.0, "/+5V_PWR")
# Down to bottom rail at Y = 104.00
add_path([(124.78, 96.10), (124.78, 104.00), (53.50, 104.00), (53.50, 76.45), (61.34, 76.45)], 1.4, "/+5V_PWR") # To LEFT TB6612 Pad 10
add_path([(53.50, 76.45), (53.50, 44.00), (86.38, 44.00), (86.38, 50.44)], 1.4, "/+5V_PWR") # To HC-SR04_1 Pad 1
add_path([(86.38, 44.00), (114.61, 44.00), (114.61, 50.51)], 1.4, "/+5V_PWR") # To HC-SR04_2 Pad 1
add_path([(114.61, 44.00), (134.34, 44.00), (134.34, 76.45)], 1.4, "/+5V_PWR") # To RIGHT TB6612 Pad 10

# VM_MOTOR:
# Connect Pad 9 of LEFT (58.80, 76.45) and Pad 9 of RIGHT (131.80, 76.45)
add_path([(58.80, 76.45), (58.80, 78.00), (51.00, 78.00), (51.00, 46.50), (131.80, 46.50), (131.80, 76.45)], 1.4, "/VM_MOTOR")

# GND BUS:
# Even GND pins on Pi header connected via bottom trunk at Y = 100.50
add_path([(86.68, 96.10), (86.68, 100.50), (122.24, 100.50), (122.24, 96.10)], 1.4, "GND")
add_path([(91.76, 96.10), (91.76, 100.50)], 1.4, "GND")
add_path([(104.46, 96.10), (104.46, 100.50)], 1.4, "GND")
add_path([(112.08, 96.10), (112.08, 100.50)], 1.4, "GND")
add_path([(79.06, 93.56), (79.06, 100.50), (86.68, 100.50)], 1.4, "GND") # Pin 39 GND

# Connect to TB6612 LEFT GND:
# Pad 11 (63.88, 76.45), Pad 16 (76.58, 76.45), Pad 8 (76.58, 61.21)
add_path([(76.58, 61.21), (76.58, 76.45)], 1.4, "GND")
add_path([(76.58, 76.45), (76.58, 83.00), (63.88, 83.00), (63.88, 76.45)], 1.4, "GND")
add_path([(76.58, 83.00), (76.58, 100.50)], 1.4, "GND")

# Connect to TB6612 RIGHT GND:
# Pad 11 (136.88, 76.45), Pad 16 (149.58, 76.45), Pad 8 (149.58, 61.21)
add_path([(149.58, 61.21), (149.58, 76.45)], 1.4, "GND")
add_path([(149.58, 76.45), (149.58, 83.00), (136.88, 83.00), (136.88, 76.45)], 1.4, "GND")
add_path([(136.88, 83.00), (136.88, 100.50)], 1.4, "GND")

# Connect Sensors to GND:
# TCRT5000 Pad 1 (109.54, 50.44), HC-SR04_1 Pad 4 (94.00, 50.44), R2 Pad 2 (89.18, 72.44)
add_path([(94.00, 50.44), (94.00, 68.00), (89.18, 68.00), (89.18, 72.44)], 1.0, "GND")
add_path([(89.18, 72.44), (89.18, 75.00), (84.00, 75.00), (84.00, 100.50)], 1.0, "GND")

add_path([(109.54, 50.44), (109.54, 62.00), (109.54, 75.00), (104.46, 75.00), (104.46, 96.10)], 1.0, "GND")

# HC-SR04_2 Pad 4 (122.23, 50.51), R4 Pad 2 (124.78, 65.45)
add_path([(122.23, 50.51), (124.78, 50.51), (124.78, 65.45)], 1.0, "GND")
add_path([(124.78, 65.45), (124.78, 75.00), (117.16, 75.00), (117.16, 93.56)], 1.0, "GND")

# OLED Pad 2 (149.58, 96.50) GND:
add_path([(149.58, 96.50), (149.58, 100.50), (136.88, 100.50)], 1.0, "GND")

# ==============================================================================
# 2. TB6612 LEFT MOTOR OUTPUTS (B.Cu 1.4mm)
# ==============================================================================
# Pad 12 (AO1, 66.42, 76.45) -> MOTOR1 Pad 1 (66.41, 53.40)
add_path([(66.42, 76.45), (66.42, 79.00), (52.20, 79.00), (52.20, 53.40), (66.41, 53.40)], 1.4, "/M1_A")

# Pad 13 (AO2, 68.96, 76.45) -> MOTOR1 Pad 2 (68.95, 53.40)
add_path([(68.96, 76.45), (68.96, 81.00), (50.50, 81.00), (50.50, 51.50), (68.95, 51.50), (68.95, 53.40)], 1.4, "/M1_B")

# Pad 14 (BO2, 71.50, 76.45) -> MOTOR2 Pad 1 (75.53, 53.44)
add_path([(71.50, 76.45), (71.50, 79.00), (79.00, 79.00), (79.00, 51.50), (75.53, 51.50), (75.53, 53.44)], 1.4, "/M2_B")

# Pad 15 (BO1, 74.04, 76.45) -> MOTOR2 Pad 2 (78.07, 53.44)
add_path([(74.04, 76.45), (74.04, 81.00), (81.00, 81.00), (81.00, 53.44), (78.07, 53.44)], 1.4, "/M2_A")

# ==============================================================================
# 3. TB6612 RIGHT MOTOR OUTPUTS (B.Cu 1.4mm)
# ==============================================================================
# Pad 12 (AO1, 139.42, 76.45) -> MOTOR3 Pad 1 (138.53, 53.94)
add_path([(139.42, 76.45), (139.42, 79.00), (127.50, 79.00), (127.50, 53.94), (138.53, 53.94)], 1.4, "/M3_A")

# Pad 13 (AO2, 141.96, 76.45) -> MOTOR3 Pad 2 (141.07, 53.94)
add_path([(141.96, 76.45), (141.96, 81.00), (126.00, 81.00), (126.00, 51.50), (141.07, 51.50), (141.07, 53.94)], 1.4, "/M3_B")

# Pad 14 (BO2, 144.50, 76.45) -> MOTOR4 Pad 1 (149.53, 53.94)
add_path([(144.50, 76.45), (144.50, 79.00), (155.00, 79.00), (155.00, 51.50), (149.53, 51.50), (149.53, 53.94)], 1.4, "/M4_B")

# Pad 15 (BO1, 147.04, 76.45) -> MOTOR4 Pad 2 (152.07, 53.94)
add_path([(147.04, 76.45), (147.04, 81.00), (157.00, 81.00), (157.00, 53.94), (152.07, 53.94)], 1.4, "/M4_A")

# ==============================================================================
# 4. TB6612 LEFT CONTROL INPUTS (Concentric Nested Arches)
# ==============================================================================
# Pad 4 (STBY_L, 66.42, 61.21) -> Pi Pin 38 (81.60, 96.10)
add_path([(66.42, 61.21), (66.42, 92.50), (81.60, 92.50), (81.60, 96.10)], 1.0, "/STBY_L")

# Pad 3 (63.88, 61.21) & Pad 5 (68.96, 61.21) -> Pi Pin 37 (81.60, 93.56)
add_path([(63.88, 61.21), (63.88, 66.00), (68.96, 66.00), (68.96, 61.21)], 1.0, "/AIN1_L")
add_path([(68.96, 66.00), (68.96, 88.00), (81.60, 88.00), (81.60, 93.56)], 1.0, "/AIN1_L")

# Pad 2 (61.34, 61.21) & Pad 6 (71.50, 61.21) -> Pi Pin 35 (84.14, 93.56)
add_path([(61.34, 61.21), (61.34, 68.50), (71.50, 68.50), (71.50, 61.21)], 1.0, "/AIN2_L")
add_path([(71.50, 68.50), (71.50, 86.00), (84.14, 86.00), (84.14, 93.56)], 1.0, "/AIN2_L")

# Pad 1 (58.80, 61.21) & Pad 7 (74.04, 61.21) -> Pi Pin 33 (86.68, 93.56)
add_path([(58.80, 61.21), (58.80, 71.00), (74.04, 71.00), (74.04, 61.21)], 1.0, "/PWMA_L")
add_path([(74.04, 71.00), (74.04, 84.00), (86.68, 84.00), (86.68, 93.56)], 1.0, "/PWMA_L")

# ==============================================================================
# 5. TB6612 RIGHT CONTROL INPUTS (Concentric Nested Arches)
# ==============================================================================
# Pad 4 (STBY_R, 139.42, 61.21) -> Pi Pin 11 (114.62, 93.56)
add_path([(139.42, 61.21), (139.42, 92.50), (114.62, 92.50), (114.62, 93.56)], 1.0, "/STBY_R")

# Pad 3 (136.88, 61.21) & Pad 5 (141.96, 61.21) -> Pi Pin 7 (119.70, 93.56)
add_path([(136.88, 61.21), (136.88, 66.00), (141.96, 66.00), (141.96, 61.21)], 1.0, "/AIN1_R")
add_path([(136.88, 66.00), (136.88, 88.00), (119.70, 88.00), (119.70, 93.56)], 1.0, "/AIN1_R")

# Pad 2 (134.34, 61.21) & Pad 6 (144.50, 61.21) -> Pi Pin 5 (122.24, 93.56)
add_path([(134.34, 61.21), (134.34, 68.50), (144.50, 68.50), (144.50, 61.21)], 1.0, "/AIN2_R")
add_path([(134.34, 68.50), (134.34, 86.00), (122.24, 86.00), (122.24, 93.56)], 1.0, "/AIN2_R")

# Pad 1 (131.80, 61.21) & Pad 7 (147.04, 61.21) -> Pi Pin 3 (124.78, 93.56)
add_path([(131.80, 61.21), (131.80, 71.00), (147.04, 71.00), (147.04, 61.21)], 1.0, "/PWMA_R")
add_path([(131.80, 71.00), (131.80, 84.00), (124.78, 84.00), (124.78, 93.56)], 1.0, "/PWMA_R")

# ==============================================================================
# 6. ULTRASONIC SENSORS
# ==============================================================================
# HC-SR04_1 (Left):
# Pad 2 (TRIG_L, 88.92, 50.44) -> Pi Pin 29 (91.76, 93.56)
add_path([(88.92, 50.44), (88.92, 60.00), (91.76, 60.00), (91.76, 93.56)], 1.0, "/TRIG_L")

# Pad 3 (Net-U_US1-ECHO, 91.46, 50.44) -> R1 Pad 1 (89.22, 65.94)
add_path([(91.46, 50.44), (91.46, 62.00), (89.22, 62.00), (89.22, 65.94)], 1.0, "Net-(U_US1-ECHO)")

# R1 Pad 2 (96.84, 65.94) -> R2 Pad 1 (96.80, 72.44) -> Pi Pin 31 (89.22, 93.56)
add_path([(96.84, 65.94), (96.80, 72.44)], 1.0, "/ECHO_L")
add_path([(96.80, 72.44), (96.80, 80.00), (89.22, 80.00), (89.22, 93.56)], 1.0, "/ECHO_L")

# HC-SR04_2 (Right):
# Pad 2 (TRIG_R, 117.15, 50.51) -> Pi Pin 13 (112.08, 93.56)
add_path([(117.15, 50.51), (117.15, 58.00), (112.08, 58.00), (112.08, 93.56)], 1.0, "/TRIG_R")

# Pad 3 (Net-U_US2-ECHO, 119.69, 50.51) -> R3 Pad 1 (124.74, 61.44)
add_path([(119.69, 50.51), (119.69, 58.00), (124.74, 58.00), (124.74, 61.44)], 1.0, "Net-(U_US2-ECHO)")

# R3 Pad 2 (117.12, 61.44) -> R4 Pad 1 (117.16, 65.45) -> Pi Pin 15 (109.54, 93.56)
add_path([(117.12, 61.44), (117.16, 65.45)], 1.0, "/ECHO_R")
add_path([(117.16, 65.45), (117.16, 80.00), (109.54, 80.00), (109.54, 93.56)], 1.0, "/ECHO_R")

# ==============================================================================
# 7. TCRT5000 LINE SENSORS (Straight down to Pi)
# ==============================================================================
# TCRT5000:
# Pad 5 (99.38, 50.44) -> Pi Pin 23 (99.38, 93.56) [/LINE_R]
add_path([(99.38, 50.44), (99.38, 93.56)], 1.0, "/LINE_R")

# Pad 4 (101.92, 50.44) -> Pi Pin 21 (101.92, 93.56) [/LINE_C]
add_path([(101.92, 50.44), (101.92, 93.56)], 1.0, "/LINE_C")

# Pad 3 (104.46, 50.44) -> Pi Pin 19 (104.46, 93.56) [/LINE_L]
add_path([(104.46, 50.44), (104.46, 93.56)], 1.0, "/LINE_L")

# Pad 2 (107.00, 50.44) -> Pi Pin 17 (107.00, 93.56) [/+3V3_LOGIC]
add_path([(107.00, 50.44), (107.00, 93.56)], 1.0, "/+3V3_LOGIC")

# ==============================================================================
# 8. OLED DISPLAY (I2C) & TOP JUMPERS
# ==============================================================================
# I2C_SCL: Pi Pin 28 (94.30, 96.10) to OLED Pad 3 (147.04, 96.50)
add_path([(94.30, 96.10), (94.30, 97.50), (147.04, 97.50), (147.04, 96.50)], 1.0, "/I2C_SCL")

# I2C_SDA: Pi Pin 27 (94.30, 93.56) via JMP1 to OLED Pad 4 (144.50, 96.50)
vias.append(make_via(94.30, 89.00, "/I2C_SDA"))
vias.append(make_via(144.50, 89.00, "/I2C_SDA"))
add_path([(94.30, 93.56), (94.30, 89.00)], 1.0, "/I2C_SDA")
add_path([(144.50, 89.00), (144.50, 96.50)], 1.0, "/I2C_SDA")
silk_items.append(make_silk_jumper(94.30, 89.00, 144.50, 89.00, "JMP1: SDA (Wire 50mm)"))

# +3V3_LOGIC to OLED: Pi Pin 17 (107.00, 93.56) via JMP2 to OLED Pad 1 (152.12, 96.50)
vias.append(make_via(107.00, 86.50, "/+3V3_LOGIC"))
vias.append(make_via(152.12, 86.50, "/+3V3_LOGIC"))
add_path([(107.00, 93.56), (107.00, 86.50)], 1.0, "/+3V3_LOGIC")
add_path([(152.12, 86.50), (152.12, 96.50)], 1.0, "/+3V3_LOGIC")
silk_items.append(make_silk_jumper(107.00, 86.50, 152.12, 86.50, "JMP2: 3V3 (Wire 45mm)"))

# Insert into file
insert_pos = text.rfind('\n)')
all_new_elements = "".join(vias) + "".join(segments) + "".join(silk_items)
final_pcb = text[:insert_pos] + "\n" + all_new_elements + text[insert_pos:]

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

print(f"Success: {len(segments)} segments, {len(vias)} vias, {len(silk_items)} silk annotations written!")

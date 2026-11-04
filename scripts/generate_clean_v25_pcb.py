import math
import json
import re
import uuid

# Load world pads
with open('scripts/world_pads_actual.json', 'r', encoding='utf-8') as f:
    world_data = json.load(f)

def get_pad(ref, pad_num):
    return tuple(world_data[ref]['pads'][str(pad_num)]['world'])

def get_net(ref, pad_num):
    return world_data[ref]['pads'][str(pad_num)]['net']

def chamfer_path(pts, d=1.2):
    if len(pts) <= 2: return list(pts)
    result = [pts[0]]
    for i in range(1, len(pts) - 1):
        p_prev, p_curr, p_next = pts[i - 1], pts[i], pts[i + 1]
        dx1, dy1 = p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]
        len1 = math.hypot(dx1, dy1)
        dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        len2 = math.hypot(dx2, dy2)
        if len1 < 1e-4 or len2 < 1e-4: continue
        ux1, uy1 = dx1 / len1, dy1 / len1
        ux2, uy2 = dx2 / len2, dy2 / len2
        dot = ux1 * ux2 + uy1 * uy2
        if abs(dot) < 0.25:
            actual_d = min(d, len1 * 0.40, len2 * 0.40)
            p_in = (round(p_curr[0] - ux1 * actual_d, 4), round(p_curr[1] - uy1 * actual_d, 4))
            p_out = (round(p_curr[0] + ux2 * actual_d, 4), round(p_curr[1] + uy2 * actual_d, 4))
            result.append(p_in); result.append(p_out)
        else:
            result.append(p_curr)
    result.append(pts[-1])
    return result

paths = []
def add_chamfered(net, pts, width=1.0, d=1.2):
    c_pts = chamfer_path(pts, d=d)
    for i in range(len(c_pts) - 1):
        paths.append({'net': net, 'p1': c_pts[i], 'p2': c_pts[i+1], 'width': width})

def add_raw(net, pts, width=1.0):
    for i in range(len(pts) - 1):
        paths.append({'net': net, 'p1': pts[i], 'p2': pts[i+1], 'width': width})

vias = []
def add_via(net, at, size=2.0, drill=0.8):
    vias.append({'net': net, 'at': at, 'size': size, 'drill': drill})

def build_all_routes():
    paths.clear()
    vias.clear()

    # ---------------------------------------------------------
    # 1. TB6612 LEFT (U_TB_L)
    # ---------------------------------------------------------
    # South internal bridges (chamfered):
    add_chamfered("/AIN1_L", [get_pad('LEFT', 3), (71.50, 71.0), (66.42, 71.0), get_pad('LEFT', 5)], width=1.0, d=1.0)
    add_chamfered("/AIN2_L", [get_pad('LEFT', 2), (74.04, 68.5), (63.88, 68.5), get_pad('LEFT', 6)], width=1.0, d=1.0)
    add_chamfered("/PWMA_L", [get_pad('LEFT', 1), (76.58, 66.0), (61.34, 66.0), get_pad('LEFT', 7)], width=1.0, d=1.0)
    add_raw("GND", [get_pad('LEFT', 8), get_pad('LEFT', 16)], width=1.4)

    # South control to Pi 4:
    add_chamfered("/PWMA_L", [get_pad('LEFT', 1), (76.58, 86.0), (81.60, 90.0), get_pad('Rasp_PI4', 37)], width=1.0, d=1.2)
    add_chamfered("/STBY_L", [get_pad('LEFT', 4), (68.96, 98.50), (81.60, 98.50), get_pad('Rasp_PI4', 38)], width=1.0, d=1.2)

    # 2 Jumpers for TB1 (AIN1_L, AIN2_L):
    via_in2_1 = (74.04, 80.00)
    via_in2_2 = (84.14, 88.00)
    add_raw("/AIN2_L", [get_pad('LEFT', 2), via_in2_1], width=1.0)
    add_via("/AIN2_L", via_in2_1)
    add_raw("/AIN2_L", [via_in2_2, get_pad('Rasp_PI4', 35)], width=1.0)
    add_via("/AIN2_L", via_in2_2)

    via_in1_1 = (71.50, 80.00)
    via_in1_2 = (86.68, 86.00)
    add_raw("/AIN1_L", [get_pad('LEFT', 3), via_in1_1], width=1.0)
    add_via("/AIN1_L", via_in1_1)
    add_raw("/AIN1_L", [via_in1_2, get_pad('Rasp_PI4', 33)], width=1.0)
    add_via("/AIN1_L", via_in1_2)

    # North Motors M1 & M2:
    add_raw("/M1_A", [get_pad('LEFT', 12), get_pad('MOTOR1', 2)], width=1.0)
    add_raw("/M1_B", [get_pad('LEFT', 13), get_pad('MOTOR1', 1)], width=1.0)

    # M2 planar:
    add_chamfered("/M2_B", [
        get_pad('LEFT', 14),
        (63.88, 59.50),
        (56.50, 59.50),
        (56.50, 48.50),
        (75.53, 48.50),
        get_pad('MOTOR2', 1)
    ], width=1.0, d=1.0)

    add_chamfered("/M2_A", [
        get_pad('LEFT', 15),
        (61.34, 58.00),
        (54.50, 58.00),
        (54.50, 46.50),
        (78.07, 46.50),
        get_pad('MOTOR2', 2)
    ], width=1.0, d=1.0)

    # ---------------------------------------------------------
    # 2. TB6612 RIGHT (U_TB_R) - 100% Planar!
    # ---------------------------------------------------------
    add_chamfered("/AIN1_R", [get_pad('RIGHT', 5), (139.42, 71.0), (144.50, 71.0), get_pad('RIGHT', 3)], width=1.0, d=1.0)
    add_chamfered("/AIN2_R", [get_pad('RIGHT', 6), (136.88, 68.5), (147.04, 68.5), get_pad('RIGHT', 2)], width=1.0, d=1.0)
    add_chamfered("/PWMA_R", [get_pad('RIGHT', 7), (134.34, 66.0), (149.58, 66.0), get_pad('RIGHT', 1)], width=1.0, d=1.0)
    add_raw("GND", [get_pad('RIGHT', 8), get_pad('RIGHT', 16)], width=1.4)

    # South control to Pi 4:
    add_chamfered("/STBY_R", [get_pad('RIGHT', 4), (141.96, 80.0), (114.62, 80.0), get_pad('Rasp_PI4', 11)], width=1.0, d=1.2)
    add_chamfered("/AIN1_R", [get_pad('RIGHT', 3), (144.50, 83.0), (119.70, 83.0), get_pad('Rasp_PI4', 7)], width=1.0, d=1.2)
    add_chamfered("/AIN2_R", [get_pad('RIGHT', 2), (147.04, 86.0), (122.24, 86.0), get_pad('Rasp_PI4', 5)], width=1.0, d=1.2)
    add_chamfered("/PWMA_R", [get_pad('RIGHT', 1), (149.58, 89.0), (124.78, 89.0), get_pad('Rasp_PI4', 3)], width=1.0, d=1.2)

    # North Motors M3 & M4:
    add_chamfered("/M3_A", [get_pad('RIGHT', 12), (141.96, 56.5), (138.53, 56.5), get_pad('MOTOR3', 1)], width=1.0, d=0.8)
    add_chamfered("/M3_B", [get_pad('RIGHT', 13), (139.42, 58.0), (141.07, 58.0), get_pad('MOTOR3', 2)], width=1.0, d=0.8)

    add_chamfered("/M4_B", [
        get_pad('RIGHT', 14),
        (136.88, 59.50),
        (133.50, 59.50),
        (133.50, 48.50),
        (149.53, 48.50),
        get_pad('MOTOR4', 1)
    ], width=1.0, d=1.0)

    add_chamfered("/M4_A", [
        get_pad('RIGHT', 15),
        (134.34, 60.50),
        (131.50, 60.50),
        (131.50, 46.50),
        (152.07, 46.50),
        get_pad('MOTOR4', 2)
    ], width=1.0, d=1.0)

    # ---------------------------------------------------------
    # 3. TCRT5000 SENSOR - 100% Planar!
    # ---------------------------------------------------------
    add_raw("/LINE_R", [get_pad('TCRT5000', 5), get_pad('Rasp_PI4', 23)], width=1.0)
    add_raw("/LINE_C", [get_pad('TCRT5000', 4), get_pad('Rasp_PI4', 21)], width=1.0)
    add_raw("/LINE_L", [get_pad('TCRT5000', 3), get_pad('Rasp_PI4', 19)], width=1.0)
    add_raw("/+3V3_LOGIC", [get_pad('TCRT5000', 2), get_pad('Rasp_PI4', 17)], width=1.0)

    # ---------------------------------------------------------
    # 4. ULTRASONIC SENSORS US1 & US2 - 100% Planar!
    # ---------------------------------------------------------
    # US1 Left:
    add_chamfered("/TRIG_L", [get_pad('HC_SR04_1', 2), (87.50, 52.0), (87.50, 91.0), get_pad('Rasp_PI4', 31)], width=1.0, d=1.2)
    add_chamfered("Net-(U_US1-ECHO)", [get_pad('HC_SR04_1', 3), (91.46, 62.0), (89.22, 62.0), get_pad('R1', 1)], width=1.0, d=1.0)
    add_raw("/ECHO_L", [get_pad('R1', 2), (96.84, 69.0), get_pad('R2', 1)], width=1.0)
    add_chamfered("/ECHO_L", [get_pad('R2', 1), (96.80, 77.0), (91.76, 77.0), get_pad('Rasp_PI4', 29)], width=1.0, d=1.2)

    # US2 Right:
    add_chamfered("/TRIG_R", [get_pad('HC_SR04_2', 2), (117.15, 53.5), (109.54, 53.5), get_pad('Rasp_PI4', 15)], width=1.0, d=1.2)
    add_chamfered("Net-(U_US2-ECHO)", [get_pad('HC_SR04_2', 3), (119.69, 54.0), (124.74, 54.0), get_pad('R3', 1)], width=1.0, d=1.0)
    add_raw("/ECHO_R", [get_pad('R3', 2), get_pad('R4', 1)], width=1.0)
    add_chamfered("/ECHO_R", [get_pad('R4', 1), (117.16, 70.0), (112.08, 70.0), get_pad('Rasp_PI4', 13)], width=1.0, d=1.2)

    # ---------------------------------------------------------
    # 5. GROUND (GND) SYSTEM - 100% Planar!
    # ---------------------------------------------------------
    # Sensors West GND:
    add_chamfered("GND", [get_pad('R2', 2), (89.18, 74.0), (94.00, 74.0), get_pad('HC_SR04_1', 4)], width=1.4, d=1.0)
    add_chamfered("GND", [get_pad('HC_SR04_1', 4), (94.00, 85.0), (96.84, 88.0), get_pad('Rasp_PI4', 25)], width=1.4, d=1.2)

    # Sensors East GND:
    add_chamfered("GND", [get_pad('TCRT5000', 1), (109.54, 46.5), (122.23, 46.5), get_pad('HC_SR04_2', 4)], width=1.4, d=1.2)
    add_chamfered("GND", [get_pad('HC_SR04_2', 4), (124.78, 50.51), get_pad('R4', 2)], width=1.4, d=1.0)
    add_chamfered("GND", [get_pad('R4', 2), (124.78, 72.0), (131.80, 72.0), get_pad('RIGHT', 8)], width=1.4, d=1.0)

    # Bottom GND Trunk along Y = 101.50
    trunk_gnd_y = 101.50
    add_chamfered("GND", [get_pad('LEFT', 8), (58.80, trunk_gnd_y), (77.00, trunk_gnd_y), (77.00, 93.56), get_pad('Rasp_PI4', 39)], width=1.4, d=1.2)
    add_raw("GND", [get_pad('Rasp_PI4', 39), get_pad('Rasp_PI4', 40)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 34), (86.68, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 30), (91.76, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 20), (104.46, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 14), (112.08, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 6), (122.24, trunk_gnd_y)], width=1.4)

    # OLED GND from TB2 South Pad 8:
    add_chamfered("GND", [get_pad('RIGHT', 8), (131.80, 74.0), (149.58, 74.0), get_pad('OLED', 2)], width=1.4, d=1.2)

    # ---------------------------------------------------------
    # 6. POWER SYSTEM (+5V_PWR & VM_MOTOR) - 100% Planar!
    # ---------------------------------------------------------
    bus_5v_y = 105.00
    west_5v_x = 51.00
    top_5v_y = 44.00
    add_raw("/+5V_PWR", [get_pad('Rasp_PI4', 4), get_pad('Rasp_PI4', 2)], width=1.4)
    add_chamfered("/+5V_PWR", [
        get_pad('Rasp_PI4', 2),
        (127.32, bus_5v_y),
        (west_5v_x, bus_5v_y),
        (west_5v_x, top_5v_y),
        (74.04, top_5v_y),
        get_pad('LEFT', 10)
    ], width=1.4, d=2.0)

    # East bus for +5V: from tb2 Pad 10 to us2 and us1
    add_chamfered("/+5V_PWR", [
        get_pad('RIGHT', 10),
        (147.04, top_5v_y),
        (114.61, top_5v_y),
        get_pad('HC_SR04_2', 1)
    ], width=1.4, d=1.2)
    add_chamfered("/+5V_PWR", [
        (114.61, top_5v_y),
        (86.38, top_5v_y),
        get_pad('HC_SR04_1', 1)
    ], width=1.4, d=1.2)

    top_vm_y = 41.50
    add_chamfered("/VM_MOTOR", [
        get_pad('LEFT', 9),
        (76.58, top_vm_y),
        (149.58, top_vm_y),
        get_pad('RIGHT', 9)
    ], width=1.4, d=1.2)

    # ---------------------------------------------------------
    # 7. OLED DISPLAY (3 JUMPERS)
    # ---------------------------------------------------------
    via_sda_1 = (94.30, 87.00)
    via_sda_2 = (144.50, 94.00)
    add_raw("/I2C_SDA", [get_pad('Rasp_PI4', 27), via_sda_1], width=1.0)
    add_via("/I2C_SDA", via_sda_1)
    add_raw("/I2C_SDA", [via_sda_2, get_pad('OLED', 4)], width=1.0)
    add_via("/I2C_SDA", via_sda_2)

    via_scl_1 = (94.30, 99.00)
    via_scl_2 = (147.04, 99.00)
    add_raw("/I2C_SCL", [get_pad('Rasp_PI4', 28), via_scl_1], width=1.0)
    add_via("/I2C_SCL", via_scl_1)
    add_raw("/I2C_SCL", [via_scl_2, get_pad('OLED', 3)], width=1.0)
    add_via("/I2C_SCL", via_scl_2)

    via_3v3_1 = (107.00, 84.00)
    via_3v3_2 = (152.12, 94.00)
    add_raw("/+3V3_LOGIC", [get_pad('Rasp_PI4', 17), via_3v3_1], width=1.0)
    add_via("/+3V3_LOGIC", via_3v3_1)
    add_raw("/+3V3_LOGIC", [via_3v3_2, get_pad('OLED', 1)], width=1.0)
    add_via("/+3V3_LOGIC", via_3v3_2)

def generate_kicad_pcb(target_file):
    build_all_routes()
    
    with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove all existing segments
    content = re.sub(r'\t\(segment\s+[\s\S]*?\n\t\)\n', '', content)
    # Remove all existing vias
    content = re.sub(r'\t\(via\s+[\s\S]*?\n\t\)\n', '', content)
    
    # Remove junk gr_text (JMP..., J1..J17)
    junk_patterns = [
        r'JMP\d+:[^\"]*',
        r'J\d+:[^\"]*',
        r'Wire\s+\d+mm',
    ]
    for pat in junk_patterns:
        content = re.sub(r'\t\(gr_text\s+"' + pat + r'"[\s\S]*?\n\t\)\n', '', content)

    # Remove dash lines (jumper simulated lines)
    content = re.sub(r'\t\(gr_line[\s\S]*?\(type\s+dash\)[\s\S]*?\n\t\)\n', '', content)

    # Remove gr_circle (via circles)
    content = re.sub(r'\t\(gr_circle[\s\S]*?\(layer\s+"F\.SilkS"\)[\s\S]*?\n\t\)\n', '', content)

    # Prepare segments sexpr with (net "net_name")
    segments_sexpr = []
    for p in paths:
        net_name = p['net']
        p1 = p['p1']
        p2 = p['p2']
        w = p['width']
        u = str(uuid.uuid4())
        seg_str = (
            f'\t(segment (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) '
            f'(width {w:.2f}) (layer "B.Cu") (net "{net_name}") (uuid "{u}"))\n'
        )
        segments_sexpr.append(seg_str)

    # Prepare vias sexpr with (net "net_name")
    vias_sexpr = []
    for v in vias:
        net_name = v['net']
        at = v['at']
        sz = v['size']
        dr = v['drill']
        u = str(uuid.uuid4())
        via_str = (
            f'\t(via (at {at[0]:.4f} {at[1]:.4f}) (size {sz:.2f}) (drill {dr:.2f}) '
            f'(layers "F.Cu" "B.Cu") (net "{net_name}") (uuid "{u}"))\n'
        )
        vias_sexpr.append(via_str)

    # Find the closing parenthesis of kicad_pcb
    last_paren = content.rfind(')')
    if last_paren == -1:
        raise ValueError("Closing parenthesis not found in kicad_pcb file!")

    new_content = (
        content[:last_paren]
        + "".join(vias_sexpr)
        + "".join(segments_sexpr)
        + content[last_paren:]
    )

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully generated {target_file}!")
    print(f"  Vias: {len(vias_sexpr)}")
    print(f"  Segments: {len(segments_sexpr)}")

if __name__ == '__main__':
    generate_kicad_pcb('Pi4_Robot_Carrier_1Layer.kicad_pcb')
    generate_kicad_pcb('robot_electronics.kicad_pcb')

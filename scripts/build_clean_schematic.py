import uuid

def u():
    return str(uuid.uuid4())

with open('scripts/lib_symbols.sexpr', 'r', encoding='utf-8') as f:
    lib_symbols_content = f.read()

# Build schematic
sch_lines = []
sch_lines.append('(kicad_sch')
sch_lines.append('\t(version 20260306)')
sch_lines.append('\t(generator "eeschema")')
sch_lines.append('\t(generator_version "10.0")')
sch_lines.append('\t(uuid "d0a1b2c3-0000-0000-0000-000000000001")')
sch_lines.append('\t(paper "A3")')
sch_lines.append('\t(title_block')
sch_lines.append('\t\t(title "SO DO NGUYEN LY ROBOT 4WD RASPBERRY PI 4 (CHUAN CONG NGHIEP - 1 LOP)")')
sch_lines.append('\t\t(date "2026-11-04")')
sch_lines.append('\t\t(rev "15.0")')
sch_lines.append('\t\t(company "DATN - He Thong Nhung & Dien Tu Cong Suat")')
sch_lines.append('\t\t(comment 1 "Thiet ke chong sap nguon, loc nhieu bulk/decoupling, triet tieu ground loop")')
sch_lines.append('\t\t(comment 2 "Logic 3.3V bao ve Pi 4, STBY noi truc tiep 3.3V, 0R jumpers chinh thuc")')
sch_lines.append('\t)')
sch_lines.append(lib_symbols_content)

def add_sym(lib_id, ref, val, fp, at, pins=None):
    rot = at[2] if len(at) > 2 else "0"
    s = []
    s.append(f'\t(symbol (lib_id "{lib_id}") (at {at[0]} {at[1]} {rot}) (unit 1)')
    s.append(f'\t\t(in_bom yes) (on_board yes) (dnp no)')
    s.append(f'\t\t(uuid "{u()}")')
    s.append(f'\t\t(property "Reference" "{ref}" (at {at[0]} {float(at[1])-3.81:.2f} 0)')
    s.append(f'\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)')
    s.append(f'\t\t(property "Value" "{val}" (at {at[0]} {float(at[1])+3.81:.2f} 0)')
    s.append(f'\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)')
    s.append(f'\t\t(property "Footprint" "{fp}" (at {at[0]} {at[1]} 0)')
    s.append(f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)')
    if pins:
        for pnum in pins:
            s.append(f'\t\t(pin "{pnum}" (uuid "{u()}"))')
    s.append(f'\t\t(instances')
    for proj in ["robot_electronics", "Pi4_Robot_Carrier_1Layer"]:
        s.append(f'\t\t\t(project "{proj}"')
        s.append(f'\t\t\t\t(path "/d0a1b2c3-0000-0000-0000-000000000001"')
        s.append(f'\t\t\t\t\t(reference "{ref}")')
        s.append(f'\t\t\t\t\t(unit 1)')
        s.append(f'\t\t\t\t)')
        s.append(f'\t\t\t)')
    s.append(f'\t\t)')
    s.append('\t)')
    return "\n".join(s)

def add_label(name, pt, rot="0"):
    justify = "right bottom" if rot in ["180", "270"] else "left bottom"
    return f'\t(label "{name}" (at {pt[0]:.2f} {pt[1]:.2f} {rot}) (fields_autoplaced yes)\n\t\t(effects (font (size 1.27 1.27)) (justify {justify}))\n\t\t(uuid "{u()}")\n\t)'

def add_wire(p1, p2):
    return f'\t(wire (pts (xy {p1[0]:.2f} {p1[1]:.2f}) (xy {p2[0]:.2f} {p2[1]:.2f}))\n\t\t(stroke (width 0) (type default))\n\t\t(uuid "{u()}")\n\t)'

def add_nc(pt):
    return f'\t(no_connect (at {pt[0]:.2f} {pt[1]:.2f}) (uuid "{u()}"))'

symbols_sexpr = []
wires_sexpr = []
labels_sexpr = []
nc_sexpr = []

# 1. BT1, SW1, F1, U1
symbols_sexpr.append(add_sym('robot_electronics:Battery_2P', 'BT1', 'BAT_3S2P_11.1V',
                             'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-2-5.08',
                             ['38.10', '50.80', '0'], pins=['1', '2']))
wires_sexpr.append(add_wire([43.18, 48.26], [55.88, 48.26])) # BT1.+ to SW1.1
labels_sexpr.append(add_label('BAT+', [48.26, 48.26]))
labels_sexpr.append(add_label('GND', [43.18, 53.34]))         # BT1.- to GND

symbols_sexpr.append(add_sym('robot_electronics:SW_SPST', 'SW1', 'SW_MAIN_10A',
                             'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-2-5.08',
                             ['60.96', '48.26', '0'], pins=['1', '2']))
wires_sexpr.append(add_wire([66.04, 48.26], [81.28, 48.26])) # SW1.2 to F1.1
labels_sexpr.append(add_label('FUSE_IN', [73.66, 48.26]))

symbols_sexpr.append(add_sym('robot_electronics:Fuse', 'F1', '7.5A_Blade',
                             'robot_electronics:Fuseholder_Blade_Mini_Keystone_3568',
                             ['86.36', '48.26', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('VM_MOTOR', [91.44, 48.26]))    # F1.2 to VM_MOTOR

symbols_sexpr.append(add_sym('robot_electronics:XL4015_Buck_Module', 'U1', 'XL4015_Buck_5A',
                             'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-4-5.08',
                             ['137.16', '50.80', '0'], pins=['1', '2', '3', '4']))
labels_sexpr.append(add_label('VM_MOTOR', [116.84, 45.72], '180')) # Pin 1 IN+
labels_sexpr.append(add_label('GND', [116.84, 55.88], '180'))      # Pin 2 IN- (Star GND)
labels_sexpr.append(add_label('+5V_PWR', [157.48, 45.72]))         # Pin 3 OUT+
labels_sexpr.append(add_label('GND', [157.48, 55.88]))             # Pin 4 OUT- (Star GND)

# Bulk & Decoupling Capacitors C1..C4
symbols_sexpr.append(add_sym('robot_electronics:C_Polarized', 'C1', '470uF_25V',
                             'robot_electronics:CP_Radial_D8.0mm_P3.50mm',
                             ['182.88', '50.80', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('VM_MOTOR', [182.88, 45.72], '90'))
labels_sexpr.append(add_label('GND', [182.88, 55.88], '270'))

symbols_sexpr.append(add_sym('robot_electronics:C_Polarized', 'C2', '470uF_25V',
                             'robot_electronics:CP_Radial_D8.0mm_P3.50mm',
                             ['198.12', '50.80', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('VM_MOTOR', [198.12, 45.72], '90'))
labels_sexpr.append(add_label('GND', [198.12, 55.88], '270'))

symbols_sexpr.append(add_sym('robot_electronics:C_Polarized', 'C3', '470uF_10V',
                             'robot_electronics:CP_Radial_D6.3mm_P2.50mm',
                             ['213.36', '50.80', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('+5V_PWR', [213.36, 45.72], '90'))
labels_sexpr.append(add_label('GND', [213.36, 55.88], '270'))

symbols_sexpr.append(add_sym('robot_electronics:C_Polarized', 'C4', '100nF',
                             'robot_electronics:C_Disc_D5.0mm_W2.5mm_P5.00mm',
                             ['228.60', '50.80', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('+5V_PWR', [228.60, 45.72], '90'))
labels_sexpr.append(add_label('GND', [228.60, 55.88], '270'))

# 2. TB6612 LEFT & MOTORS
symbols_sexpr.append(add_sym('robot_electronics:Module_TB6612FNG_Breakout', 'U_TB1', 'TB6612_Left',
                             'robot_electronics:Module_TB6612FNG_Breakout',
                             ['81.28', '127.00', '0'], pins=[str(i) for i in range(1, 17)]))
labels_sexpr.append(add_label('PWMA_L', [58.42, 109.22], '180'))
labels_sexpr.append(add_label('AIN2_L', [58.42, 114.30], '180'))
labels_sexpr.append(add_label('AIN1_L', [58.42, 119.38], '180'))
labels_sexpr.append(add_label('+3V3_LOGIC', [58.42, 124.46], '180')) # STBY -> 3.3V
labels_sexpr.append(add_label('AIN1_L', [58.42, 129.54], '180'))     # BIN1 -> AIN1
labels_sexpr.append(add_label('AIN2_L', [58.42, 134.62], '180'))     # BIN2 -> AIN2
labels_sexpr.append(add_label('PWMA_L', [58.42, 139.70], '180'))     # PWMB -> PWMA
labels_sexpr.append(add_label('GND', [58.42, 144.78], '180'))
labels_sexpr.append(add_label('VM_MOTOR', [104.14, 109.22]))
labels_sexpr.append(add_label('+3V3_LOGIC', [104.14, 114.30]))        # VCC -> 3.3V
labels_sexpr.append(add_label('GND', [104.14, 119.38]))
labels_sexpr.append(add_label('M1_A', [104.14, 124.46]))
labels_sexpr.append(add_label('M1_B', [104.14, 129.54]))
labels_sexpr.append(add_label('M2_B', [104.14, 134.62]))
labels_sexpr.append(add_label('M2_A', [104.14, 139.70]))
labels_sexpr.append(add_label('GND', [104.14, 144.78]))

symbols_sexpr.append(add_sym('robot_electronics:Conn_01x02', 'J_M1', 'MOTOR_FL',
                             'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-2-5.08',
                             ['132.08', '127.00', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('M1_A', [127.00, 124.46], '180'))
labels_sexpr.append(add_label('M1_B', [127.00, 129.54], '180'))

symbols_sexpr.append(add_sym('robot_electronics:Conn_01x02', 'J_M2', 'MOTOR_RL',
                             'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-2-5.08',
                             ['132.08', '137.16', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('M2_B', [127.00, 134.62], '180'))
labels_sexpr.append(add_label('M2_A', [127.00, 139.70], '180'))

# 3. TB6612 RIGHT & MOTORS
symbols_sexpr.append(add_sym('robot_electronics:Module_TB6612FNG_Breakout', 'U_TB2', 'TB6612_Right',
                             'robot_electronics:Module_TB6612FNG_Breakout',
                             ['299.72', '127.00', '0'], pins=[str(i) for i in range(1, 17)]))
labels_sexpr.append(add_label('PWMA_R', [276.86, 109.22], '180'))
labels_sexpr.append(add_label('AIN2_R', [276.86, 114.30], '180'))
labels_sexpr.append(add_label('AIN1_R', [276.86, 119.38], '180'))
labels_sexpr.append(add_label('+3V3_LOGIC', [276.86, 124.46], '180')) # STBY -> 3.3V
labels_sexpr.append(add_label('AIN1_R', [276.86, 129.54], '180'))     # BIN1 -> AIN1
labels_sexpr.append(add_label('AIN2_R', [276.86, 134.62], '180'))     # BIN2 -> AIN2
labels_sexpr.append(add_label('PWMA_R', [276.86, 139.70], '180'))     # PWMB -> PWMA
labels_sexpr.append(add_label('GND', [276.86, 144.78], '180'))
labels_sexpr.append(add_label('VM_MOTOR', [322.58, 109.22]))
labels_sexpr.append(add_label('+3V3_LOGIC', [322.58, 114.30]))        # VCC -> 3.3V
labels_sexpr.append(add_label('GND', [322.58, 119.38]))
labels_sexpr.append(add_label('M3_A', [322.58, 124.46]))
labels_sexpr.append(add_label('M3_B', [322.58, 129.54]))
labels_sexpr.append(add_label('M4_B', [322.58, 134.62]))
labels_sexpr.append(add_label('M4_A', [322.58, 139.70]))
labels_sexpr.append(add_label('GND', [322.58, 144.78]))

symbols_sexpr.append(add_sym('robot_electronics:Conn_01x02', 'J_M3', 'MOTOR_FR',
                             'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-2-5.08',
                             ['350.52', '127.00', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('M3_A', [345.44, 124.46], '180'))
labels_sexpr.append(add_label('M3_B', [345.44, 129.54], '180'))

symbols_sexpr.append(add_sym('robot_electronics:Conn_01x02', 'J_M4', 'MOTOR_RR',
                             'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-2-5.08',
                             ['350.52', '137.16', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('M4_B', [345.44, 134.62], '180'))
labels_sexpr.append(add_label('M4_A', [345.44, 139.70], '180'))

# 4. SENSORS (US1, US2, TCRT5000, OLED)
# US1
symbols_sexpr.append(add_sym('robot_electronics:Sensor_HC_SR04', 'U_US1', 'HC_SR04_Left',
                             'robot_electronics:Sensor_HC_SR04',
                             ['76.20', '190.50', '0'], pins=['1', '2', '3', '4']))
labels_sexpr.append(add_label('+5V_PWR', [58.42, 185.42], '180'))
labels_sexpr.append(add_label('TRIG_L', [58.42, 193.04], '180'))
wires_sexpr.append(add_wire([93.98, 193.04], [109.22, 193.04])) # ECHO to R1.1
labels_sexpr.append(add_label('GND', [93.98, 198.12]))

# R1 & R2
symbols_sexpr.append(add_sym('robot_electronics:R', 'R1', '1k',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['114.30', '193.04', '90'], pins=['1', '2']))
wires_sexpr.append(add_wire([119.38, 193.04], [119.38, 200.66])) # R1.2 to R2.1
labels_sexpr.append(add_label('ECHO_L', [119.38, 193.04]))

symbols_sexpr.append(add_sym('robot_electronics:R', 'R2', '2k',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['119.38', '205.74', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('GND', [119.38, 210.82], '270'))

# US2
symbols_sexpr.append(add_sym('robot_electronics:Sensor_HC_SR04', 'U_US2', 'HC_SR04_Right',
                             'robot_electronics:Sensor_HC_SR04',
                             ['299.72', '190.50', '0'], pins=['1', '2', '3', '4']))
labels_sexpr.append(add_label('+5V_PWR', [281.94, 185.42], '180'))
labels_sexpr.append(add_label('TRIG_R', [281.94, 193.04], '180'))
wires_sexpr.append(add_wire([317.50, 193.04], [332.74, 193.04])) # ECHO to R3.1
labels_sexpr.append(add_label('GND', [317.50, 198.12]))

# R3 & R4
symbols_sexpr.append(add_sym('robot_electronics:R', 'R3', '1k',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['337.82', '193.04', '90'], pins=['1', '2']))
wires_sexpr.append(add_wire([342.90, 193.04], [342.90, 200.66])) # R3.2 to R4.1
labels_sexpr.append(add_label('ECHO_R', [342.90, 193.04]))

symbols_sexpr.append(add_sym('robot_electronics:R', 'R4', '2k',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['342.90', '205.74', '0'], pins=['1', '2']))
labels_sexpr.append(add_label('GND', [342.90, 210.82], '270'))

# TCRT5000_3CH
symbols_sexpr.append(add_sym('robot_electronics:Sensor_Line_TCRT5000_3CH', 'U_LINE', 'TCRT5000_3CH',
                             'robot_electronics:Sensor_Line_TCRT5000_3CH',
                             ['187.96', '182.88', '0'], pins=['1', '2', '3', '4', '5']))
labels_sexpr.append(add_label('GND', [170.18, 190.50], '180'))
labels_sexpr.append(add_label('+3V3_LOGIC', [170.18, 175.26], '180'))
labels_sexpr.append(add_label('LINE_R', [205.74, 177.80]))
labels_sexpr.append(add_label('LINE_C', [205.74, 182.88]))
labels_sexpr.append(add_label('LINE_L', [205.74, 187.96]))

# OLED 1.3"
symbols_sexpr.append(add_sym('robot_electronics:Display_OLED_1.3_I2C', 'J_OLED', 'OLED_1.3_I2C',
                             'robot_electronics:Sensor_OLED_1.3',
                             ['314.96', '256.54', '0'], pins=['1', '2', '3', '4']))
labels_sexpr.append(add_label('+3V3_LOGIC', [299.72, 252.73], '180'))
labels_sexpr.append(add_label('GND', [299.72, 260.35], '180'))
labels_sexpr.append(add_label('I2C_SCL', [330.20, 252.73]))
labels_sexpr.append(add_label('I2C_SDA', [330.20, 260.35]))

# 5. ZERO-OHM JUMPERS R_JMP1..R_JMP6
symbols_sexpr.append(add_sym('robot_electronics:R', 'R_JMP1', '0R',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['254.00', '307.34', '90'], pins=['1', '2']))
wires_sexpr.append(add_wire([226.06, 307.34], [248.92, 307.34])) # Pi4 Pin 32 to R_JMP1.1
labels_sexpr.append(add_label('PWMA_R', [259.08, 307.34]))

symbols_sexpr.append(add_sym('robot_electronics:R', 'R_JMP2', '0R',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['254.00', '317.50', '90'], pins=['1', '2']))
wires_sexpr.append(add_wire([226.06, 317.50], [248.92, 317.50])) # Pi4 Pin 36 to R_JMP2.1
labels_sexpr.append(add_label('AIN1_R', [259.08, 317.50]))

symbols_sexpr.append(add_sym('robot_electronics:R', 'R_JMP3', '0R',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['254.00', '322.58', '90'], pins=['1', '2']))
wires_sexpr.append(add_wire([226.06, 322.58], [248.92, 322.58])) # Pi4 Pin 38 to R_JMP3.1
labels_sexpr.append(add_label('AIN2_R', [259.08, 322.58]))

symbols_sexpr.append(add_sym('robot_electronics:R', 'R_JMP4', '0R',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['254.00', '241.30', '90'], pins=['1', '2']))
labels_sexpr.append(add_label('+5V_PWR', [248.92, 241.30], '180'))
labels_sexpr.append(add_label('+5V_PWR', [259.08, 241.30]))

symbols_sexpr.append(add_sym('robot_electronics:R', 'R_JMP5', '0R',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['254.00', '251.46', '90'], pins=['1', '2']))
labels_sexpr.append(add_label('+3V3_LOGIC', [248.92, 251.46], '180'))
labels_sexpr.append(add_label('+3V3_LOGIC', [259.08, 251.46]))

symbols_sexpr.append(add_sym('robot_electronics:R', 'R_JMP6', '0R',
                             'robot_electronics:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
                             ['254.00', '261.62', '90'], pins=['1', '2']))
labels_sexpr.append(add_label('GND', [248.92, 261.62], '180'))
labels_sexpr.append(add_label('GND', [259.08, 261.62]))

# 6. RASPBERRY PI 4 (40-PIN)
symbols_sexpr.append(add_sym('robot_electronics:Raspberry_Pi_4_40Pin', 'U_PI4', 'Raspberry_Pi_4_40Pin',
                             'robot_electronics:PinSocket_2x20_P2.54mm_Vertical',
                             ['187.96', '279.40', '0'], pins=[str(i) for i in range(1, 41)]))

# Row 1 (Odd pins, X = 149.86)
labels_sexpr.append(add_label('+3V3_LOGIC', [149.86, 231.14], '180')) # Pin 1
labels_sexpr.append(add_label('I2C_SDA', [149.86, 236.22], '180'))    # Pin 3
labels_sexpr.append(add_label('I2C_SCL', [149.86, 241.30], '180'))    # Pin 5
nc_sexpr.append(add_nc([149.86, 246.38]))                            # Pin 7
labels_sexpr.append(add_label('GND', [149.86, 251.46], '180'))        # Pin 9
labels_sexpr.append(add_label('TRIG_L', [149.86, 256.54], '180'))     # Pin 11
labels_sexpr.append(add_label('ECHO_L', [149.86, 261.62], '180'))     # Pin 13
nc_sexpr.append(add_nc([149.86, 266.70]))                            # Pin 15
nc_sexpr.append(add_nc([149.86, 271.78]))                            # Pin 17
labels_sexpr.append(add_label('LINE_L', [149.86, 276.86], '180'))     # Pin 19
labels_sexpr.append(add_label('LINE_C', [149.86, 281.94], '180'))     # Pin 21
labels_sexpr.append(add_label('LINE_R', [149.86, 287.02], '180'))     # Pin 23
labels_sexpr.append(add_label('GND', [149.86, 292.10], '180'))        # Pin 25
nc_sexpr.append(add_nc([149.86, 297.18]))                            # Pin 27
nc_sexpr.append(add_nc([149.86, 302.26]))                            # Pin 29
nc_sexpr.append(add_nc([149.86, 307.34]))                            # Pin 31
labels_sexpr.append(add_label('PWMA_L', [149.86, 312.42], '180'))    # Pin 33
labels_sexpr.append(add_label('AIN2_L', [149.86, 317.50], '180'))    # Pin 35
labels_sexpr.append(add_label('AIN1_L', [149.86, 322.58], '180'))    # Pin 37
labels_sexpr.append(add_label('GND', [149.86, 327.66], '180'))        # Pin 39

# Row 2 (Even pins, X = 226.06)
labels_sexpr.append(add_label('+5V_PWR', [226.06, 231.14]))           # Pin 2
labels_sexpr.append(add_label('+5V_PWR', [226.06, 236.22]))           # Pin 4
labels_sexpr.append(add_label('GND', [226.06, 241.30]))               # Pin 6
nc_sexpr.append(add_nc([226.06, 246.38]))                            # Pin 8
nc_sexpr.append(add_nc([226.06, 251.46]))                            # Pin 10
nc_sexpr.append(add_nc([226.06, 256.54]))                            # Pin 12
labels_sexpr.append(add_label('GND', [226.06, 261.62]))              # Pin 14
labels_sexpr.append(add_label('TRIG_R', [226.06, 266.70]))           # Pin 16
labels_sexpr.append(add_label('ECHO_R', [226.06, 271.78]))           # Pin 18
labels_sexpr.append(add_label('GND', [226.06, 276.86]))              # Pin 20
nc_sexpr.append(add_nc([226.06, 281.94]))                            # Pin 22
nc_sexpr.append(add_nc([226.06, 287.02]))                            # Pin 24
nc_sexpr.append(add_nc([226.06, 292.10]))                            # Pin 26
nc_sexpr.append(add_nc([226.06, 297.18]))                            # Pin 28
labels_sexpr.append(add_label('GND', [226.06, 302.26]))              # Pin 30
# Pin 32 wired to R_JMP1
labels_sexpr.append(add_label('GND', [226.06, 312.42]))              # Pin 34
# Pin 36 wired to R_JMP2
# Pin 38 wired to R_JMP3
nc_sexpr.append(add_nc([226.06, 327.66]))                            # Pin 40

# Assemble
sch_lines.extend(symbols_sexpr)
sch_lines.extend(wires_sexpr)
sch_lines.extend(labels_sexpr)
sch_lines.extend(nc_sexpr)
sch_lines.append(f'\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)')
sch_lines.append(')')

full_sch = "\n".join(sch_lines) + "\n"

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(full_sch)

with open('robot_electronics.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(full_sch)

print("Regenerated clean schematic with instances!")

import re
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Load current PCB
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Update net names on pads of Rasp_PI4
# We update the net assignments in the footprint
net_updates = {
    # Left motor & sensor pins (on physical LEFT of header)
    "33": "/PWMA_L",
    "35": "/AIN2_L",
    "37": "/AIN1_L",
    "38": "/STBY_L",
    "29": "/TRIG_L",
    "31": "/ECHO_L",
    # Right motor & sensor pins (on physical RIGHT of header)
    "3": "/PWMA_R",
    "5": "/AIN2_R",
    "7": "/AIN1_R",
    "11": "/STBY_R",
    "13": "/TRIG_R",
    "15": "/ECHO_R",
    # Line sensors
    "19": "/LINE_L",
    "21": "/LINE_C",
    "23": "/LINE_R",
    # I2C
    "27": "/I2C_SDA",
    "28": "/I2C_SCL",
    # Power & Ground
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

def update_pi_pad_nets(fp_text):
    for pad_num, net_name in net_updates.items():
        # Find pad "pad_num"
        pattern = rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"'
        fp_text = re.sub(pattern, rf'\1"{net_name}"', fp_text)
    return fp_text

# Update LEFT and RIGHT TB6612 nets:
# In LEFT:
# Pads 1, 7: /PWMA_L
# Pads 2, 6: /AIN2_L
# Pads 3, 5: /AIN1_L
# Pad 4: /STBY_L
# In RIGHT:
# Pads 1, 7: /PWMA_R
# Pads 2, 6: /AIN2_R
# Pads 3, 5: /AIN1_R
# Pad 4: /STBY_R

def update_tb_nets(fp_text, is_left=True):
    prefix = "_L" if is_left else "_R"
    updates = {
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
        "12": f"/M1_A" if is_left else f"/M3_A",
        "13": f"/M1_B" if is_left else f"/M3_B",
        "14": f"/M2_B" if is_left else f"/M4_B",
        "15": f"/M2_A" if is_left else f"/M4_A",
        "16": "GND"
    }
    for pad_num, net_name in updates.items():
        pattern = rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"'
        fp_text = re.sub(pattern, rf'\1"{net_name}"', fp_text)
    return fp_text

def fp_repl(m):
    fp = m.group(0)
    if 'TB6612_Left' in fp or 'reference "LEFT"' in fp:
        return update_tb_nets(fp, is_left=True)
    elif 'TB6612_Right' in fp or 'reference "RIGHT"' in fp:
        return update_tb_nets(fp, is_left=False)
    elif 'Raspberry_Pi_4_40Pin' in fp or 'reference "Rasp_PI4"' in fp:
        return update_pi_pad_nets(fp)
    return fp

text = re.sub(r'\(footprint\s+"[^"]+"[\s\S]*?\n\t\)', fp_repl, text)

# Remove all existing segments and vias to lay down the new clean routing
text = re.sub(r'\t\(segment[\s\S]*?\n\t\)\n', '', text)
text = re.sub(r'\t\(via[\s\S]*?\n\t\)\n', '', text)
# Remove old jumper silkscreen
text = re.sub(r'\t\(gr_line\s+\(start\s+112\.08[\s\S]*?\n\t\)\n', '', text)
text = re.sub(r'\t\(gr_circle[\s\S]*?JMP[\s\S]*?\n\t\)\n', '', text)
text = re.sub(r'\t\(gr_text\s+"JMP[\s\S]*?\n\t\)\n', '', text)

print("Footprint nets updated and old segments stripped.")
with open('scripts/build_rerouted_pcb.py', 'w', encoding='utf-8') as f:
    f.write("# Routing builder\n")

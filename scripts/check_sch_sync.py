import re

def check_sch(sch_path):
    print(f"=== Inspecting {sch_path} ===")
    with open(sch_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    labels = re.findall(r'\(label\s+"([^"]+)"\s+\(at\s+([-\d.]+)\s+([-\d.]+)', text)
    print(f"Total labels in {sch_path}: {len(labels)}")
    for l in labels:
        if any(k in l[0] for k in ['PWM', 'AIN', 'BIN', 'STBY', 'TRIG', 'ECHO', 'LINE', 'SDA', 'SCL', '3V3', '5V']):
            print(f"  Label: {l[0]:<20} at ({l[1]}, {l[2]})")

check_sch('Pi4_Robot_Carrier_1Layer.kicad_sch')

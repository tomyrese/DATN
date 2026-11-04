import math
import json
import re
import uuid
import subprocess

from geometry_validator import test_track, all_pads
from interactive_router import chamfer_path, P, N, fps

def collect_clean_routes():
    accepted_tracks = []
    
    def try_route(net_name, pts, width=1.0, d=1.2, is_raw=False):
        c_pts = pts if is_raw else chamfer_path(pts, d=d)
        segs = []
        for i in range(len(c_pts) - 1):
            segs.append({
                'net_name': net_name,
                'p1': c_pts[i],
                'p2': c_pts[i+1],
                'width': width
            })
        
        for s in segs:
            ok, reason = test_track(s, accepted_tracks, all_pads, min_clearance=0.50)
            if not ok:
                return False
                
        for s in segs:
            accepted_tracks.append(s)
        return True

    # 1. Power Block (BAT, SW, FUSE, BUCK)
    try_route("/BAT+", [P('BT1', 1), P('SW1', 1)], width=1.4, is_raw=True)
    try_route("/FUSE_IN", [P('SW1', 2), (52.54, 62.00), (46.00, 68.54), P('F1', 1)], width=1.4, is_raw=True)
    try_route("/VM_MOTOR", [P('F1', 2), (54.00, 76.00), (52.00, 78.00), (42.38, 78.00), P('U1', 1)], width=1.4, is_raw=True)
    try_route("/VM_MOTOR", [P('U_TB1', 9), (56.00, 60.38), (56.00, 46.25), P('C1', 1)], width=1.4, d=1.0)

    # 2. Motor Outputs Left & Right (1.4mm)
    try_route("/M1_A", [P('U_TB1', 12), (66.73, 52.00), (65.46, 50.73), P('J_M1', 1)], width=1.4, is_raw=True)
    try_route("/M1_B", [P('U_TB1', 13), (69.27, 52.00), (70.54, 50.73), P('J_M1', 2)], width=1.4, is_raw=True)
    try_route("/M2_B", [P('U_TB1', 14), (71.81, 55.00), (74.46, 52.35), P('J_M2', 1)], width=1.4, is_raw=True)
    try_route("/M2_A", [P('U_TB1', 15), (74.35, 57.00), (79.54, 51.81), P('J_M2', 2)], width=1.4, is_raw=True)

    try_route("/M3_A", [P('U_TB2', 12), (138.73, 52.00), (137.46, 50.73), P('J_M3', 1)], width=1.4, is_raw=True)
    try_route("/M3_B", [P('U_TB2', 13), (141.27, 52.00), (142.54, 50.73), P('J_M3', 2)], width=1.4, is_raw=True)
    try_route("/M4_B", [P('U_TB2', 14), (143.81, 55.00), (146.46, 52.35), P('J_M4', 1)], width=1.4, is_raw=True)
    try_route("/M4_A", [P('U_TB2', 15), (146.35, 57.00), (151.54, 51.81), P('J_M4', 2)], width=1.4, is_raw=True)

    # 3. TB6612 Internal U-Loops (1.0mm)
    try_route("/AIN1_L", [P('U_TB1', 3), (64.19, 71.00), (69.27, 71.00), P('U_TB1', 5)], width=1.0, is_raw=True)
    try_route("/AIN2_L", [P('U_TB1', 2), (61.65, 68.00), (71.81, 68.00), P('U_TB1', 6)], width=1.0, is_raw=True)
    try_route("/PWMA_L", [P('U_TB1', 1), (59.11, 65.00), (74.35, 65.00), P('U_TB1', 7)], width=1.0, is_raw=True)

    try_route("/AIN1_R", [P('U_TB2', 3), (136.19, 71.00), (141.27, 71.00), P('U_TB2', 5)], width=1.0, is_raw=True)
    try_route("/AIN2_R", [P('U_TB2', 2), (133.65, 68.00), (143.81, 68.00), P('U_TB2', 6)], width=1.0, is_raw=True)
    try_route("/PWMA_R", [P('U_TB2', 1), (131.11, 65.00), (146.35, 65.00), P('U_TB2', 7)], width=1.0, is_raw=True)

    # 4. Left Motor Control from Pi 4 (1.0mm)
    try_route("/AIN1_L", [P('U_PI4', 37), (81.60, 90.00), (69.27, 90.00), P('U_TB1', 5)], width=1.0, d=1.0)
    try_route("/AIN2_L", [P('U_PI4', 35), (84.14, 87.50), (71.81, 87.50), P('U_TB1', 6)], width=1.0, d=1.0)
    try_route("/PWMA_L", [P('U_PI4', 33), (86.68, 85.00), (74.35, 85.00), P('U_TB1', 7)], width=1.0, d=1.0)

    # 5. Right Motor Control via Jumpers R_JMP1..3 (1.0mm)
    try_route("Net-(U_PI4-GPIO12_PWMB_R)", [
        P('U_PI4', 32), (89.22, 104.00), (131.00, 104.00), (131.00, 93.00), (130.00, 92.00), P('R_JMP1', 1)
    ], width=1.0, d=1.0)
    try_route("Net-(U_PI4-GPIO16_AIN1_R)", [
        P('U_PI4', 36), (84.14, 105.50), (133.50, 105.50), P('R_JMP2', 1)
    ], width=1.0, d=1.0)
    try_route("Net-(U_PI4-GPIO20_AIN2_R)", [
        P('U_PI4', 38), (81.60, 107.00), (137.00, 107.00), P('R_JMP3', 1)
    ], width=1.0, d=1.0)

    try_route("/PWMA_R", [P('R_JMP1', 2), (130.00, 77.00), (131.11, 75.89), P('U_TB2', 1)], width=1.0, is_raw=True)

    # 6. Ultrasonic Sensor Dividers (1.0mm)
    try_route("Net-(U_US1-ECHO)", [P('U_US1', 3), (93.27, 51.00), (88.19, 51.00), P('R1', 1)], width=1.0, is_raw=True)
    try_route("/ECHO_L", [P('R1', 2), (95.81, 62.00), (88.19, 62.00), P('R2', 1)], width=1.0, is_raw=True)
    try_route("Net-(U_US2-ECHO)", [P('U_US2', 3), (121.27, 51.00), (116.19, 51.00), P('R3', 1)], width=1.0, is_raw=True)
    try_route("/ECHO_R", [P('R3', 2), (123.81, 62.00), (116.19, 62.00), P('R4', 1)], width=1.0, is_raw=True)

    # 7. Primary Power (VM_MOTOR, 1.4mm)
    try_route("/VM_MOTOR", [
        (42.38, 78.00), (40.00, 78.00), (40.00, 38.50), (133.00, 38.50), P('C2', 1)
    ], width=1.4, d=1.0)

    # 8. TB6612 Module GND Loops (1.4mm)
    try_route("/GND", [P('U_TB1', 16), (76.89, 68.00), P('U_TB1', 8)], width=1.4, is_raw=True)
    try_route("/GND", [P('U_TB2', 16), (148.89, 68.00), P('U_TB2', 8)], width=1.4, is_raw=True)
    try_route("/+5V_PWR", [P('U_PI4', 2), P('U_PI4', 4)], width=1.4, is_raw=True)

    return accepted_tracks

def generate_pcb_file(out_path):
    tracks = collect_clean_routes()
    print(f"Total tracks to write: {len(tracks)}")

    # Read base PCB for footprints and net table
    with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
        orig = f.read()

    # Extract net list mapping: name -> net_id
    net_map = {}
    for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]+)"\)', orig):
        net_map[m.group(2)] = int(m.group(1))

    # Clean out old tracks, vias, graphics, and old Edge.Cuts
    # Extract all footprint blocks
    fp_blocks = []
    for m in re.finditer(r'\(footprint\s+"[^"]+".*?\n\t\)', orig, re.DOTALL):
        fp_str = m.group(0)
        # Clean silkscreen in footprints: remove long jumper text
        fp_str = re.sub(r'\(property\s+"Value"\s+"[^"]*Wire[^"]*"', '(property "Value" "0R"', fp_str)
        fp_blocks.append(fp_str)

    print(f"Preserved {len(fp_blocks)} clean footprints.")

    # Build Header
    lines = [
        '(kicad_pcb',
        '\t(version 20260206)',
        '\t(generator "pcbnew")',
        '\t(generator_version "10.0")',
        '\t(general',
        '\t\t(thickness 1.6)',
        '\t\t(legacy_teardrops no)',
        '\t)',
        '\t(paper "A4")',
        '\t(layers',
        '\t\t(0 "F.Cu" signal)',
        '\t\t(2 "B.Cu" signal)',
        '\t\t(9 "F.Adhes" user "F.Adhesive")',
        '\t\t(11 "B.Adhes" user "B.Adhesive")',
        '\t\t(13 "F.Paste" user)',
        '\t\t(15 "B.Paste" user)',
        '\t\t(5 "F.SilkS" user "F.Silkscreen")',
        '\t\t(7 "B.SilkS" user "B.Silkscreen")',
        '\t\t(1 "F.Mask" user)',
        '\t\t(3 "B.Mask" user)',
        '\t\t(17 "Dwgs.User" user "User.Drawings")',
        '\t\t(19 "Cmts.User" user "User.Comments")',
        '\t\t(21 "Eco1.User" user "User.Eco1")',
        '\t\t(23 "Eco2.User" user "User.Eco2")',
        '\t\t(25 "Edge.Cuts" user)',
        '\t\t(27 "Margin" user)',
        '\t\t(31 "F.CrtYd" user "F.Courtyard")',
        '\t\t(29 "B.CrtYd" user "B.Courtyard")',
        '\t\t(35 "F.Fab" user)',
        '\t\t(33 "B.Fab" user)',
        '\t)',
        '\t(setup',
        '\t\t(pad_to_mask_clearance 0)',
        '\t\t(solder_mask_min_width 0)',
        '\t\t(pad_to_paste_clearance 0)',
        '\t\t(pcbplotparams',
        '\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)',
        '\t\t\t(plot_black_and_white yes)',
        '\t\t\t(outputformat 1)',
        '\t\t)',
        '\t)',
        '\t(net 0 "")'
    ]

    # Add nets
    for name, nid in sorted(net_map.items(), key=lambda x: x[1]):
        if nid > 0:
            lines.append(f'\t(net {nid} "{name}")')

    # Add Footprints
    for fp in fp_blocks:
        lines.append(fp)

    # Add Segments (B.Cu only, 0 Vias)
    for seg in tracks:
        net_name = seg['net_name']
        nid = net_map.get(net_name, 0)
        p1 = seg['p1']
        p2 = seg['p2']
        w = seg['width']
        u = str(uuid.uuid4())
        lines.append(f'\t(segment (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (width {w:.4f}) (layer "B.Cu") (net {nid}) (tstamp {u}))')

    # Add Clean Edge.Cuts (Closed rectangle: X=36..158, Y=35..112)
    # Using 4 lines
    min_x, max_x = 36.0, 158.0
    min_y, max_y = 35.0, 112.0
    lines.append(f'\t(gr_line (start {min_x:.4f} {min_y:.4f}) (end {max_x:.4f} {min_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
    lines.append(f'\t(gr_line (start {max_x:.4f} {min_y:.4f}) (end {max_x:.4f} {max_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
    lines.append(f'\t(gr_line (start {max_x:.4f} {max_y:.4f}) (end {min_x:.4f} {max_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
    lines.append(f'\t(gr_line (start {min_x:.4f} {max_y:.4f}) (end {min_x:.4f} {min_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')

    # Add Silk Labels
    def add_text(txt, x, y, size=1.2):
        lines.append(f'\t(gr_text "{txt}" (at {x:.4f} {y:.4f}) (layer "F.SilkS") (effects (font (size {size} {size}) (thickness 0.15))) (tstamp {uuid.uuid4()}))')

    add_text("ROBOT 4WD RASPBERRY PI 4 - SINGLE LAYER PCB", 97.0, 37.0, size=1.5)
    add_text("BAT 11.1V", 50.0, 38.5, size=1.0)
    add_text("MAIN SW", 50.0, 52.5, size=1.0)
    add_text("FUSE 7.5A", 50.0, 66.5, size=1.0)
    add_text("XL4015 5V", 50.0, 84.5, size=1.0)
    add_text("M1 (FL)", 68.0, 41.5, size=1.0)
    add_text("M2 (RL)", 77.0, 41.5, size=1.0)
    add_text("M3 (FR)", 140.0, 41.5, size=1.0)
    add_text("M4 (RR)", 149.0, 41.5, size=1.0)
    add_text("US LEFT", 92.0, 41.5, size=1.0)
    add_text("LINE 3CH", 106.0, 41.5, size=1.0)
    add_text("US RIGHT", 120.0, 41.5, size=1.0)
    add_text("OLED 1.3", 145.0, 91.5, size=1.0)

    lines.append(')')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote {len(lines)} lines to {out_path}.")

if __name__ == '__main__':
    generate_pcb_file('Pi4_Robot_Carrier_1Layer.kicad_pcb')
    generate_pcb_file('robot_electronics.kicad_pcb')

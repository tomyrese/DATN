import math
import json
import re
import uuid

# First parse exact world pads from the updated PCB
import parse_world_pads_exact
fps = parse_world_pads_exact.parse_pcb_world_pads('Pi4_Robot_Carrier_1Layer.kicad_pcb')

from geometry_validator import test_track, all_pads
from interactive_router import chamfer_path

def P(ref, pnum):
    p = fps[ref]['pads'][str(pnum)]
    return (p['wx'], p['wy'])

def N(ref, pnum):
    return fps[ref]['pads'][str(pnum)]['net_name']

# Reload all_pads with the updated fps
all_pads.clear()
for ref, f_data in fps.items():
    for pnum, p in f_data['pads'].items():
        all_pads.append({
            'ref': ref,
            'pnum': pnum,
            'x': p['wx'],
            'y': p['wy'],
            'net_id': p['net_id'],
            'net_name': p['net_name'],
            'radius': p['size'][0] / 2.0
        })

print(f"Reloaded {len(all_pads)} pads from updated PCB.")

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
            print(f"[REJECT / RATSNEST] {net_name}: {reason} | seg {s['p1']} -> {s['p2']}")
            return False
            
    for s in segs:
        accepted_tracks.append(s)
    print(f"[ACCEPTED] {net_name}: {len(segs)} segs")
    return True

print("\n--- 1. Power Supply ---")
try_route("/BAT+", [P('BT1', 1), P('SW1', 1)], width=1.4, is_raw=True)
try_route("/FUSE_IN", [P('SW1', 2), (52.54, 62.00), (46.00, 68.54), P('F1', 1)], width=1.4, is_raw=True)
try_route("/VM_MOTOR", [P('F1', 2), (54.00, 76.00), (52.00, 78.00), (42.38, 78.00), P('U1', 1)], width=1.4, is_raw=True)

# VM_MOTOR from F1.2 to U_TB1.9
try_route("/VM_MOTOR", [P('F1', 2), (54.00, 62.50), (56.12, 60.38), P('U_TB1', 9)], width=1.4, is_raw=True)

print("\n--- 2. Motor Outputs Left & Right (1.4mm) ---")
try_route("/M1_A", [P('U_TB1', 12), (66.73, 52.00), (65.46, 50.73), P('J_M1', 1)], width=1.4, is_raw=True)
try_route("/M1_B", [P('U_TB1', 13), (69.27, 52.00), (70.54, 50.73), P('J_M1', 2)], width=1.4, is_raw=True)
try_route("/M2_B", [P('U_TB1', 14), (71.81, 55.00), (74.46, 52.35), P('J_M2', 1)], width=1.4, is_raw=True)
try_route("/M2_A", [P('U_TB1', 15), (74.35, 57.00), (79.54, 51.81), P('J_M2', 2)], width=1.4, is_raw=True)

try_route("/M3_A", [P('U_TB2', 12), (138.73, 52.00), (137.46, 50.73), P('J_M3', 1)], width=1.4, is_raw=True)
try_route("/M3_B", [P('U_TB2', 13), (141.27, 52.00), (142.54, 50.73), P('J_M3', 2)], width=1.4, is_raw=True)
try_route("/M4_B", [P('U_TB2', 14), (143.81, 55.00), (146.46, 52.35), P('J_M4', 1)], width=1.4, is_raw=True)
try_route("/M4_A", [P('U_TB2', 15), (146.35, 57.00), (151.54, 51.81), P('J_M4', 2)], width=1.4, is_raw=True)

print("\n--- 3. TB6612 Internal U-Loops (1.0mm) ---")
try_route("/AIN1_L", [P('U_TB1', 3), (64.19, 71.00), (69.27, 71.00), P('U_TB1', 5)], width=1.0, is_raw=True)
try_route("/AIN2_L", [P('U_TB1', 2), (61.65, 68.00), (71.81, 68.00), P('U_TB1', 6)], width=1.0, is_raw=True)
try_route("/PWMA_L", [P('U_TB1', 1), (59.11, 65.00), (74.35, 65.00), P('U_TB1', 7)], width=1.0, is_raw=True)

try_route("/AIN1_R", [P('U_TB2', 3), (136.19, 71.00), (141.27, 71.00), P('U_TB2', 5)], width=1.0, is_raw=True)
try_route("/AIN2_R", [P('U_TB2', 2), (133.65, 68.00), (143.81, 68.00), P('U_TB2', 6)], width=1.0, is_raw=True)
try_route("/PWMA_R", [P('U_TB2', 1), (131.11, 65.00), (146.35, 65.00), P('U_TB2', 7)], width=1.0, is_raw=True)

print("\n--- 4. Left Motor Control from Pi 4 (1.0mm) ---")
try_route("/AIN1_L", [P('U_PI4', 37), (81.60, 90.00), (69.27, 90.00), P('U_TB1', 5)], width=1.0, d=1.0)
try_route("/AIN2_L", [P('U_PI4', 35), (84.14, 87.50), (71.81, 87.50), P('U_TB1', 6)], width=1.0, d=1.0)
try_route("/PWMA_L", [P('U_PI4', 33), (86.68, 85.00), (74.35, 85.00), P('U_TB1', 7)], width=1.0, d=1.0)

print("\n--- 5. Right Motor Control via Jumpers R_JMP1..3 (1.0mm) ---")
try_route("Net-(U_PI4-GPIO12_PWMB_R)", [
    P('U_PI4', 32), (89.22, 104.00), (130.00, 104.00), P('R_JMP1', 2)
], width=1.0, d=1.0)
try_route("Net-(U_PI4-GPIO16_AIN1_R)", [
    P('U_PI4', 36), (84.14, 105.50), (133.50, 105.50), P('R_JMP2', 2)
], width=1.0, d=1.0)
try_route("Net-(U_PI4-GPIO20_AIN2_R)", [
    P('U_PI4', 38), (81.60, 107.00), (137.00, 107.00), P('R_JMP3', 2)
], width=1.0, d=1.0)

try_route("/PWMA_R", [P('R_JMP1', 1), (130.00, 77.00), (131.11, 75.89), P('U_TB2', 1)], width=1.0, is_raw=True)

print("\n--- 6. Ultrasonic Sensor Dividers (1.0mm) ---")
try_route("Net-(U_US1-ECHO)", [P('U_US1', 3), (93.27, 51.00), (88.19, 51.00), P('R1', 1)], width=1.0, is_raw=True)
try_route("/ECHO_L", [P('R1', 2), (95.81, 62.00), (88.19, 62.00), P('R2', 1)], width=1.0, is_raw=True)
try_route("Net-(U_US2-ECHO)", [P('U_US2', 3), (121.27, 51.00), (116.19, 51.00), P('R3', 1)], width=1.0, is_raw=True)
try_route("/ECHO_R", [P('R3', 2), (123.81, 62.00), (116.19, 62.00), P('R4', 1)], width=1.0, is_raw=True)

print("\n--- 7. TB6612 Module GND Loops (1.4mm) ---")
try_route("/GND", [P('U_TB1', 16), (76.89, 68.00), P('U_TB1', 8)], width=1.4, is_raw=True)
try_route("/GND", [P('U_TB2', 16), (148.89, 68.00), P('U_TB2', 8)], width=1.4, is_raw=True)
try_route("/+5V_PWR", [P('U_PI4', 2), P('U_PI4', 4)], width=1.4, is_raw=True)

print(f"\nTotal accepted tracks: {len(accepted_tracks)} segments.")

# Now write PCB file
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    orig = f.read()

# Extract net list
net_map = {}
for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]+)"\)', orig):
    net_map[m.group(2)] = int(m.group(1))

# Extract clean footprints
fp_blocks = []
for m in re.finditer(r'\(footprint\s+"[^"]+".*?\n\t\)', orig, re.DOTALL):
    fp_str = m.group(0)
    # clean reference font and avoid overlap
    fp_blocks.append(fp_str)

lines = [
    '(kicad_pcb',
    '\t(version 20260206)',
    '\t(generator "pcbnew")',
    '\t(generator_version "10.0")',
    '\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)',
    '\t(paper "A4")',
    '\t(layers\n\t\t(0 "F.Cu" signal)\n\t\t(2 "B.Cu" signal)\n\t\t(9 "F.Adhes" user "F.Adhesive")\n\t\t(11 "B.Adhes" user "B.Adhesive")\n\t\t(13 "F.Paste" user)\n\t\t(15 "B.Paste" user)\n\t\t(5 "F.SilkS" user "F.Silkscreen")\n\t\t(7 "B.SilkS" user "B.Silkscreen")\n\t\t(1 "F.Mask" user)\n\t\t(3 "B.Mask" user)\n\t\t(17 "Dwgs.User" user "User.Drawings")\n\t\t(19 "Cmts.User" user "User.Comments")\n\t\t(21 "Eco1.User" user "User.Eco1")\n\t\t(23 "Eco2.User" user "User.Eco2")\n\t\t(25 "Edge.Cuts" user)\n\t\t(27 "Margin" user)\n\t\t(31 "F.CrtYd" user "F.Courtyard")\n\t\t(29 "B.CrtYd" user "B.Courtyard")\n\t\t(35 "F.Fab" user)\n\t\t(33 "B.Fab" user)\n\t)',
    '\t(setup\n\t\t(pad_to_mask_clearance 0)\n\t\t(solder_mask_min_width 0)\n\t\t(pad_to_paste_clearance 0)\n\t\t(pcbplotparams\n\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)\n\t\t\t(plot_black_and_white yes)\n\t\t\t(outputformat 1)\n\t\t)\n\t)',
    '\t(net 0 "")'
]

for name, nid in sorted(net_map.items(), key=lambda x: x[1]):
    if nid > 0:
        lines.append(f'\t(net {nid} "{name}")')

for fp in fp_blocks:
    lines.append(fp)

for seg in accepted_tracks:
    net_name = seg['net_name']
    nid = net_map.get(net_name, 0)
    p1 = seg['p1']
    p2 = seg['p2']
    w = seg['width']
    u = str(uuid.uuid4())
    lines.append(f'\t(segment (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (width {w:.4f}) (layer "B.Cu") (net {nid}) (tstamp {u}))')

# Closed Edge.Cuts rectangle
lines.append(f'\t(gr_line (start 36.0 35.0) (end 158.0 35.0) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
lines.append(f'\t(gr_line (start 158.0 35.0) (end 158.0 112.0) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
lines.append(f'\t(gr_line (start 158.0 112.0) (end 36.0 112.0) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
lines.append(f'\t(gr_line (start 36.0 112.0) (end 36.0 35.0) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')

# Silk title
lines.append(f'\t(gr_text "ROBOT 4WD RASPBERRY PI 4 - SINGLE LAYER PCB" (at 97.0 37.0) (layer "F.SilkS") (effects (font (size 1.5 1.5) (thickness 0.15))) (tstamp {uuid.uuid4()}))')

lines.append(')')

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print("Wrote updated PCB files.")

import math
import json
import re
import uuid
import subprocess

from test_clean_suite import accepted_tracks, P, k_pads

print(f"Total verified tracks: {len(accepted_tracks)} segments.")

# Read base PCB for footprints and net table
with open('test_pads.kicad_pcb', 'r', encoding='utf-8') as f:
    orig = f.read()

# Extract net list mapping: name -> net_id
net_map = {}
for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]+)"\)', orig):
    net_map[m.group(2)] = int(m.group(1))

# Extract clean footprints from test_pads.kicad_pcb
fp_blocks = []
for m in re.finditer(r'\(footprint\s+"[^"]+".*?\n\t\)', orig, re.DOTALL):
    fp_str = m.group(0)
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
for seg in accepted_tracks:
    net_name = seg['net_name']
    nid = net_map.get(net_name, 0)
    p1 = seg['p1']
    p2 = seg['p2']
    w = seg['width']
    u = str(uuid.uuid4())
    lines.append(f'\t(segment (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (width {w:.4f}) (layer "B.Cu") (net {nid}) (tstamp {u}))')

# Add Clean Edge.Cuts (Closed rectangle: X=36..158, Y=35..112)
min_x, max_x = 36.0, 158.0
min_y, max_y = 35.0, 112.0
lines.append(f'\t(gr_line (start {min_x:.4f} {min_y:.4f}) (end {max_x:.4f} {min_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
lines.append(f'\t(gr_line (start {max_x:.4f} {min_y:.4f}) (end {max_x:.4f} {max_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
lines.append(f'\t(gr_line (start {max_x:.4f} {max_y:.4f}) (end {min_x:.4f} {max_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')
lines.append(f'\t(gr_line (start {min_x:.4f} {max_y:.4f}) (end {min_x:.4f} {min_y:.4f}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (tstamp {uuid.uuid4()}))')

# Clean Title Silkscreen
lines.append(f'\t(gr_text "ROBOT 4WD RASPBERRY PI 4 - SINGLE LAYER PCB" (at 97.0 37.0) (layer "F.SilkS") (effects (font (size 1.5 1.5) (thickness 0.15))) (tstamp {uuid.uuid4()}))')

lines.append(')')

for path in ['Pi4_Robot_Carrier_1Layer.kicad_pcb', 'robot_electronics.kicad_pcb']:
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote {path}.")

print("Generated master PCB files.")

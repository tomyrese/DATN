import json

with open('scripts/parsed_world_pads.json', 'r', encoding='utf-8') as f:
    fps = json.load(f)

print("=== U_PI4 pads ===")
for pnum in ['1', '2', '3', '4', '5', '6', '11', '13', '16', '18', '19', '21', '23', '32', '33', '35', '36', '37', '38', '39', '40']:
    p = fps['U_PI4']['pads'][pnum]
    print(f"Pin {pnum:>2}: ({p['wx']:6.2f}, {p['wy']:6.2f}) net={p['net_name']}")

print("\n=== U_TB1 pads ===")
for pnum in map(str, range(1, 17)):
    p = fps['U_TB1']['pads'][pnum]
    print(f"Pin {pnum:>2}: ({p['wx']:6.2f}, {p['wy']:6.2f}) net={p['net_name']}")

print("\n=== U_TB2 pads ===")
for pnum in map(str, range(1, 17)):
    p = fps['U_TB2']['pads'][pnum]
    print(f"Pin {pnum:>2}: ({p['wx']:6.2f}, {p['wy']:6.2f}) net={p['net_name']}")

print("\n=== Jumpers R_JMP1..6 ===")
for r in ['R_JMP1', 'R_JMP2', 'R_JMP3', 'R_JMP4', 'R_JMP5', 'R_JMP6']:
    p1 = fps[r]['pads']['1']
    p2 = fps[r]['pads']['2']
    print(f"{r}: P1=({p1['wx']:6.2f}, {p1['wy']:6.2f}) [{p1['net_name']}] -> P2=({p2['wx']:6.2f}, {p2['wy']:6.2f}) [{p2['net_name']}]")

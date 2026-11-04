import json
from collections import defaultdict

data = json.load(open('scripts/world_pads_actual.json', 'r', encoding='utf-8'))

net_pads = defaultdict(list)
for fp, fp_data in data.items():
    for pad_num, pad_info in fp_data['pads'].items():
        net = pad_info['net']
        if not net.startswith("unconnected-"):
            net_pads[net].append((fp, pad_num, pad_info['world']))

for net in sorted(net_pads.keys()):
    pads = net_pads[net]
    print(f"Net '{net}' ({len(pads)} pads):")
    for fp, pnum, pos in pads:
        print(f"   {fp:>12}.{pnum:<2} at ({pos[0]:.2f}, {pos[1]:.2f})")


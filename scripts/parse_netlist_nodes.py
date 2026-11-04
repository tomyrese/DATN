import json
import math
import re

# Parse project_netlist.net
with open('project_netlist.net', 'r', encoding='utf-8') as f:
    nl_text = f.read()

# Extract nets
nets = {}
net_blocks = re.findall(r'\(net\s+\(code\s+"\d+"\)\s+\(name\s+"([^"]+)"\)(.*?)(?=\(net\b|\)\s*\)\s*\Z)', nl_text, re.DOTALL)
for name, body in net_blocks:
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body)
    nets[name] = nodes

print(f"Total nets in netlist: {len(nets)}")
for n, nodes in sorted(nets.items()):
    if len(nodes) > 1:
        print(f"  {n:25}: {len(nodes)} nodes -> {', '.join([f'{r}.{p}' for r, p in nodes[:6]])}")


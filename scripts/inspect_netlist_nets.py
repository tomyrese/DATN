from parse_fps_exact import parse_sexpr
from collections import defaultdict

tree = parse_sexpr(open('project_netlist.net', 'r', encoding='utf-8').read())

nets = {}
for item in tree:
    if isinstance(item, list) and item and item[0] == 'nets':
        for net_item in item[1:]:
            if isinstance(net_item, list) and net_item and net_item[0] == 'net':
                net_name = ""
                nodes = []
                for sub in net_item:
                    if isinstance(sub, list) and sub:
                        if sub[0] == 'name':
                            net_name = sub[1].strip('"')
                        elif sub[0] == 'node':
                            ref = None
                            pin = None
                            for prop in sub:
                                if isinstance(prop, list) and len(prop) >= 2:
                                    if prop[0] == 'ref':
                                        ref = prop[1].strip('"')
                                    elif prop[0] == 'pin':
                                        pin = prop[1].strip('"')
                            nodes.append((ref, pin))
                nets[net_name] = nodes

print(f"Total nets in netlist: {len(nets)}")
for n in sorted(nets.keys()):
    print(f"\nNet '{n}' ({len(nets[n])} pins):")
    for r, p in sorted(nets[n], key=lambda x: (x[0], x[1])):
        print(f"   {r:>10}.{p}")


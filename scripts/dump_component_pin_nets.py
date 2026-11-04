from inspect_netlist_nets import nets

# Map from (ref, pin) to net name
pin_to_net = {}
for net_name, nodes in nets.items():
    for ref, pin in nodes:
        pin_to_net[(ref, pin)] = net_name

# List all footprints
all_refs = sorted(list(set(r for r, p in pin_to_net.keys())))
print(f"Total footprints with nets: {len(all_refs)}")
for ref in all_refs:
    pins = [(p, pin_to_net[(ref, p)]) for r, p in pin_to_net.keys() if r == ref]
    print(f"\nFootprint {ref} ({len(pins)} connected pins):")
    for p, n in sorted(pins, key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        print(f"  Pad {p:>2} -> net '{n}'")


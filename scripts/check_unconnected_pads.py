from init_world_pads import world_pads, net_map

unconnected = []
for ref, p_dict in world_pads.items():
    for p_num, p in p_dict.items():
        if not p['net_name']:
            unconnected.append(f"{ref}.{p_num}")

print(f"Unconnected pins: {len(unconnected)}")
print(", ".join(unconnected))

